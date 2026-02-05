# Tests

This directory contains pytest tests for the LEDDMX integration.

## Running Tests

### Install test dependencies

```bash
pip install -r requirements-test.txt
```

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=custom_components/leddmx --cov-report=html
```

### Run specific test file

```bash
pytest tests/test_light.py
```

### Run specific test

```bash
pytest tests/test_light.py::TestBJLEDLight::test_init
```

## Test Structure

- `conftest.py` - Shared pytest fixtures
- `test_init.py` - Tests for integration setup/unload
- `test_config_flow.py` - Tests for configuration flow
- `test_light.py` - Tests for light platform entity
- `test_dmxled.py` - Tests for BLE communication
- `test_effects.py` - Tests for effects definitions

## Test Markers

Tests are marked with:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.bluetooth` - Tests requiring Bluetooth mocking

Run tests by marker:
```bash
pytest -m unit
```
