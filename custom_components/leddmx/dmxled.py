import asyncio
from collections.abc import Callable

# import traceback
import logging
from typing import Any, TypeVar, cast

from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTServiceCollection
from bleak.exc import BleakDBusError, BleakError
from bleak_retry_connector import (
    BLEAK_RETRY_EXCEPTIONS as BLEAK_EXCEPTIONS,
    BleakClientWithServiceCache,
    # BleakError,
    BleakNotFoundError,
    # ble_device_has_changed,
    establish_connection,
)

from homeassistant.components import bluetooth
from homeassistant.components.light import ColorMode

LOGGER = logging.getLogger(__name__)

from .effects import effects_dmx as EFFECT_MAP

EFFECT_LIST = ["None"] + list(EFFECT_MAP.keys())

LEDDMX_NAME_PREFIX = "leddmx-"
WRITE_CHARACTERISTIC_UUIDS = ["0000ffe1-0000-1000-8000-00805f9b34fb"]

TURN_ON_CMD = bytearray.fromhex("7b ff 07 00 00 ff 00 ff bf")
TURN_OFF_CMD = bytearray.fromhex("7b ff 07 00 00 00 00 ff bf")
DEFAULT_ATTEMPTS = 3
BLEAK_BACKOFF_TIME = 0.25
RETRY_BACKOFF_EXCEPTIONS = BleakDBusError

WrapFuncType = TypeVar("WrapFuncType", bound=Callable[..., Any])


def retry_bluetooth_connection_error(func: WrapFuncType) -> WrapFuncType:
    async def _async_wrap_retry_bluetooth_connection_error(
        self: "BJLEDInstance", *args: Any, **kwargs: Any
    ) -> Any:
        attempts = DEFAULT_ATTEMPTS
        max_attempts = attempts - 1

        for attempt in range(attempts):
            try:
                return await func(self, *args, **kwargs)
            except BleakNotFoundError:
                # The lock cannot be found so there is no
                # point in retrying.
                raise
            except RETRY_BACKOFF_EXCEPTIONS as err:
                if attempt >= max_attempts:
                    LOGGER.debug(
                        "%s: %s error calling %s, reach max attempts (%s/%s)",
                        self.name,
                        type(err),
                        func,
                        attempt,
                        max_attempts,
                        exc_info=True,
                    )
                    raise
                LOGGER.debug(
                    "%s: %s error calling %s, backing off %ss, retrying (%s/%s)...",
                    self.name,
                    type(err),
                    func,
                    BLEAK_BACKOFF_TIME,
                    attempt,
                    max_attempts,
                    exc_info=True,
                )
                await asyncio.sleep(BLEAK_BACKOFF_TIME)
            except BLEAK_EXCEPTIONS as err:
                if attempt >= max_attempts:
                    LOGGER.debug(
                        "%s: %s error calling %s, reach max attempts (%s/%s): %s",
                        self.name,
                        type(err),
                        func,
                        attempt,
                        max_attempts,
                        err,
                        exc_info=True,
                    )
                    raise
                LOGGER.debug(
                    "%s: %s error calling %s, retrying  (%s/%s)...: %s",
                    self.name,
                    type(err),
                    func,
                    attempt,
                    max_attempts,
                    err,
                    exc_info=True,
                )

    return cast(WrapFuncType, _async_wrap_retry_bluetooth_connection_error)


class BJLEDInstance:
    def __init__(
        self, address: str, name: str, reset: bool, delay: int, hass
    ) -> None:
        self.loop = asyncio.get_running_loop()
        self._mac = address
        self._reset = reset
        self._delay = delay
        self._hass = hass
        self._device: BLEDevice = bluetooth.async_ble_device_from_address(
            self._hass, address
        ) or BLEDevice(address, name or "LEDDMX", None)
        self._connect_lock: asyncio.Lock = asyncio.Lock()
        self._client: BleakClientWithServiceCache | None = None
        self._disconnect_timer: asyncio.TimerHandle | None = None
        self._cached_services: BleakGATTServiceCollection | None = None
        self._expected_disconnect = False
        self._is_on = None
        self._rgb_color = None
        self._brightness = 255
        self._effect = None
        self._effect_speed = 0x64
        self._color_mode = ColorMode.RGB
        self._write_uuid = None
        self._turn_on_cmd = None
        self._turn_off_cmd = None
        self._model = self._detect_model()

        LOGGER.debug(
            "Model information for device %s : ModelNo %s. MAC: %s",
            self._device.name,
            self._model,
            self._mac,
        )

    def _detect_model(self) -> int:
        device_name = (self._device.name or "").lower()
        if device_name.startswith(LEDDMX_NAME_PREFIX):
            self._turn_on_cmd = TURN_ON_CMD
            self._turn_off_cmd = TURN_OFF_CMD
            return 0
        self._turn_on_cmd = TURN_ON_CMD
        self._turn_off_cmd = TURN_OFF_CMD
        return 0

    async def _write(self, data: bytearray):
        """Send command to device and read response."""
        if data is None:
            raise ValueError(f"{self.name}: Command data is None (device model may not be supported)")
        await self._ensure_connected()
        await self._write_while_connected(data)

    async def _write_while_connected(self, data: bytearray):
        if data is None:
            return
        LOGGER.debug("%s: Writing data: %s", self.name, data.hex())
        await self._client.write_gatt_char(self._write_uuid, data, False)

    @property
    def mac(self):
        return self._device.address

    @property
    def reset(self):
        return self._reset

    @property
    def name(self):
        return self._device.name

    @property
    def rssi(self):
        return self._device.rssi

    @property
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    @property
    def rgb_color(self):
        return self._rgb_color

    @property
    def effect_list(self) -> list[str]:
        return EFFECT_LIST

    @property
    def effect(self):
        return self._effect

    @property
    def color_mode(self):
        return self._color_mode

    @retry_bluetooth_connection_error
    async def set_rgb_color(
        self, rgb: tuple[int, int, int], brightness: int | None = None
    ):
        self._rgb_color = rgb
        if brightness is None:
            if self._brightness is None:
                self._brightness = 255
            else:
                brightness = self._brightness
        brightness_percent = int(brightness * 100 / 255)
        # Now adjust the RBG values to match the brightness
        red = int(rgb[0] * brightness_percent / 100)
        green = int(rgb[1] * brightness_percent / 100)
        blue = int(rgb[2] * brightness_percent / 100)
        # RGB packet
        rgb_packet = bytearray.fromhex("7b ff 07")
        rgb_packet.append(red)
        rgb_packet.append(green)
        rgb_packet.append(blue)
        rgb_packet.extend(bytearray.fromhex("00 ff bf"))
        LOGGER.info("RGB Packet: %s", rgb_packet.hex())
        await self._write(rgb_packet)

    async def set_brightness_local(self, value: int):
        # 0 - 255, should convert automatically with the hex calls
        # call color temp or rgb functions to update
        self._brightness = value
        await self.set_rgb_color(self._rgb_color, value)

    @retry_bluetooth_connection_error
    async def turn_on(self):
        await self._write(self._turn_on_cmd or TURN_ON_CMD)
        self._is_on = True

    @retry_bluetooth_connection_error
    async def turn_off(self):
        await self._write(self._turn_off_cmd or TURN_OFF_CMD)
        self._is_on = False

    @retry_bluetooth_connection_error
    async def set_effect(self, effect: str):
        if effect not in EFFECT_LIST:
            LOGGER.error("Effect %s not supported", effect)
            return
        self._effect = effect

        if effect == "None":
            self._effect = None
            rgb = self._rgb_color or (255, 255, 255)
            await self.set_rgb_color(rgb)
            return

        effect_id = EFFECT_MAP.get(effect)
        hex_cmd = f"7b ff 03 {effect_id:02x} ff ff ff ff bf"
        LOGGER.debug("Effect ID: %s", effect_id)
        LOGGER.debug("Effect name: %s", effect)
        LOGGER.debug("Effect hex_cmd: %s", hex_cmd)
        await self._write(bytearray.fromhex(hex_cmd))

    @retry_bluetooth_connection_error
    async def update(self):
        LOGGER.debug("%s: Update in bjled called", self.name)
        # I dont think we have anything to update

    async def _ensure_connected(self) -> None:
        """Ensure connection to device is established."""
        if self._connect_lock.locked():
            LOGGER.debug(
                "%s: Connection already in progress, waiting for it to complete",
                self.name,
            )
        if self._client and self._client.is_connected:
            self._reset_disconnect_timer()
            return
        async with self._connect_lock:
            # Check again while holding the lock
            if self._client and self._client.is_connected:
                self._reset_disconnect_timer()
                return
            LOGGER.debug("%s: Connecting", self.name)
            client = await establish_connection(
                BleakClientWithServiceCache,
                self._device,
                self.name,
                self._disconnected,
                cached_services=self._cached_services,
                ble_device_callback=lambda: self._device,
            )
            LOGGER.debug("%s: Connected", self.name)
            resolved = self._resolve_characteristics(client.services)
            if not resolved:
                # Try to handle services failing to load
                # resolved = self._resolve_characteristics(await client.get_services())
                resolved = self._resolve_characteristics(client.services)
            self._cached_services = client.services if resolved else None

            self._client = client
            self._reset_disconnect_timer()

    def _resolve_characteristics(self, services: BleakGATTServiceCollection) -> bool:
        """Resolve characteristics."""
        for characteristic in WRITE_CHARACTERISTIC_UUIDS:
            if char := services.get_characteristic(characteristic):
                self._write_uuid = char
                break
        return bool(self._write_uuid)

    def _reset_disconnect_timer(self) -> None:
        """Reset disconnect timer."""
        if self._disconnect_timer:
            self._disconnect_timer.cancel()
        self._expected_disconnect = False
        if self._delay is not None and self._delay != 0:
            LOGGER.debug(
                "%s: Configured disconnect from device in %s seconds",
                self.name,
                self._delay,
            )
            self._disconnect_timer = self.loop.call_later(self._delay, self._disconnect)

    def _disconnected(self, client: BleakClientWithServiceCache) -> None:
        """Disconnected callback."""
        if self._expected_disconnect:
            LOGGER.debug("%s: Disconnected from device", self.name)
            return
        LOGGER.debug(
            "%s: Device unexpectedly disconnected (common with BLE, will reconnect on next use)",
            self.name,
        )

    def _disconnect(self) -> None:
        """Disconnect from device."""
        self._disconnect_timer = None
        asyncio.create_task(self._execute_timed_disconnect())

    async def stop(self) -> None:
        """Stop the LEDBLE."""
        LOGGER.debug("%s: Stop", self.name)
        await self._execute_disconnect()

    async def _execute_timed_disconnect(self) -> None:
        """Execute timed disconnection."""
        LOGGER.debug("%s: Disconnecting after timeout of %s", self.name, self._delay)
        await self._execute_disconnect()

    async def _execute_disconnect(self) -> None:
        """Execute disconnection."""
        async with self._connect_lock:
            client = self._client
            self._expected_disconnect = True
            self._client = None
            self._write_uuid = None
            if client and client.is_connected:
                try:
                    await client.disconnect()
                except (BleakDBusError, BleakError) as err:
                    LOGGER.debug(
                        "%s: Bluetooth reported error during disconnect (connection already closed): %s",
                        self.name,
                        err,
                    )
            LOGGER.debug("%s: Disconnected", self.name)
