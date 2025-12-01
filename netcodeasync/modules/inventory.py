import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from netcodeasync.models import NetDevice, get_device_instance

"""
Inventory management
"""


class Inventory:
    """
    Manages a collection of network devices.
    """

    def __init__(self, devices: Optional[List[Dict[str, Any]]] = None):
        self._devices_data: Dict[str, Dict[str, Any]] = {}
        """
        {
            # uid: {device_data},
            "8caeaa6c0cebd6b5ddab9945076e817871d0a1d1": {
                "platform": "mikrotik",
                "host": "192.168.0.1",
                "user": "admin",
                "password": "password", 
                }
        }
        """
        if devices:
            for d in devices:
                self._add_device_from_dict(d)

    def _generate_uid(self, platform: str, host: str, user: str, password: str) -> str:
        s = f"{platform}{host}{user}{password}"
        return hashlib.sha1(s.encode()).hexdigest()

    def _add_device_from_dict(self, data: Dict[str, Any]):
        platform = data.get("platform")
        host = data.get("host")
        user = data.get("user")
        password = data.get("password")

        if all([platform, host, user, password]):
            uid = self._generate_uid(platform, host, user, password)
            # Make a copy to avoid modifying the input dict in place if it's reused
            device_data = data.copy()
            device_data["uid"] = uid
            self._devices_data[uid] = device_data

    def add_device(self, platform: str, host: str, user: str, password: str, **kwargs):
        """
        Add a single device to the inventory.
        """
        uid = self._generate_uid(platform, host, user, password)
        # todo check if uid already exists in the _devices_data, raise an exception if it does
        device_data = {
            "platform": platform,
            "host": host,
            "user": user,
            "password": password,
            "uid": uid,
        }
        device_data.update(kwargs)
        self._devices_data[uid] = device_data

    # todo: add a delete_device function, to remove a device if it matches one of the following kwargs (host, uid)

    def get_device_by_uid(self, uid: str) -> Dict[str, Any]:
        """
        Return a device dictionary by its UID.
        """
        if uid in self._devices_data:
            return self._devices_data[uid]
        raise ValueError(f"Device with UID {uid} not found")

    def get_devices_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """
        Return a list of device dictionaries matching the platform.
        """
        return [d for d in self._devices_data.values() if d.get("platform") == platform]

    def get_device_by_host(self, host: str) -> Dict[str, Any]:
        """
        Return a device dictionary by the host.
        Raises ValueError if host not found or if duplicate hosts are found.
        """
        matches = [d for d in self._devices_data.values() if d.get("host") == host]
        if not matches:
            raise ValueError(f"Device with host {host} not found")
        if len(matches) > 1:
            raise ValueError(f"Multiple devices found with host {host}")
        return matches[0]

    def load_from_json(self, path: Union[str, Path]):
        """
        Load devices from a JSON file.
        Expected format:
        [
            {
                "platform": "mikrotik_ros",
                "host": "192.168.1.1",
                "user": "admin",
                "password": "password"
            },
            ...
        ]
        OR
        {
            "devices": [...]
        }
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Inventory file not found: {path}")

        with open(path, "r") as f:
            data = json.load(f)

        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "devices" in data:
            items = data["devices"]
        else:
            raise ValueError(
                "Invalid JSON format. Expected list of devices or dict with 'devices' key."
            )

        for item in items:
            self._add_device_from_dict(item)

    def get_devices(self) -> List[NetDevice]:
        """
        Instantiate and return a list of NetDevice objects from the inventory data.
        """
        devices = []
        for d in self._devices_data.values():
            try:
                dev = get_device_instance(d)
                devices.append(dev)
            except Exception as e:
                print(f"Failed to instantiate device {d.get('host', 'unknown')}: {e}")
        return devices

    def __iter__(self):
        """Allow iterating directly over the instantiated devices."""
        return iter(self.get_devices())

    def __len__(self):
        return len(self._devices_data)
