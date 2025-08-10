"""
Basic MIDI humanization module.

This module provides simple velocity and timing randomization
for MIDI files without advanced musical analysis.
"""

import random
from .presets import get_preset_settings
from .core import resolve_overlapping_notes


def humanize_midi_basic(music, method="basic", preset_name="medium"):
    """
    Original basic MIDI humanization with simple randomization.

    Args:
        music: The muspy.Music object to humanize
        method: The humanization method (should be "basic")
        preset_name: The preset intensity to apply

    Returns:
        The humanized muspy.Music object
    """
    settings = get_preset_settings(method, preset_name)

    velocity_range = settings["velocity_range"]
    noteon_timing_range = settings["noteon_timing_range"]
    noteoff_timing_range = settings["noteoff_timing_range"]
    min_duration_beats = settings["min_duration_beats"]

    print(f"Applying {method} humanization with {preset_name} intensity:")
    print(f"  Velocity range: ±{velocity_range}")
    print(f"  Note-on timing range: ±{noteon_timing_range:.3f} beats")
    print(f"  Note-off timing range: ±{noteoff_timing_range:.3f} beats")
    print(f"  Minimum note duration: {min_duration_beats} beats")

    # Get the resolution for timing calculations
    resolution = music.resolution

    # Convert beat-based timing ranges to tick-based
    noteon_timing_ticks = int(noteon_timing_range * resolution)
    noteoff_timing_ticks = int(noteoff_timing_range * resolution)
    min_duration_ticks = int(min_duration_beats * resolution)

    print(
        f"  Timing in ticks (resolution={resolution}): note-on ±{noteon_timing_ticks}, note-off ±{noteoff_timing_ticks}"
    )

    for track in music.tracks:
        print(f"\nProcessing track: {track.name}")
        original_count = len(track.notes)

        for note in track.notes:
            original_start = note.start
            original_end = note.end
            original_velocity = note.velocity

            # Randomize velocity (clamp to MIDI range)
            velocity_offset = random.randint(-velocity_range, velocity_range)
            note.velocity = max(1, min(127, note.velocity + velocity_offset))

            # Randomize note-on timing
            start_offset = random.randint(-noteon_timing_ticks, noteon_timing_ticks)
            note.start = max(0, note.start + start_offset)

            # Randomize note-off timing
            end_offset = random.randint(-noteoff_timing_ticks, noteoff_timing_ticks)
            note.end = note.end + end_offset

            # Ensure minimum duration
            if note.end - note.start < min_duration_ticks:
                note.end = note.start + min_duration_ticks

            # Debug output for significant changes
            if (
                abs(velocity_offset) > velocity_range // 2
                or abs(start_offset) > noteon_timing_ticks // 2
            ):
                print(
                    f"    Note {note.pitch}: velocity {original_velocity}→{note.velocity}, "
                    f"timing {original_start}→{note.start}, duration {original_end-original_start}→{note.end-note.start}"
                )

        print(f"  Processed {original_count} notes")

    # Resolve overlapping notes
    resolve_overlapping_notes(music, min_duration_ticks)

    return music
