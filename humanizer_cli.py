#!/usr/bin/env python3
"""
MIDI Humanizer CLI - Make MIDI files sound more human-like.

This tool applies various humanization techniques to MIDI files to make them
sound more natural and less mechanical. It supports multiple methods and
intensity presets.
"""

import warnings

# Suppress the pkg_resources deprecation warning from pretty_midi/muspy
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")

import argparse
import muspy
import os

# Import humanization modules
from humanizer import (
    HUMANIZATION_METHODS,
    get_preset_settings,
    humanize_midi_basic,
    humanize_midi_advanced,
)


def main():
    parser = argparse.ArgumentParser(
        description="Humanize MIDI files to make them sound more natural"
    )

    # List presets option (check this first)
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available methods and presets",
    )

    # Required positional arguments (only when not listing presets)
    parser.add_argument("input_file", nargs="?", help="Input MIDI file")
    parser.add_argument("output_file", nargs="?", help="Output MIDI file")

    # Method and preset options
    parser.add_argument(
        "--method",
        choices=list(HUMANIZATION_METHODS.keys()),
        default="basic",
        help=f"Humanization method. Available: {', '.join(HUMANIZATION_METHODS.keys())}",
    )

    parser.add_argument(
        "--preset",
        help="Humanization intensity preset (minimal, medium, aggressive) or style preset (classical, romantic, jazz)",
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
    parser.add_argument(
        "--roll-probability",
        type=float,
        help="Override chord roll probability (0.0-1.0, piano_performance method only)",
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

    # Check required arguments for processing
    if not args.input_file or not args.output_file:
        parser.error(
            "input_file and output_file are required when not using --list-presets"
        )

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return

    # Set default preset if not provided
    method = args.method
    if args.preset:
        preset = args.preset
    else:
        # Set sensible defaults based on method
        if method == "basic":
            preset = "medium"
        elif method == "piano_performance":
            preset = "classical"
        else:
            preset = "medium"
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
        # Choose appropriate humanization function based on method
        if method == "piano_performance":
            humanized_music = humanize_midi_advanced(music, method, preset)
        else:  # basic and any future simple methods
            humanized_music = humanize_midi_basic(music, method, preset)

        print(f"\nSaving humanized MIDI file: {args.output_file}")
        muspy.write_midi(args.output_file, humanized_music)
        print("Humanization complete!")

    except Exception as e:
        print(f"Error during humanization: {e}")
        return


if __name__ == "__main__":
    main()
