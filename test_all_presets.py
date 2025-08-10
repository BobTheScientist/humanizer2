#!/usr/bin/env python3
"""
Test script to generate humanized MIDI files using all available methods and presets.
This script takes an input MIDI file and creates output files for every combination
of humanization method and preset.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_available_options():
    """Get all available methods and presets by running the humanizer with --list-presets"""
    try:
        result = subprocess.run(
            [sys.executable, "humanizer_cli.py", "--list-presets"],
            capture_output=True,
            text=True,
            check=True,
        )

        methods = {}
        current_method = None

        for line in result.stdout.split("\n"):
            line = line.strip()
            if line.startswith("Method: "):
                current_method = line.replace("Method: ", "")
                methods[current_method] = []
            elif (
                line
                and current_method
                and ":" in line
                and not line.startswith("Description")
                and not line.startswith("Presets:")
            ):
                preset_name = line.split(":")[0].strip()
                if preset_name:  # Make sure it's not empty
                    methods[current_method].append(preset_name)

        return methods
    except subprocess.CalledProcessError as e:
        print(f"Error getting available options: {e}")
        return {}


def create_output_filename(input_file, method, preset, output_dir):
    """Create a descriptive output filename"""
    input_path = Path(input_file)
    stem = input_path.stem
    extension = input_path.suffix

    output_filename = f"{stem}_{method}_{preset}{extension}"
    return os.path.join(output_dir, output_filename)


def run_humanization(input_file, output_file, method, preset):
    """Run the humanizer with specified method and preset"""
    cmd = [
        sys.executable,
        "humanizer_cli.py",
        input_file,
        output_file,
        "--method",
        method,
        "--preset",
        preset,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def main():
    parser = argparse.ArgumentParser(
        description="Generate humanized MIDI files using all available methods and presets"
    )

    parser.add_argument("input_file", help="Input MIDI file to humanize")
    parser.add_argument(
        "--output-dir",
        default="test_outputs",
        help="Directory to save output files (default: test_outputs)",
    )
    parser.add_argument("--method", help="Only test a specific method (optional)")
    parser.add_argument(
        "--preset", help="Only test a specific preset (optional, requires --method)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output from each humanization",
    )

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        return 1

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Output directory: {args.output_dir}")

    # Get available options
    print("Getting available humanization options...")
    methods = get_available_options()

    if not methods:
        print("Error: Could not retrieve available methods and presets")
        return 1

    # Filter methods/presets if specified
    if args.method:
        if args.method not in methods:
            print(
                f"Error: Method '{args.method}' not found. Available: {list(methods.keys())}"
            )
            return 1
        methods = {args.method: methods[args.method]}

        if args.preset:
            if args.preset not in methods[args.method]:
                print(
                    f"Error: Preset '{args.preset}' not found for method '{args.method}'. Available: {methods[args.method]}"
                )
                return 1
            methods[args.method] = [args.preset]

    # Count total combinations
    total_combinations = sum(len(presets) for presets in methods.values())
    print(
        f"Will generate {total_combinations} humanized versions of '{args.input_file}'"
    )
    print()

    # Generate files for each combination
    successful = 0
    failed = 0

    for method, presets in methods.items():
        print(f"Method: {method}")

        for preset in presets:
            output_file = create_output_filename(
                args.input_file, method, preset, args.output_dir
            )
            print(f"  Preset: {preset} -> {os.path.basename(output_file)}")

            success, output = run_humanization(
                args.input_file, output_file, method, preset
            )

            if success:
                successful += 1
                if args.verbose:
                    print(f"    ✓ Success")
                    # Show just the key info from the output
                    lines = output.split("\n")
                    for line in lines:
                        if (
                            "Applying" in line
                            or "Velocity range" in line
                            or "Processed" in line
                            or "Resolved" in line
                        ):
                            print(f"      {line.strip()}")
            else:
                failed += 1
                print(f"    ✗ Failed: {output}")

        print()

    # Summary
    print("=" * 50)
    print(f"Test Summary:")
    print(f"  Input file: {args.input_file}")
    print(f"  Output directory: {args.output_dir}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {total_combinations}")

    if successful > 0:
        print(f"\nGenerated files:")
        for file in sorted(os.listdir(args.output_dir)):
            if file.endswith(".mid"):
                file_path = os.path.join(args.output_dir, file)
                size = os.path.getsize(file_path)
                print(f"  {file} ({size:,} bytes)")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
