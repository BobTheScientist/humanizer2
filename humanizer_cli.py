import argparse
import muspy
import random
import os


# Humanization methods and presets
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
                "description": "Very subtle humanization - barely noticeable variations",
            },
            "medium": {
                "velocity_range": 10,
                "noteon_timing_range": 0.01,
                "noteoff_timing_range": 0.005,
                "min_duration_beats": 1 / 32,
                "description": "Moderate humanization - natural musical variations",
            },
            "aggressive": {
                "velocity_range": 20,
                "noteon_timing_range": 0.02,
                "noteoff_timing_range": 0.01,
                "min_duration_beats": 1 / 32,
                "description": "Strong humanization - pronounced expressive variations",
            },
        },
    }
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


def humanize_midi(music, method="basic", preset_name="medium"):
    """
    Apply humanization to a MIDI file using specified method and preset.

    Args:
        music: The muspy.Music object to humanize
        method: The humanization method to use
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

    # Resolve overlapping notes by shortening earlier notes
    print("\nResolving note overlaps...")
    overlap_count = 0

    for track in music.tracks:
        # Sort notes by pitch, then by start time
        notes_by_pitch = {}
        for note in track.notes:
            if note.pitch not in notes_by_pitch:
                notes_by_pitch[note.pitch] = []
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

    return music


def main():
    parser = argparse.ArgumentParser(
        description="Humanize MIDI files to make them sound more natural"
    )

    # Required positional arguments
    parser.add_argument("input_file", help="Input MIDI file")
    parser.add_argument("output_file", help="Output MIDI file")

    # Method and preset options
    parser.add_argument(
        "--method",
        choices=list(HUMANIZATION_METHODS.keys()),
        default="basic",
        help=f"Humanization method. Available: {', '.join(HUMANIZATION_METHODS.keys())}",
    )

    parser.add_argument(
        "--preset", help="Humanization intensity preset (minimal, medium, aggressive)"
    )

    # List presets option
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available methods and presets",
    )

    # Manual parameter overrides
    parser.add_argument(
        "--velocity-range",
        type=int,
        help="Override velocity randomization range (±value, 0-64)",
    )
    parser.add_argument(
        "--timing-range",
        type=float,
        help="Override timing randomization range in beats (±value)",
    )

    # Debugging
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Handle list-presets command
    if args.list_presets:
        print("Available humanization methods and presets:")
        for method_name, method_data in HUMANIZATION_METHODS.items():
            print(f"\nMethod: {method_name}")
            print(f"Description: {method_data['description']}")
            print("Presets:")
            for preset_name, preset_data in method_data["presets"].items():
                print(f"  {preset_name}: {preset_data['description']}")
        return

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return

    # Set default preset if not provided
    method = args.method
    if args.preset:
        preset = args.preset
    else:
        preset = "medium"  # Default preset
        print(f"No preset specified, using default: {preset}")

    # Validate preset exists for the method
    try:
        get_preset_settings(method, preset)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"Loading MIDI file: {args.input_file}")
    try:
        music = muspy.read_midi(args.input_file)
        print(f"Successfully loaded MIDI file")
        print(f"  Tracks: {len(music.tracks)}")
        print(f"  Resolution: {music.resolution} ticks per beat")

        total_notes = sum(len(track.notes) for track in music.tracks)
        print(f"  Total notes: {total_notes}")

        if total_notes == 0:
            print("Warning: No notes found in MIDI file")
            return

    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return

    print(f"\nHumanizing with method '{method}' and preset '{preset}'...")

    try:
        humanized_music = humanize_midi(music, method, preset)

        print(f"\nSaving humanized MIDI file: {args.output_file}")
        muspy.write_midi(args.output_file, humanized_music)
        print("Humanization complete!")

    except Exception as e:
        print(f"Error during humanization: {e}")
        return


if __name__ == "__main__":
    main()
