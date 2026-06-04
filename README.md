# Robot Pressure Calibration README

This project reads a calibration CSV, fits `Feet` and `Tank` values from the known points, completes slots 16 to 30, and mirrors them around the 15/16 axis to generate slots 1 to 30.

## CSV format

The input file uses three columns: `Slot`, `Feet`, and `Tank`. Blank `Feet` or `Tank` cells are treated as missing values that will be estimated from the fitted curve.

Example:

```csv
Slot,Feet,Tank
16,,
17,,
18,,
19,4,6.5
20,4,6.5
21,,
22,,
23,4,5.5
24,,
25,,
26,4.5,4
27,4.5,4
28,,
29,,
30,,
```

## Symmetry rule

The circle is mirrored around the boundary between slot 15 and slot 16, so slot 30 is next to slot 1 and slot 15 is next to slot 16. The mapping is `30 ↔ 1`, `29 ↔ 2`, ..., `16 ↔ 15`.

Mirror formula:

$$
\text{mirror\_slot} = 31 - \text{slot}
$$

## Workflow

1. Load the CSV with pandas.
2. Use the rows that already contain numeric `Feet` and `Tank` values to fit quadratic coefficients.
3. Generate completed values for slots 16 to 30 from the fitted curves.
4. Mirror those values across the 15/16 axis to build the full slot 1 to 30 table.
5. Save the coefficients to `robot_coef.npz` and export the completed table as CSV.

## Output

- `robot_coef.npz`: saved coefficients for reuse.
- `RobotPressureCalibration_1_to_30_mirror_15_16.csv`: completed slot table from 1 to 30.

## Notes

The result quality depends on how many known calibration points exist in the source CSV. If more real points are added later, rerunning the process will produce a better fitted table.