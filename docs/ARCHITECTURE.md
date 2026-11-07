# Architecture

## Prototype A: Gemini web app

```text
Browser
  ├── HTML/CSS interface
  ├── JavaScript image selection and preview
  ├── Gemini API key held in sessionStorage
  └── HTTPS request with image + prompt
          └── Google Gemini 2.5 Flash Vision API
                  └── Generated text response displayed in UI
```

This path does not run a locally trained CNN. The prompt requests a structured skin-image assessment from a general vision model.

## Prototype B: Flask + TensorFlow demo

```text
Browser (React 18 via CDN)
        |
        | POST /api/predict (multipart image)
        v
Flask API
        |
        ├── Pillow: decode, resize to 224 × 224, RGB conversion
        ├── NumPy: normalize pixel values
        |
        ├── TensorFlow mode, if model/skin_model.h5 loads
        |       └── Keras model prediction
        |
        └── Heuristic mode otherwise
                └── deterministic pseudo-probabilities from image statistics
        |
        v
JSON response + local prediction_history.json
```

The TensorFlow model's output class order must match the API's `CLASS_NAMES` order. The current training script builds class labels from sorted metadata values, while the Flask app uses a separately hard-coded class list. Verify and reconcile this mapping before using any trained model; otherwise predictions can be assigned incorrect labels.
