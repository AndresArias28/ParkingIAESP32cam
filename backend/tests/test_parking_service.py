import copy
import unittest

from backend.app.parking_service import ParkingService


class MemoryRepository:
    def __init__(self):
        self.value = None

    def transaction(self, update):
        self.value = update(copy.deepcopy(self.value))
        return self.value


class ParkingServiceTest(unittest.TestCase):
    def setUp(self):
        self.repo = MemoryRepository()
        self.service = ParkingService(self.repo)
        self.now = 1_000_000
        self.serial = 0

    def observe(self, camera, kind, confidence=0.99, advance=2000):
        self.now += advance
        self.serial += 1
        return self.service.observe(camera, kind, confidence,
                                    f"event{self.serial}", self.now)

    def test_one_car_until_two_empty_frames(self):
        self.assertTrue(self.observe("entrance-01", "car")["counted"])
        for _ in range(5):
            self.assertEqual(self.observe("entrance-01", "car")["reason"], "already_seen")
        self.observe("entrance-01", "empty")
        self.assertFalse(self.observe("entrance-01", "car")["counted"])
        self.observe("entrance-01", "empty")
        self.observe("entrance-01", "empty")
        self.assertTrue(self.observe("entrance-01", "car")["counted"])
        self.assertEqual(self.repo.value["state"]["occupied"]["car"], 2)
        self.assertEqual(len(self.repo.value["events"]), 2)

    def test_low_confidence_and_cooldown(self):
        self.assertEqual(self.observe("entrance-01", "car", 0.5)["reason"], "low_confidence")
        self.assertTrue(self.observe("entrance-01", "car")["counted"])
        self.observe("entrance-01", "empty", advance=100)
        self.observe("entrance-01", "empty", advance=100)
        self.assertEqual(self.observe("entrance-01", "car", advance=100)["reason"], "cooldown")
        self.assertEqual(self.repo.value["state"]["occupied"]["car"], 1)
        self.assertEqual(len(self.repo.value["events"]), 1)

    def test_exit_zero_and_independent_motorcycles(self):
        self.assertEqual(self.observe("exit-01", "car")["reason"], "capacity_limit")
        self.assertTrue(self.observe("entrance-01", "motorcycle")["counted"])
        self.observe("exit-01", "empty")
        self.observe("exit-01", "empty")
        self.assertTrue(self.observe("exit-01", "motorcycle")["counted"])
        self.assertEqual(self.repo.value["state"]["occupied"]["motorcycle"], 0)
        self.assertEqual(self.repo.value["state"]["available"]["motorcycle"], 5)

    def test_capacity_and_persistent_detector(self):
        for index in range(5):
            if index:
                self.observe("entrance-01", "empty")
                self.observe("entrance-01", "empty")
            self.assertTrue(self.observe("entrance-01", "car")["counted"])
        self.observe("entrance-01", "empty")
        self.observe("entrance-01", "empty")
        self.assertEqual(self.observe("entrance-01", "car")["reason"], "capacity_limit")
        restarted = ParkingService(self.repo)
        self.assertEqual(restarted.observe("entrance-01", "car", 0.99,
                        "restart", self.now + 2000)["reason"], "already_seen")
        self.assertEqual(self.repo.value["state"]["occupied"]["car"], 5)
        self.assertEqual(self.repo.value["state"]["available"]["car"], 0)


if __name__ == "__main__":
    unittest.main()
