"""Tests for light platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_EFFECT, ATTR_RGB_COLOR
from homeassistant.const import CONF_MAC

from custom_components.leddmx.light import BJLEDLight, async_setup_entry
from custom_components.leddmx.const import DOMAIN


@pytest.fixture
def mock_bjled_instance():
    """Create a mock BJLEDInstance."""
    instance = MagicMock()
    instance.mac = "AA:BB:CC:DD:EE:FF"
    instance.name = "Test LEDDMX"
    instance.is_on = True
    instance.brightness = 255
    instance.rgb_color = (255, 0, 0)
    instance._effect = None
    instance._color_mode = "rgb"
    instance.effect_list = ["AUTO", "1:Forward Dreaming"]
    instance.turn_on = AsyncMock()
    instance.turn_off = AsyncMock()
    instance.set_rgb_color = AsyncMock()
    instance.set_brightness_local = AsyncMock()
    instance.set_effect = AsyncMock()
    instance.update = AsyncMock()
    return instance


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "mac": "AA:BB:CC:DD:EE:FF",
        "name": "Test LEDDMX Device",
    }
    return entry


class TestBJLEDLight:
    """Test BJLEDLight entity."""

    def test_init(self, mock_bjled_instance):
        """Test entity initialization."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        
        assert light._instance == mock_bjled_instance
        assert light._entry_id == "test_entry_id"
        assert light._attr_name == "Test Light"
        assert light._attr_unique_id == "AA:BB:CC:DD:EE:FF"

    def test_available(self, mock_bjled_instance):
        """Test available property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.available is True

    def test_brightness(self, mock_bjled_instance):
        """Test brightness property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.brightness == 255

    def test_rgb_color(self, mock_bjled_instance):
        """Test rgb_color property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.rgb_color == (255, 0, 0)

    def test_is_on(self, mock_bjled_instance):
        """Test is_on property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.is_on is True

    def test_effect_list(self, mock_bjled_instance):
        """Test effect_list property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.effect_list == ["AUTO", "1:Forward Dreaming"]

    def test_effect(self, mock_bjled_instance):
        """Test effect property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.effect is None

    def test_color_mode(self, mock_bjled_instance):
        """Test color_mode property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.color_mode == "rgb"

    def test_should_poll(self, mock_bjled_instance):
        """Test should_poll property."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        assert light.should_poll is False

    @pytest.mark.asyncio
    async def test_async_turn_on(self, mock_bjled_instance):
        """Test turning on the light."""
        mock_bjled_instance.is_on = False  # Light is off, so turn_on should be called
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        light.async_write_ha_state = MagicMock()
        
        await light.async_turn_on()
        
        mock_bjled_instance.turn_on.assert_called_once()
        light.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_turn_on_with_brightness(self, mock_bjled_instance):
        """Test turning on with brightness."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        light.async_write_ha_state = MagicMock()
        
        await light.async_turn_on(**{ATTR_BRIGHTNESS: 128})
        
        mock_bjled_instance.set_brightness_local.assert_called_once_with(128)
        light.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_turn_on_with_rgb(self, mock_bjled_instance):
        """Test turning on with RGB color."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        light.async_write_ha_state = MagicMock()
        
        await light.async_turn_on(**{ATTR_RGB_COLOR: (0, 255, 0)})
        
        mock_bjled_instance.set_rgb_color.assert_called_once_with((0, 255, 0), None)
        light.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_turn_on_with_effect(self, mock_bjled_instance):
        """Test turning on with effect."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        light.async_write_ha_state = MagicMock()
        
        await light.async_turn_on(**{ATTR_EFFECT: "AUTO"})
        
        mock_bjled_instance.set_effect.assert_called_once_with("AUTO")
        light.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_turn_off(self, mock_bjled_instance):
        """Test turning off the light."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        light.async_write_ha_state = MagicMock()
        
        await light.async_turn_off()
        
        mock_bjled_instance.turn_off.assert_called_once()
        light.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_set_effect(self, mock_bjled_instance):
        """Test setting effect."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        light.async_write_ha_state = MagicMock()
        
        await light.async_set_effect("AUTO")
        
        assert light._effect == "AUTO"
        mock_bjled_instance.set_effect.assert_called_once_with("AUTO")
        light.async_write_ha_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update(self, mock_bjled_instance):
        """Test updating the entity."""
        light = BJLEDLight(mock_bjled_instance, "Test Light", "test_entry_id")
        light.async_write_ha_state = MagicMock()
        
        await light.async_update()
        
        mock_bjled_instance.update.assert_called_once()
        light.async_write_ha_state.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry(hass, mock_config_entry, mock_bjled_instance):
    """Test async_setup_entry."""
    hass.data[DOMAIN] = {mock_config_entry.entry_id: mock_bjled_instance}
    async_add_devices = MagicMock()
    
    await async_setup_entry(hass, mock_config_entry, async_add_devices)

    async_add_devices.assert_called_once()
    assert len(async_add_devices.call_args[0][0]) == 1
    assert isinstance(async_add_devices.call_args[0][0][0], BJLEDLight)
