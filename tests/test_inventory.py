import json
import os
import unittest
from unittest.mock import MagicMock, patch

from netcodeasync.models import NetDevice
from netcodeasync.modules.inventory import Inventory


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.inventory = Inventory()
        self.test_file = "test_inventory.json"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_device(self):
        self.inventory.add_device(
            platform="mikrotik_ros",
            host="192.168.88.1",
            user="admin",
            password="password",
        )
        self.assertEqual(len(self.inventory), 1)
        device = self.inventory.get_device_by_host("192.168.88.1")
        self.assertEqual(device["host"], "192.168.88.1")

    def test_load_from_json_list(self):
        data = [
            {
                "platform": "mikrotik_ros",
                "host": "10.0.0.1",
                "user": "admin",
                "password": "password",
            }
        ]
        with open(self.test_file, "w") as f:
            json.dump(data, f)

        self.inventory.load_from_json(self.test_file)
        self.assertEqual(len(self.inventory), 1)
        device = self.inventory.get_device_by_host("10.0.0.1")
        self.assertEqual(device["host"], "10.0.0.1")

    def test_load_from_json_dict(self):
        data = {
            "devices": [
                {
                    "platform": "arista_eos",
                    "host": "10.0.0.2",
                    "user": "admin",
                    "password": "password",
                }
            ]
        }
        with open(self.test_file, "w") as f:
            json.dump(data, f)

        self.inventory.load_from_json(self.test_file)
        self.assertEqual(len(self.inventory), 1)
        devices = self.inventory.get_devices_by_platform("arista_eos")
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["platform"], "arista_eos")

    @patch("netcodeasync.modules.inventory.get_device_instance")
    def test_get_devices(self, mock_get_device):
        mock_device = MagicMock(spec=NetDevice)
        mock_get_device.return_value = mock_device

        self.inventory.add_device(
            platform="mikrotik_ros",
            host="192.168.88.1",
            user="admin",
            password="password",
        )

        devices = self.inventory.get_devices()
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0], mock_device)
        # Check that it was called with the device dict
        # Since add_device generates a uid, we need to match a dict that contains at least our inputs
        # Or we can just check the call args
        call_args = mock_get_device.call_args[0][0]
        self.assertEqual(call_args["platform"], "mikrotik_ros")
        self.assertEqual(call_args["host"], "192.168.88.1")
        self.assertEqual(call_args["user"], "admin")
        self.assertEqual(call_args["password"], "password")

    def test_iter(self):
        # Mocking get_devices for iteration test would be complex because __iter__ calls get_devices
        # Instead, let's just rely on the logic that get_devices returns a list
        # and verify we can iterate
        with patch.object(Inventory, "get_devices") as mock_get_devices:
            mock_get_devices.return_value = [1, 2, 3]
            items = [i for i in self.inventory]
            self.assertEqual(items, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
