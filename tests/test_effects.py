"""Tests for effects module."""
from custom_components.leddmx.effects import effects_dmx


def test_effects_dmx_is_dict():
    """Test that effects_dmx is a dictionary."""
    assert isinstance(effects_dmx, dict)


def test_effects_dmx_not_empty():
    """Test that effects_dmx contains effects."""
    assert len(effects_dmx) > 0


def test_effects_dmx_contains_auto():
    """Test that AUTO effect exists."""
    assert "AUTO" in effects_dmx
    assert effects_dmx["AUTO"] == 255


def test_effects_dmx_values_are_integers():
    """Test that all effect values are integers."""
    for effect_name, effect_id in effects_dmx.items():
        assert isinstance(effect_id, int), f"Effect {effect_name} should have integer ID"


def test_effects_dmx_values_range():
    """Test that effect IDs are in valid range."""
    for effect_name, effect_id in effects_dmx.items():
        if effect_name == "AUTO":
            assert effect_id == 255
        else:
            assert 1 <= effect_id <= 255, f"Effect {effect_name} ID {effect_id} out of range"


def test_effects_dmx_has_common_effects():
    """Test that common effects exist."""
    common_effects = [
        "AUTO",
        "1:Forward Dreaming",
        "2:Backward Dreaming",
        "80:Strobe White",
    ]
    for effect in common_effects:
        assert effect in effects_dmx, f"Common effect {effect} should exist"
