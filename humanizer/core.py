"""
Core utilities for MIDI humanization.

This module contains common functions used by different humanization methods,
including chord detection, timing utilities, and musical analysis functions.
"""

import random
from collections import defaultdict


def detect_chords(notes, tolerance_ticks=10):
    """
    Detect simultaneous notes (chords) within a timing tolerance.
    Returns a list of chord groups.
    """
    # Group notes by start time (with tolerance)
    note_groups = defaultdict(list)

    for note in notes:
        # Find if this note belongs to an existing group
        found_group = False
        for start_time in note_groups.keys():
            if abs(note.start - start_time) <= tolerance_ticks:
                note_groups[start_time].append(note)
                found_group = True
                break

        if not found_group:
            note_groups[note.start].append(note)

    # Return only groups with 3+ notes (actual chords)
    chords = [group for group in note_groups.values() if len(group) >= 3]
    return chords


def apply_chord_rolling(chord_notes, roll_timing_ticks, roll_pattern="upward"):
    """
    Apply rolling effect to a chord.

    Args:
        chord_notes: List of notes in the chord
        roll_timing_ticks: Time delay between notes in ticks
        roll_pattern: "upward", "downward", "inside_out", "outside_in"
    """
    if len(chord_notes) < 3:
        return chord_notes

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

    # Apply timing offsets
    base_time = min(note.start for note in chord_notes)
    for i, note in enumerate(note_order):
        note.start = base_time + (i * roll_timing_ticks)

    return chord_notes


def separate_hands_by_pitch(notes, split_point=60):
    """
    Separate notes into left and right hand based on pitch.
    Default split at middle C (MIDI note 60).
    """
    left_hand = []
    right_hand = []

    for note in notes:
        if note.pitch < split_point:
            left_hand.append(note)
        else:
            right_hand.append(note)

    return left_hand, right_hand


def detect_phrase_endings(notes, min_duration_ticks=480):
    """
    Simple phrase ending detection based on note duration.
    Notes longer than min_duration_ticks are likely phrase endings.
    """
    phrase_endings = []
    for note in notes:
        duration = note.end - note.start
        if duration >= min_duration_ticks:
            phrase_endings.append(note)
    return phrase_endings


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


def group_notes_by_timing(notes, timing_tolerance_ticks=10):
    """
    Group notes that occur at roughly the same time (for velocity correlation).
    Returns dict of {timing: [notes]} where timing is representative start time.
    """
    groups = defaultdict(list)

    for note in notes:
        # Find existing group within tolerance
        found_group = False
        for group_time in groups.keys():
            if abs(note.start - group_time) <= timing_tolerance_ticks:
                groups[group_time].append(note)
                found_group = True
                break

        if not found_group:
            groups[note.start].append(note)

    return groups


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


def resolve_overlapping_notes(music, min_duration_ticks):
    """
    Resolve overlapping notes by shortening earlier notes.
    This is a common utility used by all humanization methods.
    """
    print("Resolving note overlaps...")
    overlap_count = 0

    for track in music.tracks:
        # Sort notes by pitch, then by start time
        notes_by_pitch = defaultdict(list)
        for note in track.notes:
            notes_by_pitch[note.pitch].append(note)

        for pitch, notes in notes_by_pitch.items():
            notes.sort(key=lambda n: n.start)

            for i in range(len(notes) - 1):
                current_note = notes[i]
                next_note = notes[i + 1]

                # If current note overlaps with next note
                if current_note.end > next_note.start:
                    overlap_count += 1
                    # Shorten current note to end just before next note starts
                    current_note.end = max(
                        current_note.start + min_duration_ticks, next_note.start - 1
                    )

    print(f"Resolved {overlap_count} overlapping notes")
    return overlap_count
