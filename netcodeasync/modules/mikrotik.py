import asyncio

from netcodeasync.models import get_device_instance

"""
Mikrotik specific functions
"""


def verify_device_type(conn_info: dict) -> None:
    if conn_info.get("platform") != "mikrotik_ros":
        raise SystemError(
            f"device type does not match function called|Inventory:{conn_info["platform"]}"
        )


async def get_routing_table(conn_info: dict) -> dict:
    tasks = []
    device = get_device_instance(
        {
            "platform": conn_info["platform"],
            "host": conn_info["ip"],
            "user": conn_info["user"],
            "password": conn_info["pass"],
        }
    )
    verify_device_type(conn_info)

    task = device.send_command(
        command="/ip route print",
    )
    tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


## todo, implement some other common functions
