"""
Advanced piano performance humanization module.

This module provides sophisticated humanization techniques specifically
designed for piano music, including chord rolling with normal distribution,
hand separation, beat accenting, and musical phrasing.
"""

import random
from collections import defaultdict
from .presets import get_preset_settings
from .core import (
    detect_chords,
    separate_hands_by_pitch,
    detect_phrase_endings,
    group_notes_by_timing,
    resolve_overlapping_notes,
)


def apply_chord_rolling_normal_dist(
    chord_notes, mean_timing_ticks, std_timing_ticks, roll_pattern="upward"
):
    """
    Apply rolling effect to a chord using normal distribution for timing variation.

    Args:
        chord_notes: List of notes in the chord
        mean_timing_ticks: Mean time delay between notes in ticks
        std_timing_ticks: Standard deviation for timing variation
        roll_pattern: "upward", "downward", "inside_out", "outside_in"
    """
    if len(chord_notes) < 3:
        return chord_notes

    # Draw from normal distribution for this specific chord's roll intensity
    actual_roll_timing = random.gauss(mean_timing_ticks, std_timing_ticks)
    # Clamp to reasonable bounds (prevent negative or extremely long rolls)
    actual_roll_timing = max(0.2, min(actual_roll_timing, mean_timing_ticks * 6))

    # Sort notes by pitch
    sorted_notes = sorted(chord_notes, key=lambda n: n.pitch)

    if roll_pattern == "upward":
        note_order = sorted_notes
    elif roll_pattern == "downward":
        note_order = sorted_notes[::-1]
    elif roll_pattern == "inside_out":
        # Start from middle notes and work outward
        mid = len(sorted_notes) // 2
        note_order = []
        for i in range(len(sorted_notes)):
            if i % 2 == 0:
                idx = mid + i // 2
            else:
                idx = mid - (i + 1) // 2
            if 0 <= idx < len(sorted_notes):
                note_order.append(sorted_notes[idx])
    elif roll_pattern == "outside_in":
        # Start from outer notes and work inward
        note_order = []
        left, right = 0, len(sorted_notes) - 1
        start_left = True
        while left <= right:
            if start_left:
                note_order.append(sorted_notes[left])
                left += 1
            else:
                note_order.append(sorted_notes[right])
                right -= 1
            start_left = not start_left
    else:
        note_order = sorted_notes

    # Apply timing offsets with the calculated timing
    base_time = min(note.start for note in chord_notes)
    for i, note in enumerate(note_order):
        note.start = base_time + int(i * actual_roll_timing)

    return chord_notes


def choose_roll_pattern(chord_notes, settings):
    """
    Intelligently choose rolling pattern based on chord characteristics.
    """
    chord_span = max(note.pitch for note in chord_notes) - min(
        note.pitch for note in chord_notes
    )

    # Jazz style prefers varied patterns
    if settings.get("jazz_chord_emphasis", False):
        patterns = ["upward", "downward", "inside_out"]
        return random.choice(patterns)

    # Wide chords often roll upward
    if chord_span > 24:  # More than 2 octaves
        return "upward" if random.random() < 0.7 else "downward"

    # Narrow chords can use any pattern
    patterns = ["upward", "downward", "inside_out", "outside_in"]
    return random.choice(patterns)


def calculate_dynamic_roll_probability(base_probability, std_probability=0.02):
    """
    Calculate a varying roll probability using normal distribution.
    This creates sections with more or less rolling tendency.
    """
    actual_probability = random.gauss(base_probability, std_probability)
    # Clamp between 0 and reasonable maximum
    return max(0.0, min(actual_probability, base_probability * 3))


def detect_beat_strength(note, resolution, time_signature=(4, 4)):
    """
    Detect if note is on strong beat, weak beat, or off-beat.
    Returns strength multiplier for velocity.
    """
    beat_ticks = resolution
    beats_per_measure = time_signature[0]

    # Position within the beat (0.0 = exactly on beat, 0.5 = halfway between beats)
    beat_position = (note.start % beat_ticks) / beat_ticks

    # Which beat in the measure (0, 1, 2, 3 for 4/4)
    beat_number = (note.start // beat_ticks) % beats_per_measure

    if beat_position < 0.1:  # Very close to a beat (within 10% of beat)
        if beat_number == 0:  # Downbeat (beat 1)
            return 1.15  # 15% stronger
        elif beat_number == 2:  # Beat 3 in 4/4
            return 1.08  # 8% stronger
        else:  # Beats 2, 4
            return 0.95  # 5% weaker
    else:  # Off-beat
        return 0.88  # 12% weaker


def apply_chord_velocity_correlation(
    chord_notes, base_velocity_offset, internal_variation=4
):
    """
    Apply correlated velocity changes to a chord.
    All notes in the chord get similar velocity adjustment with small internal variation.
    """
    for note in chord_notes:
        # Each note gets the base offset plus small random variation
        individual_offset = base_velocity_offset + random.randint(
            -internal_variation, internal_variation
        )
        note.velocity = max(1, min(127, note.velocity + individual_offset))


def apply_beat_accenting_and_correlation(notes, settings):
    """
    Apply beat-aware velocity changes with chord correlation.
    """
    resolution = settings["resolution"]
    velocity_range = settings["velocity_range"]

    # Group notes by timing for velocity correlation
    note_groups = group_notes_by_timing(notes, timing_tolerance_ticks=10)

    for group_time, group_notes in note_groups.items():
        # Use the first note to determine beat strength
        representative_note = group_notes[0]

        # Calculate base velocity offset for this group
        base_offset = random.randint(-velocity_range, velocity_range)

        # Apply beat accenting if enabled
        if settings.get("beat_accenting", False):
            beat_multiplier = detect_beat_strength(representative_note, resolution)
            base_offset = int(base_offset * beat_multiplier)

        # Apply correlated velocity changes to all notes in this timing group
        if settings.get("chord_velocity_correlation", False) and len(group_notes) > 1:
            apply_chord_velocity_correlation(group_notes, base_offset)
        else:
            # Apply individual velocity changes (old method)
            for note in group_notes:
                individual_offset = random.randint(-velocity_range, velocity_range)
                if settings.get("beat_accenting", False):
                    beat_multiplier = detect_beat_strength(note, resolution)
                    individual_offset = int(individual_offset * beat_multiplier)
                note.velocity = max(1, min(127, note.velocity + individual_offset))


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


def apply_phrase_end_ritardando(notes, phrase_endings, settings):
    """
    Apply subtle ritardando (slowing) at phrase endings.
    """
    resolution = settings["resolution"]

    for phrase_note in phrase_endings:
        # Find notes near the phrase ending
        for note in notes:
            distance = abs(note.start - phrase_note.start)
            if distance < resolution * 2:  # Within 2 beats
                # Apply slight delay for ritardando effect
                delay = random.randint(5, 25)
                note.start += delay


def humanize_midi_advanced(music, method="piano_performance", preset_name="classical"):
    """
    Advanced MIDI humanization with normal distribution chord rolling and musical intelligence.

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
    print(f"  Chord roll base probability: {settings['chord_roll_probability']:.1%}")
    print(
        f"  Chord roll timing: μ={settings['chord_roll_mean_timing']:.4f}, σ={settings['chord_roll_std_timing']:.4f} beats"
    )
    print(f"  Hand separation: {settings.get('hand_separation_enabled', False)}")
    print(f"  Beat accenting: {settings.get('beat_accenting', False)}")
    print(
        f"  Chord velocity correlation: {settings.get('chord_velocity_correlation', False)}"
    )

    # Convert timing ranges to ticks
    noteon_timing_ticks = int(settings["noteon_timing_range"] * music.resolution)
    noteoff_timing_ticks = int(settings["noteoff_timing_range"] * music.resolution)
    min_duration_ticks = int(settings["min_duration_beats"] * music.resolution)

    # Convert normal distribution parameters to ticks
    mean_roll_ticks = settings["chord_roll_mean_timing"] * music.resolution
    std_roll_ticks = settings["chord_roll_std_timing"] * music.resolution

    for track in music.tracks:
        print(f"\nProcessing track: {track.name}")
        original_count = len(track.notes)

        if original_count == 0:
            continue

        # Step 1: Detect and apply chord rolling with normal distribution
        chords = detect_chords(track.notes, tolerance_ticks=5)
        rolled_chords = 0

        for chord in chords:
            # Calculate dynamic probability for this chord
            dynamic_probability = calculate_dynamic_roll_probability(
                settings["chord_roll_probability"],
                settings.get("chord_roll_probability_std", 0.02),
            )

            if random.random() < dynamic_probability:
                roll_pattern = choose_roll_pattern(chord, settings)
                apply_chord_rolling_normal_dist(
                    chord, mean_roll_ticks, std_roll_ticks, roll_pattern
                )
                rolled_chords += 1

                print(
                    f"    Applied {roll_pattern} roll to {len(chord)}-note chord (prob: {dynamic_probability:.1%})"
                )

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
