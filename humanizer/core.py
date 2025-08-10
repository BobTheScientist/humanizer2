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
