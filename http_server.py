import asyncio

from aiohttp import web

from netcodeasync.models import get_device_instance
from netcodeasync.modules.inventory import Inventory

"""
HTTP API server to interface with NetCodeAsync

run: python3 http_server.py > server_v2.log 2>&1 &
add device: curl -X PUT -H "Content-Type: application/json" -d '{"platform": "mikrotik_ros", "host": "192.168.0.1", "user": "admin", "password": "password"}' http://localhost:8080/device
do a command: curl -X PUT -H "Content-Type: application/json" -d '{"host": "192.168.0.1", "command": "/system identity print"}' http://localhost:8080/command
"""


async def get_devices(request):
    inventory = request.app["inventory"]
    # Accessing protected member to list devices
    devices = list(inventory._devices_data.values())
    return web.json_response(devices)


async def add_device(request):
    inventory = request.app["inventory"]
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    try:
        # Expects platform, host, user, password
        inventory.add_device(**data)
        return web.json_response({"status": "added", "device": data}, status=201)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


async def execute_command(request):
    inventory = request.app["inventory"]
    semaphore = request.app["semaphore"]

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    host = data.get("host")
    command = data.get("command")

    if not host or not command:
        return web.json_response({"error": "host and command required"}, status=400)

    try:
        device_data = inventory.get_device_by_host(host)
        device = get_device_instance(device_data)

        # device.send_command is async, await directly
        result = await device.send_command(command, semaphore=semaphore)
        return web.json_response(result)

    except ValueError as e:
        return web.json_response({"error": str(e)}, status=404)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def init_app_state(app):
    # Initialize semaphore within the event loop context
    app["semaphore"] = asyncio.Semaphore(20)


def main():
    app = web.Application()
    app["inventory"] = Inventory()

    # Register startup callback to initialize async objects
    app.on_startup.append(init_app_state)

    app.add_routes(
        [
            web.get("/devices", get_devices),
            web.put("/devices", add_device),
            web.put("/command", execute_command),
        ]
    )

    print("NetCodeAsync HTTP Server starting on port 8080...")
    web.run_app(app, port=8080)


if __name__ == "__main__":
    main()
