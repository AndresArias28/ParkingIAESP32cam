"""Carga y preprocesamiento de modelos de imagen de Teachable Machine."""

import os
from pathlib import Path
import re
import unicodedata

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


MODEL_DIR = Path(__file__).resolve().parents[2] / "ml" / "model"
LABELS = {"carro": "car", "car": "car", "moto": "motorcycle",
          "motorcycle": "motorcycle", "vacio": "empty", "empty": "empty"}


class InvalidImage(ValueError):
    pass


def normalize_label(label):
    # labels.txt suele tener líneas como "0 Carro".
    name = re.sub(r"^\s*\d+\s+", "", label).strip().lower()
    name = "".join(char for char in unicodedata.normalize("NFD", name)
                   if unicodedata.category(char) != "Mn")
    if name not in LABELS:
        raise ValueError(f"Etiqueta desconocida en labels.txt: {label!r}")
    return LABELS[name]


class ImageClassifier:
    def __init__(self, model_dir=MODEL_DIR):
        model_dir = Path(model_dir)
        model_path = model_dir / "keras_model.h5"
        labels_path = model_dir / "labels.txt"
        if not model_path.is_file() or not labels_path.is_file():
            raise FileNotFoundError(
                f"Faltan keras_model.h5 o labels.txt en {model_dir}. "
                "Exporta TensorFlow → Keras → Descargar y copia ambos archivos allí.")

        labels = [normalize_label(line) for line in
                  labels_path.read_text(encoding="utf-8-sig").splitlines()
                  if line.strip()]
        if len(labels) != 3 or set(labels) != {"car", "motorcycle", "empty"}:
            raise ValueError("labels.txt debe tener exactamente Carro, Moto y Vacío, una vez cada una.")

        # Teachable Machine exporta modelos H5 creados con Keras 2.
        os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
        from tensorflow import keras

        self.model = keras.models.load_model(str(model_path), compile=False)
        self.labels = labels
        shape = self.model.input_shape
        if isinstance(shape, list) or len(shape) != 4 or shape[-1] != 3:
            raise ValueError(f"Forma de entrada no compatible: {shape}")
        self.height, self.width = shape[1], shape[2]
        if not isinstance(self.height, int) or not isinstance(self.width, int):
            raise ValueError(f"Dimensiones de imagen no definidas: {shape}")
        output_shape = self.model.output_shape
        if isinstance(output_shape, list) or output_shape[-1] != len(labels):
            raise ValueError("Número de salidas del modelo distinto a labels.txt.")

    def predict(self, image_bytes):
        from io import BytesIO

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image.load()
                image = ImageOps.fit(image.convert("RGB"),
                                     (self.width, self.height), Image.Resampling.LANCZOS)
                array = np.asarray(image, dtype=np.float32)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImage("La imagen no se puede abrir o está dañada.") from exc

        batch = np.expand_dims((array / 127.5) - 1.0, axis=0)
        scores = np.asarray(self.model.predict(batch, verbose=0))[0]
        if len(scores) != len(self.labels) or not np.all(np.isfinite(scores)):
            raise RuntimeError("El modelo devolvió probabilidades inválidas.")
        index = int(np.argmax(scores))
        return {"prediction": self.labels[index],
                "confidence": round(float(scores[index]), 4)}
