from .aristadevice import AristaDevice
from .junosdevice import JunosDevice
from .mikrotikdevice import MikrotikDevice
from .netdevice import NetDevice


def get_device_instance(device_data):
    platform = device_data.get("platform")
    host = device_data.get("host")
    user = device_data.get("user")
    password = device_data.get("password")

    if platform == "mikrotik_ros":
        return MikrotikDevice(host, user, password)
    elif platform == "arista_eos":
        return AristaDevice(host, user, password)
    elif platform == "juniper_junos":
        return JunosDevice(host, user, password)
    else:
        raise ValueError(f"Unsupported platform: {platform}")


__all__ = [
    "NetDevice",
    "MikrotikDevice",
    "AristaDevice",
    "JunosDevice",
    "get_device_instance",
]
