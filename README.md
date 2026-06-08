# Robot Pressure Calibration

This project calibrates robot pressure values (Feet and Tank) across 30 slots for two operating modes: **Enter** and **Baffle**. Known data points for slots 16–30 are linearly interpolated to fill missing values, then mirrored around the 15/16 symmetry axis to generate slots 1–15.

## Input files

Each CSV contains slots 16 to 30 with known `Feet` and `Tank` values at specific rows:

| File | Mode |
|---|---|
| `RobotEnterPressureCalibration.csv` | Enter |
| `RobotBafflePressureCalibration.csv` | Baffle |

Columns: `Slot`, `Feet`, `Tank`. Blank cells are treated as missing and will be interpolated.

## Workflow

1. Read the CSV with pandas.
2. Use known `Feet` / `Tank` values to linearly interpolate (with extrapolation) missing values for slots 16–30.
3. Round interpolated values to 1 decimal place.
4. Mirror slots 16–30 in reverse order to produce slots 1–15 (axis between slot 15 and 16).
5. Compute `Diff = Feet - Tank`.
6. Save full table and `.npz` coefficients to `output/`.

## Symmetry

The mirror axis lies between slot 15 and slot 16:
- Slot 1 ↔ 30, Slot 2 ↔ 29, ..., Slot 15 ↔ 16

## Output

`output/` directory contains:

| File | Description |
|---|---|
| `RobotEnterPressureCalibration_full.csv` | Full 1–30 table for Enter mode |
| `RobotBafflePressureCalibration_full.csv` | Full 1–30 table for Baffle mode |
| `RobotEnterPressureCalibration_coef.npz` | Slot/feet/tank arrays for Enter mode |
| `RobotBafflePressureCalibration_coef.npz` | Slot/feet/tank arrays for Baffle mode |
| `robot_calibration_script.py` | Reusable standalone script for arbitrary input CSVs |

## Usage

Run `PressureCalibration.py` to process both modes:
```
python PressureCalibration.py
```

Or use the standalone `robot_calibration_script.py` with your own CSV.
