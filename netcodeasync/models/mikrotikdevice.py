from scrapli_community.mikrotik.routeros.async_driver import AsyncMikrotikRouterOSDriver

from .netdevice import NetDevice


class MikrotikDevice(NetDevice):
    @property
    def driver_class(self):
        return AsyncMikrotikRouterOSDriver

    @property
    def driver_kwargs(self):
        return {
            # Relax the prompt pattern to match typical Mikrotik prompts
            # even if there are trailing spaces or duplicated prompts.
            "comms_prompt_pattern": r"\[.+?@.+?\] >.*",
        }
