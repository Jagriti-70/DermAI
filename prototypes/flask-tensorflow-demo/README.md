[README (2).md](https://github.com/user-attachments/files/34525426/README.2.md)
# Flask + TensorFlow demo

A Flask API and React 18 (CDN) browser interface for an image-upload workflow.

## Run
```bash
python -m venv .venv
# Activate the environment, then:
pip install -r requirements.txt
python backend/app.py
```
Open `http://127.0.0.1:5000`.

By default, this app uses a deterministic heuristic because no trained model weights are included. If a compatible `model/skin_model.h5` exists, the app attempts to load it. The optional `train_model.py` builds a TensorFlow/Keras ResNet50 model; it does not implement PyTorch EfficientNetB4.

See the root README and `../../docs/` for limitations, API details and dataset notes.
