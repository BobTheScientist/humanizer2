"""
Humanizer package for MIDI humanization.

This package provides various methods for making MIDI files sound more natural
and human-like through different humanization techniques.
"""

from .basic import humanize_midi_basic
from .piano_performance import humanize_midi_advanced
from .presets import HUMANIZATION_METHODS, get_preset_settings

__all__ = [
    "humanize_midi_basic",
    "humanize_midi_advanced",
    "HUMANIZATION_METHODS",
    "get_preset_settings",
]
