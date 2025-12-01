# NetCodeAsync

NetCodeAsync is a network automation framework designed for asynchronous interaction with network devices. It leverages Python's `asyncio` to handle multiple device connections and operations concurrently.

## HTTP Server

The project includes an HTTP API server (`http_server.py`) that provides a RESTful interface for:

*   **Inventory Management**: Add and list network devices.
*   **Command Execution**: Run CLI commands against devices in the inventory.

### Usage

1.  **Start the Server**:
    ```bash
    uv run python3 http_server.py
    ```
    The server listens on port 8080.

2.  **Add a Device**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
        "platform": "mikrotik_ros",
        "host": "192.168.0.1",
        "user": "admin",
        "password": "password"
    }' http://localhost:8080/devices
    ```

3.  **Run a Command**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
        "host": "192.168.0.1",
        "command": "/system identity print"
    }' http://localhost:8080/command
    ```

## Todo

- [ ] Persistent inventory via SQLite
- [ ] Applying device configs (with concurrency locking for devices being configured)
