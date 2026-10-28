# Batch acoustic measurement with Parselmouth

A Python script that automates acoustic measurements I previously made by hand in Praat for my MA thesis on sonorants in Bangla and Bishnupriya Manipuri.

For every `.wav` file with a matching Praat `.TextGrid`, the script reads one interval tier and, for each labelled segment, measures:

- duration (ms)
- mean intensity (dB)
- mean F0 (Hz)
- F1, F2 and F3 (Hz) at the segment midpoint
- F1 and F2 at 25% and 75% of each segment, to capture formant movement
- a speaker column, taken from the file name


All results are written to one CSV file, ready for analysis in SPSS, R or Python.

## Setup

```
pip install -r requirements.txt
```

## Usage

```
python measure_segments.py DATA_FOLDER OUTPUT.csv --tier 1 --max-formant 5000
```

- `DATA_FOLDER`: folder with `.wav` files and `.TextGrid` files of the same name
- `--tier`: the interval tier containing the segment labels (default 1)
- `--max-formant`: 5000 Hz for adult male speakers, 5500 Hz for adult female speakers (Praat's usual settings)

Example with the included synthetic test file:

```
python measure_segments.py sample_data sample_output.csv
```

## Method

Measurements use Praat's algorithms through [Parselmouth](https://parselmouth.readthedocs.io/): Burg formant analysis, Praat's default pitch tracking, and energy-averaged intensity. Unlabelled intervals are skipped.

## Data

The field recordings from my thesis are not included, to protect speakers' privacy. `sample_data/` contains only a synthetic test signal.

## Author

Sulthana Sume, MA in Linguistics, University of Dhaka
