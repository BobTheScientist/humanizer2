"""
Advanced piano performance humanization module.

This module provides sophisticated humanization techniques specifically
designed for piano music, including chord rolling, hand separation,
beat accenting, and musical phrasing.
"""

import random
from collections import defaultdict
from .presets import get_preset_settings
from .core import (
    detect_chords,
    apply_chord_rolling,
    separate_hands_by_pitch,
    detect_phrase_endings,
    choose_roll_pattern,
    apply_beat_accenting_and_correlation,
    apply_phrase_end_ritardando,
    group_notes_by_timing,
    resolve_overlapping_notes,
)


def humanize_hand(notes, hand_type, settings):
    """
    Apply hand-specific humanization.

    Args:
        notes: List of notes for this hand
        hand_type: "left" or "right"
        settings: Humanization settings
    """
    if hand_type == "left":
        # Left hand (accompaniment) - more stable, less variation
        timing_factor = settings.get("left_hand_timing_factor", 0.8)
        velocity_factor = 0.9
    else:
        # Right hand (melody) - more expressive
        timing_factor = 1.0
        velocity_factor = settings.get("right_hand_velocity_factor", 1.1)

    # Apply timing variations
    timing_range = int(
        settings["noteon_timing_range"] * settings["resolution"] * timing_factor
    )
    for note in notes:
        start_offset = random.randint(-timing_range, timing_range)
        note.start = max(0, note.start + start_offset)

    # Apply velocity variations with beat accenting and correlation
    hand_settings = settings.copy()
    hand_settings["velocity_range"] = int(settings["velocity_range"] * velocity_factor)
    apply_beat_accenting_and_correlation(notes, hand_settings)


def humanize_midi_advanced(music, method="piano_performance", preset_name="classical"):
    """
    Advanced MIDI humanization with chord rolling and musical intelligence.

    Args:
        music: The muspy.Music object to humanize
        method: The humanization method (should be "piano_performance")
        preset_name: The preset style to apply

    Returns:
        The humanized muspy.Music object
    """
    settings = get_preset_settings(method, preset_name)
    settings["resolution"] = music.resolution

    print(f"Applying {method} humanization with {preset_name} style:")
    print(f"  Velocity range: ±{settings['velocity_range']}")
    print(f"  Chord roll probability: {settings['chord_roll_probability']:.1%}")
    print(f"  Hand separation: {settings.get('hand_separation_enabled', False)}")
    print(f"  Beat accenting: {settings.get('beat_accenting', False)}")
    print(
        f"  Chord velocity correlation: {settings.get('chord_velocity_correlation', False)}"
    )

    # Convert timing ranges to ticks
    noteon_timing_ticks = int(settings["noteon_timing_range"] * music.resolution)
    noteoff_timing_ticks = int(settings["noteoff_timing_range"] * music.resolution)
    min_duration_ticks = int(settings["min_duration_beats"] * music.resolution)
    chord_roll_ticks = int(settings["chord_roll_timing"] * music.resolution)

    for track in music.tracks:
        print(f"\nProcessing track: {track.name}")
        original_count = len(track.notes)

        if original_count == 0:
            continue

        # Step 1: Detect and apply chord rolling
        chords = detect_chords(track.notes, tolerance_ticks=5)
        rolled_chords = 0

        for chord in chords:
            if random.random() < settings["chord_roll_probability"]:
                roll_pattern = choose_roll_pattern(chord, settings)
                apply_chord_rolling(chord, chord_roll_ticks, roll_pattern)
                rolled_chords += 1

                print(f"    Applied {roll_pattern} roll to {len(chord)}-note chord")

        print(f"  Rolled {rolled_chords} out of {len(chords)} chords")

        # Step 2: Hand separation and specific humanization
        if settings.get("hand_separation_enabled", False):
            left_hand, right_hand = separate_hands_by_pitch(track.notes)
            print(
                f"  Left hand: {len(left_hand)} notes, Right hand: {len(right_hand)} notes"
            )

            humanize_hand(left_hand, "left", settings)
            humanize_hand(right_hand, "right", settings)

            if settings.get("chord_velocity_correlation", False):
                left_groups = len(
                    [g for g in group_notes_by_timing(left_hand).values() if len(g) > 1]
                )
                right_groups = len(
                    [
                        g
                        for g in group_notes_by_timing(right_hand).values()
                        if len(g) > 1
                    ]
                )
                print(
                    f"  Applied velocity correlation: {left_groups} left hand, {right_groups} right hand chord groups"
                )
        else:
            # Apply basic humanization to all notes
            # First apply timing changes
            for note in track.notes:
                start_offset = random.randint(-noteon_timing_ticks, noteon_timing_ticks)
                note.start = max(0, note.start + start_offset)

                end_offset = random.randint(-noteoff_timing_ticks, noteoff_timing_ticks)
                note.end = note.end + end_offset

                # Ensure minimum duration
                if note.end - note.start < min_duration_ticks:
                    note.end = note.start + min_duration_ticks

            # Then apply velocity changes with correlation and beat accenting
            apply_beat_accenting_and_correlation(track.notes, settings)

            if settings.get("chord_velocity_correlation", False):
                note_groups = group_notes_by_timing(track.notes)
                chord_groups = len([g for g in note_groups.values() if len(g) > 1])
                print(f"  Applied velocity correlation to {chord_groups} chord groups")

        # Step 3: Apply phrase-end ritardando
        phrase_endings = detect_phrase_endings(track.notes)
        if phrase_endings:
            apply_phrase_end_ritardando(track.notes, phrase_endings, settings)
            print(f"  Applied ritardando to {len(phrase_endings)} phrase endings")

        # Step 4: Resolve overlapping notes
        overlap_count = 0
        notes_by_pitch = defaultdict(list)
        for note in track.notes:
            notes_by_pitch[note.pitch].append(note)

        for pitch, notes in notes_by_pitch.items():
            notes.sort(key=lambda n: n.start)
            for i in range(len(notes) - 1):
                current_note = notes[i]
                next_note = notes[i + 1]
                if current_note.end > next_note.start:
                    overlap_count += 1
                    current_note.end = max(
                        current_note.start + min_duration_ticks, next_note.start - 1
                    )

        if overlap_count > 0:
            print(f"  Resolved {overlap_count} overlapping notes")

        print(f"  Processed {original_count} notes")

    return music
