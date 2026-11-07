# Model card — current repository state

## Summary

This repository currently contains two different inference approaches:

1. A browser application that sends images to Google's Gemini 2.5 Flash Vision API.
2. A Flask application that attempts to load a local TensorFlow/Keras model named `skin_model.h5`; if it cannot, it returns heuristic demo outputs.

## Intended use

Educational software prototyping and learning about image-upload interfaces, API integration and model-serving patterns.

## Out-of-scope use

Clinical diagnosis, screening, triage, treatment recommendations, risk assessment, or decisions about whether to seek medical care.

## Model details

| Item | Current evidence in repository |
|---|---|
| PyTorch EfficientNetB4 | Not present in supplied source |
| TensorFlow/Keras ResNet50 | Optional training script is present |
| Trained weights | Not included |
| Grad-CAM | Not implemented in supplied source |
| PostgreSQL | Not implemented; Flask history uses JSON |
| Verified test metrics | Not included |
| Default Flask inference | Heuristic demo |

## Limitations and risks

- Dermatoscopic image datasets do not represent every camera, skin tone, age group, body site or clinical setting.
- A general-purpose vision-language model can produce plausible but incorrect descriptions.
- A heuristic based on pixel statistics is not a medical classifier.
- A confidence-like number is not necessarily calibrated probability.
- The code's class labels and the optional training script's sorted class mapping need reconciliation.

## Evaluation status

No reproducible held-out evaluation report is included. Do not add performance claims until evaluation code, split definitions, class-wise metrics, confusion matrix and test results are available and can be reproduced.

## Human oversight

Any real concern about a skin lesion should be assessed by a qualified healthcare professional. The application must never be used to reassure a user that a lesion is harmless.
