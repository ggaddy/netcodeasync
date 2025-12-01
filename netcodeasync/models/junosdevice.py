from scrapli.driver.core import AsyncJunosDriver

from .netdevice import NetDevice


class JunosDevice(NetDevice):
    @property
    def driver_class(self):
        return AsyncJunosDriver
