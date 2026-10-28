"""
measure_segments.py

Batch acoustic measurement of labelled segments with Parselmouth (Praat in Python).

For every .wav file in a folder that has a matching .TextGrid file, the script
reads one interval tier, and for each labelled interval it measures:
  - duration (ms)
  - mean intensity (dB)
  - mean F0 (Hz), if the segment is voiced
  - F1, F2, F3 (Hz) at the midpoint of the interval

Results are written to a single CSV file, one row per segment.

Usage:
    python measure_segments.py DATA_FOLDER OUTPUT.csv [--tier 1] [--max-formant 5500]

Use --max-formant 5000 for adult male speakers and 5500 for adult female speakers
(the usual Praat settings).
"""

import argparse
import math
from pathlib import Path

import pandas as pd
import parselmouth
from parselmouth.praat import call


def measure_file(wav_path, textgrid_path, tier, max_formant):
    sound = parselmouth.Sound(str(wav_path))
    textgrid = parselmouth.read(str(textgrid_path))

    # Analysis objects, computed once per file
    pitch = sound.to_pitch()
    intensity = sound.to_intensity()
    formants = sound.to_formant_burg(maximum_formant=max_formant)

    rows = []
    n_intervals = call(textgrid, "Get number of intervals", tier)
    for i in range(1, n_intervals + 1):
        label = call(textgrid, "Get label of interval", tier, i).strip()
        if not label:  # skip unlabelled intervals (silence, etc.)
            continue

        start = call(textgrid, "Get start time of interval", tier, i)
        end = call(textgrid, "Get end time of interval", tier, i)
        mid = (start + end) / 2

        f0 = call(pitch, "Get mean", start, end, "Hertz")
        db = call(intensity, "Get mean", start, end, "energy")

        def formant(n):
            value = formants.get_value_at_time(n, mid)
            return None if value is None or math.isnan(value) else round(value, 1)
        speaker = wav_path.stem.split("_")[0]
        def formant_at(n, proportion):
            t = start + (end - start) * proportion
            value = formants.get_value_at_time(n, t)
            return None if value is None or math.isnan(value) else round(value, 1)
            
        rows.append({
            "file": wav_path.stem,
            "speaker": speaker,"F3_Hz": formant(3),
            "label": label,
            "start_s": round(start, 3),
            "end_s": round(end, 3),
            "duration_ms": round((end - start) * 1000, 1),
            "intensity_dB": None if math.isnan(db) else round(db, 1),
            "f0_Hz": None if math.isnan(f0) else round(f0, 1),
            "F1_Hz": formant(1),
            "F2_Hz": formant(2),
            "F3_Hz": formant(3),
            "F1_25_Hz": formant_at(1, 0.25),
            "F1_75_Hz": formant_at(1, 0.75),
            "F2_25_Hz": formant_at(2, 0.25),
            "F2_75_Hz": formant_at(2, 0.75),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="Batch acoustic measurement with Parselmouth.")
    parser.add_argument("data_folder", help="Folder containing .wav files and matching .TextGrid files")
    parser.add_argument("output_csv", help="Path of the CSV file to write")
    parser.add_argument("--tier", type=int, default=1, help="Interval tier number to read (default: 1)")
    parser.add_argument("--max-formant", type=float, default=5500,
                        help="Maximum formant in Hz (5000 for men, 5500 for women; default 5500)")
    args = parser.parse_args()

    folder = Path(args.data_folder)
    all_rows = []
    for wav in sorted(folder.glob("*.wav")):
        tg = wav.with_suffix(".TextGrid")
        if not tg.exists():
            print(f"Skipping {wav.name}: no matching TextGrid")
            continue
        rows = measure_file(wav, tg, args.tier, args.max_formant)
        print(f"{wav.name}: {len(rows)} segments measured")
        all_rows.extend(rows)

    if not all_rows:
        print("No segments found. Check the folder, file names and tier number.")
        return

    df = pd.DataFrame(all_rows)
    df.to_csv(args.output_csv, index=False)
    print(f"\nSaved {len(df)} rows to {args.output_csv}")
    # Quick summary: mean duration and formants per segment label
    print(df.groupby("label")[["duration_ms", "F1_Hz", "F2_Hz"]].mean().round(1))


if __name__ == "__main__":
    main()
