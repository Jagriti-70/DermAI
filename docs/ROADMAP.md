# Development roadmap

## Phase 1 — Make the current prototypes reproducible

- [ ] Choose one primary application and clearly mark the other as an experimental prototype.
- [ ] Add dependency pinning and documented Python versions.
- [ ] Add upload validation and automated tests for invalid files and oversized images.
- [ ] Fix the model class-index mismatch between the training script and Flask API.
- [ ] Replace the heuristic fallback with an explicit “model not installed” state so demo output cannot be mistaken for a prediction.
- [ ] Add a privacy notice and upload deletion controls.

## Phase 2 — Build a defensible ML pipeline

- [ ] Decide and document the intended architecture (for example, TensorFlow ResNet50 or PyTorch EfficientNet).
- [ ] Create deterministic train/validation/test splits and document leakage prevention.
- [ ] Handle class imbalance using documented methods.
- [ ] Save model weights, class mapping, preprocessing configuration and training metadata as versioned artifacts.
- [ ] Evaluate on a held-out test set and report per-class precision, recall, F1, sensitivity, specificity, ROC-AUC and a confusion matrix where appropriate.
- [ ] Calibrate confidence scores and assess performance across relevant subgroups.
- [ ] Implement and validate Grad-CAM only if explainability is part of the project scope.

## Phase 3 — Production-quality application

- [ ] Add a secure server-side inference API.
- [ ] Add a database only if persistence requirements justify it; document schema and migrations.
- [ ] Add authentication, audit logging, monitoring and data-retention controls.
- [ ] Conduct clinical, privacy, security and regulatory review before any real-world use.
