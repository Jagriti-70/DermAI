"""
Skin Disease Detection - Flask Backend
=======================================
Serves a REST API for image upload + prediction, and also serves the
frontend HTML so the whole thing runs as ONE process from a single
double-click launcher.

Endpoints:
  GET  /                -> Frontend UI (index.html)
  POST /api/predict     -> Upload image, returns predicted class + confidence
  GET  /api/health      -> Health check
  GET  /api/classes     -> List of disease classes the model can detect
  GET  /uploads/<file>  -> Serve uploaded images back to the UI
"""

import os
import io
import uuid
import base64
import datetime
import json
import traceback

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from PIL import Image
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR   = os.path.join(BASE_DIR, "uploads")
MODEL_DIR    = os.path.join(BASE_DIR, "model")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
HISTORY_FILE = os.path.join(BASE_DIR, "prediction_history.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR,  exist_ok=True)

# Disease classes (matches HAM10000 + a couple common conditions)
CLASS_NAMES = [
    "Melanocytic nevi (Mole)",
    "Melanoma",
    "Benign keratosis-like lesions",
    "Basal cell carcinoma",
    "Actinic keratoses",
    "Vascular lesions",
    "Dermatofibroma",
    "Eczema",
    "Psoriasis",
    "Fungal infection",
]

CLASS_INFO = {
    "Melanocytic nevi (Mole)":     {"severity": "Low",      "advice": "Usually benign. Monitor for changes in size/color."},
    "Melanoma":                    {"severity": "High",     "advice": "Potentially serious. Consult a dermatologist immediately."},
    "Benign keratosis-like lesions":{"severity": "Low",     "advice": "Generally harmless. Routine monitoring recommended."},
    "Basal cell carcinoma":        {"severity": "Moderate", "advice": "Most common skin cancer. Treatable — see a doctor."},
    "Actinic keratoses":           {"severity": "Moderate", "advice": "Pre-cancerous. Schedule a dermatology visit."},
    "Vascular lesions":            {"severity": "Low",      "advice": "Usually benign vascular issue. Routine checkup."},
    "Dermatofibroma":              {"severity": "Low",      "advice": "Benign skin nodule. No urgent action needed."},
    "Eczema":                      {"severity": "Low",      "advice": "Chronic inflammation. Moisturize; topical creams help."},
    "Psoriasis":                   {"severity": "Moderate", "advice": "Autoimmune condition. Dermatologist can prescribe treatment."},
    "Fungal infection":            {"severity": "Low",      "advice": "Topical antifungal creams usually effective."},
}

IMG_SIZE = 224

# ---------------------------------------------------------------------------
# Model loading (with graceful fallback so the app ALWAYS runs)
# ---------------------------------------------------------------------------
MODEL          = None
MODEL_BACKEND  = "heuristic"   # "tensorflow" | "heuristic"

def load_model_safely():
    """Try to load a trained Keras model; otherwise fall back to a
    deterministic heuristic so the UI still works end-to-end."""
    global MODEL, MODEL_BACKEND
    model_path = os.path.join(MODEL_DIR, "skin_model.h5")

    if os.path.exists(model_path):
        try:
            import tensorflow as tf  # imported lazily
            MODEL = tf.keras.models.load_model(model_path)
            MODEL_BACKEND = "tensorflow"
            print(f"[OK] Loaded trained model from {model_path}")
            return
        except Exception as e:
            print(f"[WARN] Could not load TF model: {e}")
            print("[WARN] Falling back to heuristic mode.")

    print("[INFO] Running in HEURISTIC mode (no trained .h5 model found).")
    print("[INFO] Place a trained 'skin_model.h5' in the model/ folder to upgrade.")
    MODEL_BACKEND = "heuristic"


def preprocess_image(pil_img):
    pil_img = pil_img.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(pil_img).astype("float32") / 255.0
    return arr


def predict_heuristic(arr):
    """Deterministic 'demo' classifier based on image color statistics.
    Returns (class_index, confidence, prob_vector). Same image always
    yields the same answer, which is exactly what you want for a demo."""
    r, g, b = arr[..., 0].mean(), arr[..., 1].mean(), arr[..., 2].mean()
    std     = arr.std()
    # Use a seed derived from pixel stats so result is reproducible per image
    seed = int(abs(r * 1000 + g * 100 + b * 10 + std * 1000)) % (2**31)
    rng  = np.random.default_rng(seed)
    logits = rng.normal(0, 1, size=len(CLASS_NAMES))
    # Bias toward more common classes
    logits[0] += 0.8   # nevi (most common)
    logits[2] += 0.4
    probs = np.exp(logits) / np.exp(logits).sum()
    idx   = int(np.argmax(probs))
    return idx, float(probs[idx]), probs.tolist()


def predict_tensorflow(arr):
    import tensorflow as tf  # noqa
    batch = np.expand_dims(arr, axis=0)
    probs = MODEL.predict(batch, verbose=0)[0]
    idx   = int(np.argmax(probs))
    return idx, float(probs[idx]), probs.tolist()


def predict(arr):
    if MODEL_BACKEND == "tensorflow" and MODEL is not None:
        return predict_tensorflow(arr)
    return predict_heuristic(arr)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=FRONTEND_DIR,
    static_folder=FRONTEND_DIR,
    static_url_path="/static",
)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/api/health")
def health():
    return jsonify({
        "status":  "ok",
        "backend": MODEL_BACKEND,
        "classes": len(CLASS_NAMES),
        "time":    datetime.datetime.now().isoformat(timespec="seconds"),
    })


@app.route("/api/classes")
def classes():
    return jsonify({
        "classes": [
            {"name": c, **CLASS_INFO[c]} for c in CLASS_NAMES
        ]
    })


@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided (field name: 'image')."}), 400

        file = request.files["image"]
        if not file.filename:
            return jsonify({"error": "Empty filename."}), 400

        # Save upload
        ext        = os.path.splitext(file.filename)[1].lower() or ".png"
        if ext not in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
            return jsonify({"error": f"Unsupported file type: {ext}"}), 400
        unique     = f"{uuid.uuid4().hex}{ext}"
        save_path  = os.path.join(UPLOAD_DIR, unique)
        file.save(save_path)

        # Load + predict
        pil_img    = Image.open(save_path)
        arr        = preprocess_image(pil_img)
        idx, conf, probs = predict(arr)
        cls_name   = CLASS_NAMES[idx]
        info       = CLASS_INFO[cls_name]

        # Build response
        top3_idx   = np.argsort(probs)[::-1][:3]
        top3       = [
            {"name": CLASS_NAMES[i], "confidence": round(probs[i] * 100, 2)}
            for i in top3_idx
        ]

        result = {
            "prediction":   cls_name,
            "confidence":   round(conf * 100, 2),
            "severity":     info["severity"],
            "advice":       info["advice"],
            "top3":         top3,
            "image_url":    f"/uploads/{unique}",
            "backend":      MODEL_BACKEND,
            "timestamp":    datetime.datetime.now().isoformat(timespec="seconds"),
        }

        # Save to history
        save_history(result)
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/history")
def history_endpoint():
    if not os.path.exists(HISTORY_FILE):
        return jsonify({"history": []})
    try:
        with open(HISTORY_FILE) as f:
            return jsonify({"history": json.load(f)[-20:][::-1]})
    except Exception:
        return jsonify({"history": []})


def save_history(record):
    data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                data = json.load(f)
        except Exception:
            data = []
    data.append(record)
    with open(HISTORY_FILE, "w") as f:
        json.dump(data[-100:], f, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  Skin Disease Detection — Flask Server")
    print("=" * 60)
    load_model_safely()
    print("  Open your browser at: http://127.0.0.1:5000")
    print("=" * 60)
    # Disable reloader so the auto-launched browser doesn't re-open
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
