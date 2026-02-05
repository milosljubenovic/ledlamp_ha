"""Tests for __init__ module."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.leddmx import async_setup_entry, async_unload_entry
from custom_components.leddmx.const import DOMAIN


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {"mac": "AA:BB:CC:DD:EE:FF"}
    entry.options = {}
    entry.title = "Test Device"
    entry.add_update_listener = MagicMock(return_value=MagicMock())
    return entry


@pytest.fixture
def mock_bjled_instance():
    """Create a mock BJLEDInstance."""
    instance = MagicMock()
    instance.mac = "AA:BB:CC:DD:EE:FF"
    instance.name = "Test Device"
    instance.stop = AsyncMock()
    return instance


@pytest.mark.asyncio
@patch("custom_components.leddmx.BJLEDInstance")
async def test_async_setup_entry_success(
    mock_bjled_class, hass: HomeAssistant, mock_config_entry, mock_bjled_instance
):
    """Test successful setup entry."""
    mock_bjled_class.return_value = mock_bjled_instance
    
    result = await async_setup_entry(hass, mock_config_entry)
    
    assert result is True
    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]
    mock_config_entry.async_on_unload.assert_called()


@pytest.mark.asyncio
@patch("custom_components.leddmx.BJLEDInstance")
async def test_async_setup_entry_with_options(
    mock_bjled_class, hass: HomeAssistant, mock_config_entry, mock_bjled_instance
):
    """Test setup entry with options."""
    mock_config_entry.options = {"reset": True, "delay": 60}
    mock_bjled_class.return_value = mock_bjled_instance
    
    result = await async_setup_entry(hass, mock_config_entry)
    
    assert result is True
    mock_bjled_class.assert_called_once_with(
        "AA:BB:CC:DD:EE:FF", True, 60, hass
    )


@pytest.mark.asyncio
async def test_async_unload_entry_success(
    hass: HomeAssistant, mock_config_entry, mock_bjled_instance
):
    """Test successful unload entry."""
    hass.data[DOMAIN] = {mock_config_entry.entry_id: mock_bjled_instance}
    mock_config_entry.async_unload_platforms = AsyncMock(return_value=True)
    
    result = await async_unload_entry(hass, mock_config_entry)
    
    assert result is True
    mock_bjled_instance.stop.assert_called_once()
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_failure(
    hass: HomeAssistant, mock_config_entry, mock_bjled_instance
):
    """Test failed unload entry."""
    hass.data[DOMAIN] = {mock_config_entry.entry_id: mock_bjled_instance}
    # The code calls hass.config_entries.async_unload_platforms, not entry.async_unload_platforms
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)
    
    result = await async_unload_entry(hass, mock_config_entry)
    
    assert result is False
    # When unload fails, stop should not be called (only called if unload_ok is True)
    mock_bjled_instance.stop.assert_not_called()
    # The code removes the entry from hass.data even on failure (line 44 always executes)
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]
