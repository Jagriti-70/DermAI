# Dataset notes

The optional training script expects the HAM10000 dataset in this local layout:

```text
prototypes/flask-tensorflow-demo/
└── data/
    └── HAM10000/
        ├── HAM10000_metadata.csv
        └── images/
            ├── image_id_1.jpg
            └── ...
```

The script reads the `image_id` and `dx` columns from the metadata CSV.

## Before training or publishing results

- Obtain the dataset from its official distribution source and review its current licence and terms.
- Keep the dataset and patient-related metadata out of this Git repository unless you have a clear legal basis and have checked the dataset terms.
- Record the exact dataset version, preprocessing, class mapping, split strategy, random seeds and training configuration.
- Prevent leakage between train and test data. Where appropriate, split by patient or lesion rather than randomly splitting near-duplicate images.
- Keep an explicit mapping between dataset labels and model output indices. The current demo's API labels do not directly match the seven HAM10000 diagnostic abbreviations; reconcile this before using a trained model.
- Do not claim model accuracy, AUC, sensitivity or other metrics unless they come from a reproducible evaluation on a held-out test set.

Dataset reference: HAM10000, “A large collection of multi-source dermatoscopic images of common pigmented skin lesions.” Check the dataset provider's current page and terms before use.
