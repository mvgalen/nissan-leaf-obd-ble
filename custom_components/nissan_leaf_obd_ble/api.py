"""API for nissan leaf obd ble."""

# import asyncio
import logging

from bleak.backends.device import BLEDevice

from .commands import leaf_commands
from .obd import OBD
from .decoders import (
    soc,
    lbc
)
from .OBDCommand import OBDCommand


_LOGGER: logging.Logger = logging.getLogger(__package__)


class NissanLeafObdBleApiClient:
    """API for connecting to the Nissan Leaf OBD BLE dongle."""

    def __init__(
        self,
        ble_device: BLEDevice,
    ) -> None:
        """Initialise."""
        self._ble_device = ble_device

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        if self._ble_device is None:
            return {}

        api = await OBD.create(self._ble_device, protocol="6")

        if api is None:
            return None

        data = {}
        w1_cmd = OBDCommand("wake1",                   "WAKE1",    b"00",      0, lbc, header=b"682",)
        await api.query(w1_cmd, force=True)
        w2_cmd = OBDCommand("wake2",                   "WAKE2",    b"00",      0, lbc, header=b"603",)
        await api.query(w2_cmd, force=True)
        w3_cmd = OBDCommand("wake3",                   "WAKE3",    b"00",      0, lbc, header=b"5c0",)
        await api.query(w3_cmd, force=True)

        for command in leaf_commands.values():
#            if command.name == "lbc":
#                lbc_cmd = OBDCommand("lbc",                   "Li-ion battery controller",    b"02210100000000000",      0, lbc, header=b"79B",)
#                await api.send(lbc_cmd, force=True)
            response = await api.query(command, force=True)
            # the first command is the Mystery command. If this doesn't have a response, then none of the other will
            if command.name == "unknown" and len(response.messages) == 0:
                break
            if response.value is not None:
                data.update(response.value)  # send the command, and parse the response
#        lbc_cmd = OBDCommand("lbc",                   "Li-ion battery controller",    b"0221010000000000",      53, lbc, header=b"79B",)
#        lbc2_cmd = OBDCommand("lbc",                   "Li-ion battery controller",    b"3000000000000000",      53, lbc, header=b"79B",)
#        await api.send(lbc_cmd)
#        response = await api.query(lbc2_cmd, force=True)
#        # the first command is the Mystery command. If this doesn't have a response, then none of the other will
#        if response.value is not None:
#            data.update(response.value)  # send the command, and parse the response


#        soc_cmd = OBDCommand("soc",                   "Soc",    b"022101",      8, soc,                    header=b"55B",)
#        response = await api.read(soc_cmd)
#        if response.value is not None:
#            data.update(response.value)

        _LOGGER.debug("Returning data: %s", data)
	
        await api.close()
        return data
