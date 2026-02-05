"""Pytest configuration and fixtures."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTCharacteristic, BleakGATTServiceCollection
from home_assistant_bluetooth import BluetoothServiceInfo
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import HomeAssistant

from custom_components.leddmx.const import DOMAIN


@pytest.fixture
def hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_reload = AsyncMock()
    hass.bus = MagicMock()
    hass.bus.async_listen_once = MagicMock(return_value=MagicMock())
    return hass




@pytest.fixture
def mock_ble_device():
    """Create a mock BLE device."""
    device = MagicMock(spec=BLEDevice)
    device.address = "AA:BB:CC:DD:EE:FF"
    device.name = "LEDDMX-03-DD2B"
    device.rssi = -50
    return device


@pytest.fixture
def mock_bluetooth_service_info(mock_ble_device):
    """Create a mock BluetoothServiceInfoBleak."""
    service_info = MagicMock(spec=BluetoothServiceInfoBleak)
    service_info.address = mock_ble_device.address
    service_info.name = mock_ble_device.name
    service_info.rssi = mock_ble_device.rssi
    service_info.device = mock_ble_device
    return service_info


@pytest.fixture
def mock_bleak_client():
    """Create a mock BleakClientWithServiceCache."""
    client = AsyncMock()
    client.is_connected = True
    client.services = MagicMock(spec=BleakGATTServiceCollection)
    
    # Mock characteristic
    char = MagicMock(spec=BleakGATTCharacteristic)
    char.uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"
    client.services.get_characteristic = MagicMock(return_value=char)
    
    client.write_gatt_char = AsyncMock()
    client.disconnect = AsyncMock()
    return client


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "mac": "AA:BB:CC:DD:EE:FF",
        "name": "Test LEDDMX Device",
    }
    entry.options = {}
    entry.title = "Test LEDDMX Device"
    entry.add_update_listener = MagicMock(return_value=MagicMock())
    return entry


@pytest.fixture
def mock_async_ble_device_from_address(mock_ble_device):
    """Mock async_ble_device_from_address."""
    with patch(
        "custom_components.leddmx.dmxled.bluetooth.async_ble_device_from_address",
        return_value=mock_ble_device,
    ) as mock:
        yield mock


@pytest.fixture
def mock_establish_connection(mock_bleak_client):
    """Mock establish_connection from bleak_retry_connector."""
    async def _establish_connection(*args, **kwargs):
        return mock_bleak_client
    
    with patch(
        "custom_components.leddmx.dmxled.establish_connection",
        side_effect=_establish_connection,
    ) as mock:
        yield mock
