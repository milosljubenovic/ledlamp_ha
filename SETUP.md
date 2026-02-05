# Development Setup

This project uses `uv` for fast Python package management and virtual environment handling.

## Initial Setup

1. **Create virtual environment:**
   ```bash
   uv venv
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Install project with test dependencies:**
   ```bash
   uv pip install -e ".[test]"
   ```

## Running Tests

```bash
# Activate venv first
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components/leddmx --cov-report=html

# Run specific test file
pytest tests/test_light.py

# Run specific test
pytest tests/test_light.py::TestBJLEDLight::test_init
```

## Project Structure

- `pyproject.toml` - Project configuration and dependencies
- `.venv/` - Virtual environment (gitignored)
- `tests/` - Test suite
- `custom_components/leddmx/` - Integration code

## Dependencies

- **Runtime:** `bleak`, `bleak-retry-connector`, `bluetooth-data-tools`, `bluetooth-sensor-state-data`, `home-assistant-bluetooth`
- **Test:** `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `homeassistant`, `freezegun`, `pyserial`

All dependencies are managed in `pyproject.toml`.
