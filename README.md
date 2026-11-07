# DermAI — Skin Image Analysis Prototypes

DermAI is a collection of educational prototypes exploring image-based skin-condition analysis. This repository contains **two separate implementations** preserved from the supplied project files:

1. **Gemini web prototype** — a static HTML/CSS/JavaScript interface that sends an uploaded image to the Google Gemini 2.5 Flash Vision API.
2. **Flask + TensorFlow demo** — a Flask API with a React 18 interface loaded from CDNs. It can load a compatible Keras `.h5` model if one is supplied; otherwise it runs a deterministic image-statistics heuristic.

> **Important model-status note:** The supplied source code does not contain a trained EfficientNetB4/PyTorch model, Grad-CAM implementation, PostgreSQL integration, or verifiable evaluation results. The optional training script uses TensorFlow/Keras ResNet50. The Flask app's default mode is a heuristic demo, not a clinically meaningful classifier. Do not describe either prototype as a validated medical diagnostic system.

## Repository contents

```text
DermAI-GitHub/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATASETS.md
│   ├── MODEL_CARD.md
│   ├── SECURITY.md
│   └── ROADMAP.md
├── tests/
│   ├── README.md
│   └── test_flask_api.py
└── prototypes/
    ├── gemini-web/
    │   ├── index.html
    │   ├── README.md
    │   └── src/
    │       ├── app.js
    │       └── style.css
    └── flask-tensorflow-demo/
        ├── README.md
        ├── requirements.txt
        ├── train_model.py
        ├── backend/
        │   └── app.py
        └── frontend/
            └── index.html
```

## 1. Run the Gemini web prototype

1. Open `prototypes/gemini-web/README.md`.
2. Create a Gemini API key in Google AI Studio.
3. Open `prototypes/gemini-web/index.html` in a modern browser.
4. Enter your key in the app and upload an image.

The browser calls Gemini directly. This is convenient for a local demonstration, but **not appropriate for a public production deployment** because the key is handled by client-side code. See [Security](docs/SECURITY.md).

## 2. Run the Flask demo

Python 3.10 or newer is recommended.

```bash
cd prototypes/flask-tensorflow-demo
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
python backend/app.py
```

Open `http://127.0.0.1:5000`.

The app reports its active backend at `/api/health`:
- `heuristic`: no compatible model file was found; output is a deterministic demo result based on image statistics.
- `tensorflow`: a compatible `model/skin_model.h5` file was loaded.

The provided `train_model.py` is an optional TensorFlow/Keras ResNet50 training example. It requires the HAM10000 dataset arranged as described in [Datasets](docs/DATASETS.md). Training has not been performed or independently verified as part of this repository package.

## 3. API quick reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serve the frontend |
| GET | `/api/health` | Report status, backend mode and class count |
| GET | `/api/classes` | Return configured class labels and informational text |
| POST | `/api/predict` | Accept an image as multipart form field `image` |
| GET | `/api/history` | Return recent locally stored prediction records |

See [API documentation](docs/API.md) for request and response examples.

## 4. Tests

Install `pytest` in the same virtual environment and run:

```bash
pip install pytest
pytest -q
```

The included tests check basic Flask API availability and response structure. They do **not** validate medical accuracy or model performance.

## Current limitations

- The two prototypes are independent; they are not integrated into one application.
- The Flask demo stores prediction history in a local JSON file, not PostgreSQL.
- The optional training script is TensorFlow/Keras ResNet50, not PyTorch EfficientNetB4.
- Grad-CAM is not implemented in the supplied source.
- No model weights or verified benchmark report are included.
- Gemini-generated responses are not equivalent to a trained, validated classifier.

## Responsible use

This software is for learning and experimentation only. It is not a medical device and must not be used to diagnose, rule out, triage, or treat a skin condition. Do not delay professional care based on its output. Skin images are sensitive personal data; use only images you have permission to process and avoid uploading identifiable or private images to third-party services.

## Suggested next steps

See [Roadmap](docs/ROADMAP.md) for concrete steps to turn this collection of prototypes into a reproducible machine-learning project.
