"""
Optional: Train a real CNN on HAM10000 to replace the heuristic backend.
========================================================================
Run this ONLY if you want to train a real model. The app works without it.

Steps:
  1. Download HAM10000 from https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
  2. Extract images into:  data/HAM10000/images/
     and CSV into:         data/HAM10000/HAM10000_metadata.csv
  3. pip install tensorflow scikit-learn
  4. python train_model.py
  5. The trained 'skin_model.h5' is saved into model/ and auto-loaded next run.
"""

import os
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

IMG_SIZE   = 224
BATCH_SIZE = 32
EPOCHS     = 15
DATA_DIR   = "data/HAM10000"
MODEL_OUT  = "model/skin_model.h5"

def main():
    csv_path = os.path.join(DATA_DIR, "HAM10000_metadata.csv")
    img_dir  = os.path.join(DATA_DIR, "images")
    df = pd.read_csv(csv_path)

    classes  = sorted(df["dx"].unique())
    cls2idx  = {c: i for i, c in enumerate(classes)}
    print("Classes:", classes)

    X, y = [], []
    for _, row in df.iterrows():
        p = os.path.join(img_dir, row["image_id"] + ".jpg")
        if not os.path.exists(p):
            continue
        img = Image.open(p).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
        X.append(np.array(img) / 255.0)
        y.append(cls2idx[row["dx"]])
    X = np.array(X, dtype="float32")
    y = tf.keras.utils.to_categorical(y, num_classes=len(classes))

    Xt, Xv, yt, yv = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    base = ResNet50(weights="imagenet", include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base.trainable = False
    x   = GlobalAveragePooling2D()(base.output)
    x   = Dense(256, activation="relu")(x)
    x   = Dropout(0.4)(x)
    out = Dense(len(classes), activation="softmax")(x)
    model = Model(base.input, out)
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    model.fit(Xt, yt, validation_data=(Xv, yv), epochs=EPOCHS, batch_size=BATCH_SIZE)
    os.makedirs("model", exist_ok=True)
    model.save(MODEL_OUT)
    print(f"Saved trained model to {MODEL_OUT}")

if __name__ == "__main__":
    main()
