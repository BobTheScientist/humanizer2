import muspy
import sys


def analyze_muspy(file_path):
    """Analyze MIDI file using muspy"""
    try:
        # Load the MIDI file
        music = muspy.read_midi(file_path)

        print(f"File: {file_path}")
        print(f"Resolution: {music.resolution} ticks per beat")
        print(f"Tempos: {len(music.tempos)}")
        print(f"Key signatures: {len(music.key_signatures)}")
        print(f"Time signatures: {len(music.time_signatures)}")
        print(f"Tracks: {len(music.tracks)}")
        print()

        # Show notes from each track
        for i, track in enumerate(music.tracks):
            print(f"Track {i}: {track.name if track.name else 'Unnamed'}")
            print(f"  Program: {track.program}, Is drum: {track.is_drum}")
            print(f"  Notes: {len(track.notes)}")

            if track.notes:
                print("  Note details:")
                print("    #   Start     End       Duration  Pitch  Vel  Note")
                print("    " + "-" * 55)

                for j, note in enumerate(track.notes[:20]):  # Show first 20 notes
                    duration = note.end - note.start
                    # Simple note name conversion
                    note_names = [
                        "C",
                        "C#",
                        "D",
                        "D#",
                        "E",
                        "F",
                        "F#",
                        "G",
                        "G#",
                        "A",
                        "A#",
                        "B",
                    ]
                    octave = (note.pitch // 12) - 1
                    note_name = note_names[note.pitch % 12] + str(octave)
                    print(
                        f"    {j:2d}  {note.start:8d}  {note.end:8d}  {duration:8d}  {note.pitch:3d}  {note.velocity:3d}  {note_name}"
                    )

                if len(track.notes) > 20:
                    print(f"    ... and {len(track.notes) - 20} more notes")

                # Look for E4 notes specifically
                e4_notes = [n for n in track.notes if n.pitch == 64]
                print(f"\n  E4 notes in this track: {len(e4_notes)}")
                for j, note in enumerate(e4_notes):
                    duration = note.end - note.start
                    print(
                        f"    E4 #{j+1}: start {note.start:8d}, end {note.end:8d}, duration {duration:8d}, vel {note.velocity}"
                    )

            print()

    except Exception as e:
        print(f"Error reading MIDI file with muspy: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python muspy_analyzer.py <midi_file>")
        sys.exit(1)

    analyze_muspy(sys.argv[1])
