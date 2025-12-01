from scrapli.driver.core import AsyncEOSDriver

from .netdevice import NetDevice


class AristaDevice(NetDevice):
    @property
    def driver_class(self):
        return AsyncEOSDriver
