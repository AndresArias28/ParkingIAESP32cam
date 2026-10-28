"""Pruebas del contrato HTTP sin necesitar un modelo exportado."""

import io
import unittest

from backend.app.classifier import InvalidImage, normalize_label
from backend.app.server import create_app


class FakeClassifier:
    def predict(self, image_bytes):
        if image_bytes == b"bad":
            raise InvalidImage("Imagen inválida")
        return {"prediction": "car", "confidence": 0.9}


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app(FakeClassifier()).test_client()

    def test_labels_from_teachable_machine(self):
        self.assertEqual(normalize_label("0 Carro"), "car")
        self.assertEqual(normalize_label("2 Vacío"), "empty")
        with self.assertRaises(ValueError):
            normalize_label("1 Persona")

    def test_multipart_image_and_camera(self):
        response = self.client.post("/api/v1/predict?camera=entrance-01",
                                    data={"image": (io.BytesIO(b"jpeg"), "foto.jpg")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json,
                         {"prediction": "car", "confidence": 0.9,
                          "camera": "entrance-01"})

    def test_raw_jpeg(self):
        response = self.client.post("/api/v1/predict", data=b"jpeg",
                                    content_type="image/jpeg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["prediction"], "car")

    def test_invalid_requests(self):
        self.assertEqual(self.client.post("/api/v1/predict?camera=unknown",
                         data=b"jpeg", content_type="image/jpeg").status_code, 400)
        self.assertEqual(self.client.post("/api/v1/predict", json={}).status_code, 400)
        self.assertEqual(self.client.post("/api/v1/predict", data=b"bad",
                         content_type="image/jpeg").status_code, 400)
        self.assertEqual(self.client.post("/api/v1/predict", data=b"",
                         content_type="image/jpeg").status_code, 400)

    def test_size_limit(self):
        response = self.client.post("/api/v1/predict", data=b"x" * (5 * 1024 * 1024 + 1),
                                    content_type="image/jpeg")
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
