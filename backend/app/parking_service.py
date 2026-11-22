"""Reglas de conteo aplicadas en una transacción de Firebase RTDB."""

from copy import deepcopy


DEFAULT_CAPACITY = {"car": 5, "motorcycle": 5}
CAMERA_ACTION = {"entrance-01": "in", "exit-01": "out"}
VEHICLES = {"car", "motorcycle"}


class ParkingService:
    def __init__(self, repository):
        self.repository = repository

    def observe(self, camera, prediction, confidence, event_id, timestamp_ms):
        if camera not in CAMERA_ACTION:
            raise ValueError("Cámara desconocida")
        if prediction not in VEHICLES | {"empty"}:
            raise ValueError("Predicción desconocida")
        if not 0 <= confidence <= 1:
            raise ValueError("Confianza inválida")

        outcome = {"counted": False, "reason": "not_counted"}

        def update(current):
            nonlocal outcome
            data = deepcopy(current) if isinstance(current, dict) else {}
            config = data.setdefault("config", {})
            capacity = config.setdefault("capacity", deepcopy(DEFAULT_CAPACITY))
            threshold = float(config.setdefault("confidenceThreshold", 0.85))
            cooldown_ms = int(config.setdefault("cooldownMs", 2500))
            state = data.setdefault("state", {})
            occupied = state.setdefault("occupied", {"car": 0, "motorcycle": 0})
            state.setdefault("available", {})
            for kind in VEHICLES:
                cap = int(capacity[kind])
                occupied[kind] = max(0, min(cap, int(occupied.get(kind, 0))))
                state["available"][kind] = cap - occupied[kind]

            cameras = data.setdefault("cameras", {})
            camera_data = cameras.setdefault(camera, {})
            camera_data["type"] = "entrance" if camera == "entrance-01" else "exit"
            camera_data["online"] = True
            detector = camera_data.setdefault("detector", {})
            detector.setdefault("armed", True)
            detector.setdefault("emptyStreak", 0)
            camera_data["lastSeenMs"] = timestamp_ms
            events = data.setdefault("events", {})

            reason = "low_confidence"
            counted = False
            if confidence >= threshold:
                if prediction == "empty":
                    detector["emptyStreak"] += 1
                    if detector["emptyStreak"] >= 2:
                        detector["armed"] = True
                    reason = "empty"
                else:
                    detector["emptyStreak"] = 0
                    if not detector["armed"]:
                        reason = "already_seen"
                    else:
                        detector["armed"] = False
                        last = int(detector.get("lastEventMs", 0))
                        if timestamp_ms - last < cooldown_ms:
                            reason = "cooldown"
                        else:
                            action = CAMERA_ACTION[camera]
                            delta = 1 if action == "in" else -1
                            new_value = occupied[prediction] + delta
                            if not 0 <= new_value <= int(capacity[prediction]):
                                reason = "capacity_limit"
                            else:
                                occupied[prediction] = new_value
                                state["available"][prediction] = int(capacity[prediction]) - new_value
                                detector["lastEventMs"] = timestamp_ms
                                events[event_id] = {
                                    "camera": camera, "type": prediction, "action": action,
                                    "confidence": round(confidence, 4),
                                    "timestamp": timestamp_ms,
                                }
                                counted = True
                                reason = "accepted"
            # El callback puede repetirse por conflictos; solo conservar el último resultado.
            outcome = {"counted": counted, "reason": reason,
                       "occupied": dict(occupied),
                       "available": dict(state["available"])}
            return data

        self.repository.transaction(update)
        return outcome
