from abc import ABC, abstractmethod

from scrapli.driver.core import AsyncEOSDriver, AsyncIOSXEDriver
from scrapli.exceptions import ScrapliException


# --- 1. The Abstract Base Class ---
class NetDevice(ABC):
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

    @property
    @abstractmethod
    def driver_class(self):
        """Child classes must define which Scrapli driver to use."""
        pass

    @property
    def driver_kwargs(self):
        """Child classes can define extra driver kwargs."""
        return {}

    async def send_command(self, command, semaphore, **kwargs):
        """
        Generic function to send any command.

        Args:
            command (str): The command to execute (e.g., "show ip int brief")
            semaphore (asyncio.Semaphore): The concurrency limiter
            **kwargs: Any extra arguments supported by scrapli's send_command
                      (e.g., timeout_ops=30, strip_prompt=False)
        """
        async with semaphore:
            # Define connection params
            device_params = {
                "host": self.hostname,
                "auth_username": self.username,
                "auth_password": self.password,
                "auth_strict_key": False,
                "transport": "asyncssh",
                "timeout_socket": 30,
                "timeout_transport": 60,
            }
            device_params.update(self.driver_kwargs)

            try:
                # Establish the connection
                async with self.driver_class(**device_params) as conn:

                    # Pass the command AND any extra kwargs (like timeouts) to Scrapli
                    response = await conn.send_command(command, **kwargs)

                    # Return a structured dictionary so the main loop knows who sent what
                    return {
                        "host": self.hostname,
                        "status": "success",
                        "command": command,
                        "output": response.result,
                    }

            except ScrapliException as e:
                return {
                    "host": self.hostname,
                    "status": "failed",
                    "command": command,
                    "error": str(e),
                }
