"""Compatibilidad entre el estado existente y el esquema del backend."""

from copy import deepcopy
import unittest

from backend.app.firebase_repository import FirebaseRepository
from backend.app.parking_service import ParkingService


class MemoryRootReference:
    def __init__(self, value):
        self.value = value

    def transaction(self, update):
        self.value = update(deepcopy(self.value))
        return self.value


class FirebaseRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.reference = MemoryRootReference({
            "config": {
                "cuposMaxCarro": 100,
                "cuposMaxMoto": 200,
                "umbral": 0.85,
                "cooldownMs": 2000,
            },
            "estado": {
                "ocupadosCarro": 10,
                "dispCarro": 90,
                "ocupadosMoto": 0,
                "dispMoto": 200,
                "updatedAt": 0,
                "campoExtra": "conservar",
            },
            "otroNodo": {"valor": 1},
        })
        self.service = ParkingService(FirebaseRepository(self.reference))

    def test_legacy_and_new_state_update_together(self):
        result = self.service.observe("entrance-01", "car", 0.96, "event1", 10000)
        self.assertTrue(result["counted"])
        root = self.reference.value
        self.assertEqual(root["estado"]["ocupadosCarro"], 11)
        self.assertEqual(root["estado"]["dispCarro"], 89)
        self.assertEqual(root["estado"]["ocupadosMoto"], 0)
        self.assertEqual(root["estado"]["dispMoto"], 200)
        self.assertEqual(root["estado"]["updatedAt"], 10000)
        self.assertEqual(root["estado"]["campoExtra"], "conservar")
        self.assertEqual(root["otroNodo"], {"valor": 1})
        self.assertEqual(root["parking"]["config"]["capacity"],
                         {"car": 100, "motorcycle": 200})
        self.assertEqual(root["parking"]["config"]["cooldownMs"], 2000)
        self.assertEqual(root["parking"]["state"]["occupied"]["car"], 11)
        self.assertEqual(root["parking"]["state"]["available"]["car"], 89)

    def test_duplicate_does_not_increment_either_state(self):
        self.service.observe("entrance-01", "car", 0.96, "event1", 10000)
        result = self.service.observe("entrance-01", "car", 0.96, "event2", 12000)
        self.assertEqual(result["reason"], "already_seen")
        self.assertEqual(self.reference.value["estado"]["ocupadosCarro"], 11)
        self.assertEqual(self.reference.value["parking"]["state"]["occupied"]["car"], 11)
        self.assertEqual(len(self.reference.value["parking"]["events"]), 1)

    def test_external_legacy_change_is_respected(self):
        self.service.observe("entrance-01", "empty", 0.96, "event1", 10000)
        self.reference.value["estado"]["ocupadosCarro"] = 25
        self.reference.value["estado"]["dispCarro"] = 75
        result = self.service.observe("entrance-01", "car", 0.96, "event2", 12000)
        self.assertTrue(result["counted"])
        self.assertEqual(self.reference.value["estado"]["ocupadosCarro"], 26)
        self.assertEqual(self.reference.value["parking"]["state"]["occupied"]["car"], 26)


if __name__ == "__main__":
    unittest.main()
