import unittest

from sensor.simulator import read_ec_sensor


class SensorSimulatorTests(unittest.TestCase):
    def test_sensor_reading_has_expected_shape(self):
        reading = read_ec_sensor("batch-1")
        self.assertEqual(reading["batch_id"], "batch-1")
        self.assertIn("ec_value", reading)
        self.assertIn("tampered", reading)
        self.assertIn("status", reading)
        self.assertTrue(0.1 <= reading["ec_value"] <= 2.5)


if __name__ == "__main__":
    unittest.main()
