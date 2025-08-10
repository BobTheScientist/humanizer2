"""
Enhanced presets and configuration for MIDI humanization methods.

This module contains all the preset definitions for different humanization
methods with normal distribution parameters for more realistic chord rolling.
"""

# Enhanced humanization methods with normal distribution chord rolling
HUMANIZATION_METHODS = {
    "basic": {
        "name": "Basic Randomization",
        "description": "Simple velocity and timing randomization",
        "presets": {
            "minimal": {
                "velocity_range": 5,
                "noteon_timing_range": 0.005,
                "noteoff_timing_range": 0.002,
                "min_duration_beats": 1 / 32,
                "chord_roll_probability": 0.0,  # No rolling in basic mode
                "chord_roll_timing": 0.002,
                "description": "Very subtle humanization - barely noticeable variations",
            },
            "medium": {
                "velocity_range": 10,
                "noteon_timing_range": 0.01,
                "noteoff_timing_range": 0.005,
                "min_duration_beats": 1 / 32,
                "chord_roll_probability": 0.0,  # No rolling in basic mode
                "chord_roll_timing": 0.004,
                "description": "Moderate humanization - natural musical variations",
            },
            "aggressive": {
                "velocity_range": 20,
                "noteon_timing_range": 0.02,
                "noteoff_timing_range": 0.01,
                "min_duration_beats": 1 / 32,
                "chord_roll_probability": 0.0,  # No rolling in basic mode
                "chord_roll_timing": 0.006,
                "description": "Strong humanization - pronounced expressive variations",
            },
        },
    },
    "piano_performance": {
        "name": "Advanced Piano Performance",
        "description": "Realistic piano performance with normal distribution chord rolling and hand separation",
        "presets": {
            "classical": {
                "velocity_range": 12,
                "noteon_timing_range": 0.008,
                "noteoff_timing_range": 0.004,
                "min_duration_beats": 1 / 32,
                "chord_roll_probability": 0.05,  # 5% base probability
                "chord_roll_probability_std": 0.015,  # Varies ±1.5%
                "chord_roll_mean_timing": 0.0002,  # Extremely subtle mean (0.096 ticks at 480 resolution)
                "chord_roll_std_timing": 0.0001,  # Very tight distribution
                "hand_separation_enabled": True,
                "left_hand_timing_factor": 0.7,
                "right_hand_velocity_factor": 1.2,
                "beat_accenting": True,
                "chord_velocity_correlation": True,
                "description": "Classical piano style with barely perceptible chord rolling and hand independence",
            },
            "romantic": {
                "velocity_range": 18,
                "noteon_timing_range": 0.015,
                "noteoff_timing_range": 0.008,
                "min_duration_beats": 1 / 32,
                "chord_roll_probability": 0.08,  # 8% base probability
                "chord_roll_probability_std": 0.025,  # More variation ±2.5%
                "chord_roll_mean_timing": 0.0003,  # Still very subtle (0.144 ticks at 480)
                "chord_roll_std_timing": 0.0002,  # Slightly more variation
                "hand_separation_enabled": True,
                "left_hand_timing_factor": 0.6,
                "right_hand_velocity_factor": 1.4,
                "beat_accenting": True,
                "chord_velocity_correlation": True,
                "description": "Romantic piano style with subtle expressive chord rolling and rubato",
            },
            "jazz": {
                "velocity_range": 15,
                "noteon_timing_range": 0.012,
                "noteoff_timing_range": 0.006,
                "min_duration_beats": 1 / 32,
                "chord_roll_probability": 0.12,  # 12% base probability
                "chord_roll_probability_std": 0.04,  # Lots of variation ±4%
                "chord_roll_mean_timing": 0.0004,  # Slightly more noticeable (0.192 ticks)
                "chord_roll_std_timing": 0.0003,  # More expressive variation
                "hand_separation_enabled": True,
                "left_hand_timing_factor": 0.8,
                "right_hand_velocity_factor": 1.3,
                "jazz_chord_emphasis": True,
                "beat_accenting": True,
                "chord_velocity_correlation": True,
                "description": "Jazz piano style with varied chord rolling and swing feel",
            },
        },
    },
}


def get_preset_settings(method, preset_name):
    """Get settings for a humanization method and preset"""
    if method not in HUMANIZATION_METHODS:
        raise ValueError(f"Unknown method: {method}")

    if preset_name not in HUMANIZATION_METHODS[method]["presets"]:
        available_presets = list(HUMANIZATION_METHODS[method]["presets"].keys())
        raise ValueError(
            f"Unknown preset '{preset_name}' for method '{method}'. Available: {available_presets}"
        )

    return HUMANIZATION_METHODS[method]["presets"][preset_name]
