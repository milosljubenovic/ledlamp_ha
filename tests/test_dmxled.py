"""Tests for dmxled module."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bleak.exc import BleakDBusError
from bleak_retry_connector import BleakNotFoundError
from homeassistant.components.light import ColorMode
from custom_components.leddmx.dmxled import BJLEDInstance
from custom_components.leddmx.effects import effects_dmx


@pytest.mark.asyncio
async def test_init_success(hass, mock_ble_device, mock_async_ble_device_from_address):
    """Test successful initialization."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    assert instance._mac == "AA:BB:CC:DD:EE:FF"
    assert instance._reset is False
    assert instance._delay == 120
    assert instance._device == mock_ble_device
    assert instance._brightness == 255
    assert instance._color_mode == ColorMode.RGB


@pytest.mark.asyncio
async def test_init_device_not_found(hass, mock_async_ble_device_from_address):
    """Test initialization when device is not in cache uses fallback BLEDevice."""
    mock_async_ble_device_from_address.return_value = None

    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-2E0E", False, 120, hass)

    assert instance._device is not None
    assert instance._device.address == "AA:BB:CC:DD:EE:FF"
    assert instance._device.name == "LEDDMX-03-2E0E"


@pytest.mark.asyncio
async def test_detect_model(hass, mock_ble_device, mock_async_ble_device_from_address):
    """Test model detection."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    assert instance._model == 0
    assert instance._turn_on_cmd is not None
    assert instance._turn_off_cmd is not None


@pytest.mark.asyncio
async def test_mac_property(hass, mock_ble_device, mock_async_ble_device_from_address):
    """Test mac property."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    assert instance.mac == "AA:BB:CC:DD:EE:FF"


@pytest.mark.asyncio
async def test_name_property(hass, mock_ble_device, mock_async_ble_device_from_address):
    """Test name property."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    assert instance.name == "LEDDMX-03-DD2B"


@pytest.mark.asyncio
async def test_effect_list_property(hass, mock_ble_device, mock_async_ble_device_from_address):
    """Test effect_list property."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    effect_list = instance.effect_list
    assert isinstance(effect_list, list)
    assert len(effect_list) > 0
    assert "AUTO" in effect_list


@pytest.mark.asyncio
async def test_turn_on(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test turn_on method."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    await instance.turn_on()
    
    assert instance._is_on is True
    mock_bleak_client.write_gatt_char.assert_called()


@pytest.mark.asyncio
async def test_turn_off(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test turn_off method."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    await instance.turn_off()
    
    assert instance._is_on is False
    mock_bleak_client.write_gatt_char.assert_called()


@pytest.mark.asyncio
async def test_set_rgb_color(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test set_rgb_color method."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    await instance.set_rgb_color((255, 128, 0), 200)
    
    assert instance._rgb_color == (255, 128, 0)
    # set_rgb_color doesn't update self._brightness, it only uses the parameter
    # The brightness is used for calculation but not stored
    # So we check that the default brightness (255) is still there
    assert instance._brightness == 255
    mock_bleak_client.write_gatt_char.assert_called()


@pytest.mark.asyncio
async def test_set_brightness_local(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test set_brightness_local method."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    instance._rgb_color = (255, 0, 0)
    
    await instance.set_brightness_local(128)
    
    assert instance._brightness == 128
    mock_bleak_client.write_gatt_char.assert_called()


@pytest.mark.asyncio
async def test_set_effect(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test set_effect method."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    await instance.set_effect("AUTO")
    
    assert instance._effect == "AUTO"
    mock_bleak_client.write_gatt_char.assert_called()


@pytest.mark.asyncio
async def test_set_effect_invalid(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test set_effect with invalid effect."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    await instance.set_effect("Invalid Effect")
    
    mock_bleak_client.write_gatt_char.assert_not_called()


@pytest.mark.asyncio
async def test_update(
    hass, mock_ble_device, mock_async_ble_device_from_address
):
    """Test update method."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    await instance.update()
    
    # Update doesn't do anything currently, just verify it doesn't raise


@pytest.mark.asyncio
async def test_stop(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test stop method."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    # Connect first
    await instance.turn_on()
    
    # Then stop
    await instance.stop()
    
    mock_bleak_client.disconnect.assert_called()


@pytest.mark.asyncio
async def test_retry_on_bluetooth_error(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test retry mechanism on Bluetooth errors."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    # Simulate a retryable error followed by success
    # BleakDBusError requires error_body parameter
    mock_bleak_client.write_gatt_char.side_effect = [
        BleakDBusError("test error", {"error": "test"}),
        None,
    ]
    
    await instance.turn_on()
    
    # Should have retried
    assert mock_bleak_client.write_gatt_char.call_count >= 2


@pytest.mark.asyncio
async def test_retry_on_bleak_not_found_error(
    hass, mock_ble_device, mock_async_ble_device_from_address,
    mock_establish_connection, mock_bleak_client
):
    """Test that BleakNotFoundError is not retried."""
    instance = BJLEDInstance("AA:BB:CC:DD:EE:FF", "LEDDMX-03-DD2B", False, 120, hass)
    
    mock_bleak_client.write_gatt_char.side_effect = BleakNotFoundError("Device not found")
    
    with pytest.raises(BleakNotFoundError):
        await instance.turn_on()
