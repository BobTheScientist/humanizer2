# MIDI Humanizer CLI

This tool takes a MIDI file and applies humanization by randomizing note velocity and timing. Useful for making mechanically generated MIDI sound more like a live performance.

## Usage

```sh
/Users/bubzebub/repos/humanizer2/.venv/bin/python humanizer_cli.py input.mid output.mid [--velocity 10] [--timing 0.01]
```

- `input.mid`: Path to the input MIDI file
- `output.mid`: Path to save the humanized MIDI file
- `--velocity`: Max velocity randomization (+/-), default 10
- `--timing`: Max timing randomization in beats (+/-), default 0.01

## Example

```sh
/Users/bubzebub/repos/humanizer2/.venv/bin/python humanizer_cli.py song.mid song_humanized.mid --velocity 15 --timing 0.02
```

## Requirements
- Python 3.7+
- mido
- python-rtmidi

## Next Steps
- Add accent-aware and ML-based humanization methods.
- Integrate with DAWs as a plugin.
