"""API HTTP de clasificación. Ejecutar con: py -m backend.app.server"""

import os
import time
import hmac
from uuid import uuid4

from flask import Flask, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge

from .classifier import ImageClassifier, InvalidImage
from .local_config import load_local_env
from .parking_service import ParkingService


CAMERAS = {"entrance-01", "exit-01"}


def create_app(classifier=None, parking_service=None, camera_token=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    classifier = classifier if classifier is not None else ImageClassifier()
    if parking_service is not None:
        camera_token = camera_token or os.environ.get("PARKING_CAMERA_TOKEN")
        if not camera_token:
            raise ValueError("Falta PARKING_CAMERA_TOKEN para activar el conteo")

    @app.get("/health")
    def health():
        return jsonify(status="ok", model="loaded")

    @app.post("/api/v1/predict")
    def predict():
        camera = request.args.get("camera")
        if camera is not None and camera not in CAMERAS:
            return jsonify(error="Cámara desconocida."), 400
        if parking_service is not None and camera is not None:
            supplied = request.headers.get("X-Camera-Token", "")
            if not hmac.compare_digest(supplied, camera_token):
                return jsonify(error="Cámara no autorizada."), 401

        if "image" in request.files:
            image_bytes = request.files["image"].read()
        elif request.mimetype == "image/jpeg":
            image_bytes = request.get_data()
        else:
            return jsonify(error="Envía un JPEG como campo 'image' o cuerpo image/jpeg."), 400
        if not image_bytes:
            return jsonify(error="La imagen está vacía."), 400

        try:
            result = classifier.predict(image_bytes)
        except InvalidImage as exc:
            return jsonify(error=str(exc)), 400
        if camera is not None:
            result["camera"] = camera
        if parking_service is not None and camera is not None:
            result.update(parking_service.observe(
                camera, result["prediction"], result["confidence"],
                uuid4().hex, int(time.time() * 1000)))
            app.logger.info("Conteo %s: %s (%s)", camera,
                            "sí" if result["counted"] else "no", result["reason"])
        app.logger.info("Predicción %s: %s (%.4f)", camera or "sin cámara",
                        result["prediction"], result["confidence"])
        return jsonify(result)

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(_error):
        return jsonify(error="La imagen supera el límite de 5 MB."), 413

    return app


def main():
    load_local_env()
    try:
        parking_service = None
        if os.environ.get("PARKING_FIREBASE_ENABLED") == "1":
            from .firebase_repository import FirebaseRepository
            parking_service = ParkingService(FirebaseRepository())
        app = create_app(parking_service=parking_service)
    except (FileNotFoundError, ValueError, OSError) as exc:
        raise SystemExit(f"No se pudo iniciar el servidor: {exc}") from exc
    port = int(os.environ.get("PARKING_PORT", "5000"))
    host = os.environ.get("PARKING_HOST", "127.0.0.1")
    app.logger.setLevel("INFO")
    print(f"Servidor listo en {host}:{port}", flush=True)
    print(f"Conteo Firebase: {'activado' if parking_service is not None else 'desactivado'}",
          flush=True)
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()

