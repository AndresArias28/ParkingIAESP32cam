"""Adaptador Firebase: mantiene parking y el esquema legado en una transacción."""

from copy import deepcopy
import os


class FirebaseRepository:
    def __init__(self, reference=None):
        if reference is not None:
            self.reference = reference
            return
        database_url = os.environ.get("FIREBASE_DATABASE_URL")
        if not database_url:
            raise ValueError("Falta FIREBASE_DATABASE_URL")
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            raise ValueError("Falta GOOGLE_APPLICATION_CREDENTIALS")
        import firebase_admin
        from firebase_admin import credentials, db

        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(
                credentials.ApplicationDefault(), {"databaseURL": database_url})
        self.reference = db.reference("/")

    def transaction(self, update):
        def update_root(current):
            root = deepcopy(current) if isinstance(current, dict) else {}
            parking = root.get("parking")
            parking = parking if isinstance(parking, dict) else {}

            legacy_config = root.get("config")
            if isinstance(legacy_config, dict):
                config = parking.setdefault("config", {})
                capacity = config.setdefault("capacity", {})
                for legacy_key, kind in (
                    ("cuposMaxCarro", "car"), ("cuposMaxMoto", "motorcycle")
                ):
                    if legacy_key in legacy_config:
                        capacity[kind] = legacy_config[legacy_key]
                if "umbral" in legacy_config:
                    config["confidenceThreshold"] = legacy_config["umbral"]
                if "cooldownMs" in legacy_config:
                    config["cooldownMs"] = legacy_config["cooldownMs"]

            legacy_state = root.get("estado")
            if isinstance(legacy_state, dict):
                state = parking.setdefault("state", {})
                occupied = state.setdefault("occupied", {})
                for legacy_key, kind in (
                    ("ocupadosCarro", "car"), ("ocupadosMoto", "motorcycle")
                ):
                    if legacy_key in legacy_state:
                        occupied[kind] = legacy_state[legacy_key]

            parking = update(parking)
            root["parking"] = parking
            state = parking["state"]
            occupied = state["occupied"]
            available = state["available"]
            legacy_state = root.get("estado")
            if not isinstance(legacy_state, dict):
                legacy_state = {}
                root["estado"] = legacy_state
            legacy_state.update({
                "ocupadosCarro": occupied["car"],
                "ocupadosMoto": occupied["motorcycle"],
                "dispCarro": available["car"],
                "dispMoto": available["motorcycle"],
            })
            seen = [camera.get("lastSeenMs", 0)
                    for camera in parking.get("cameras", {}).values()
                    if isinstance(camera, dict)]
            if seen:
                legacy_state["updatedAt"] = max(seen)
            return root

        return self.reference.transaction(update_root)
