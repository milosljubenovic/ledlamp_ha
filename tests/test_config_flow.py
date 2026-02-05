"""Tests for config flow."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.data_entry_flow import FlowResultType

from custom_components.leddmx.config_flow import BJLEDFlowHandler, DeviceData


@pytest.fixture
def mock_bluetooth_discovery():
    """Create a mock Bluetooth discovery info."""
    # Create a simple object with the required attributes
    class MockServiceInfo:
        def __init__(self):
            self.address = "AA:BB:CC:DD:EE:FF"
            self.name = "LEDDMX-03-DD2B"
            self.rssi = -50
    
    return MockServiceInfo()


@pytest.fixture
def mock_bluetooth_discovery_unsupported():
    """Create a mock unsupported Bluetooth discovery info."""
    service_info = MagicMock(spec=BluetoothServiceInfoBleak)
    service_info.address = "AA:BB:CC:DD:EE:00"
    service_info.name = "Unsupported Device"
    service_info.rssi = -50
    return service_info


class TestDeviceData:
    """Test DeviceData class."""

    def test_supported_device(self, mock_bluetooth_discovery):
        """Test that LEDDMX devices are supported."""
        device_data = DeviceData(mock_bluetooth_discovery)
        assert device_data.supported() is True

    def test_unsupported_device(self, mock_bluetooth_discovery_unsupported):
        """Test that non-LEDDMX devices are not supported."""
        device_data = DeviceData(mock_bluetooth_discovery_unsupported)
        assert device_data.supported() is False

    def test_address(self, mock_bluetooth_discovery):
        """Test address property."""
        device_data = DeviceData(mock_bluetooth_discovery)
        assert device_data.address() == "AA:BB:CC:DD:EE:FF"

    def test_rssi(self, mock_bluetooth_discovery):
        """Test RSSI property."""
        device_data = DeviceData(mock_bluetooth_discovery)
        assert device_data.rssi() == -50


class TestBJLEDFlowHandler:
    """Test BJLEDFlowHandler."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_bluetooth_discovery_supported(
        self, hass, mock_bluetooth_discovery
    ):
        """Test Bluetooth discovery with supported device."""
        # This test requires full Home Assistant setup with bluetooth
        # Skip for now as it needs more complex mocking
        pytest.skip("Requires full HA bluetooth setup")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_bluetooth_discovery_unsupported(
        self, hass, mock_bluetooth_discovery_unsupported
    ):
        """Test Bluetooth discovery with unsupported device."""
        # This test requires full Home Assistant setup with bluetooth
        pytest.skip("Requires full HA bluetooth setup")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_bluetooth_discovery_already_configured(
        self, hass, mock_bluetooth_discovery
    ):
        """Test Bluetooth discovery when device is already configured."""
        # This test requires full Home Assistant setup with bluetooth
        pytest.skip("Requires full HA bluetooth setup")

