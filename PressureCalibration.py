import numpy as np, pandas as pd
from scipy.interpolate import interp1d
from pathlib import Path

# Reload original input
orig = pd.read_csv('RobotPressureCalibration.csv')
orig['Feet'] = pd.to_numeric(orig['Feet'], errors='coerce')
orig['Tank'] = pd.to_numeric(orig['Tank'], errors='coerce')

slots = orig['Slot'].to_numpy(dtype=int)
feet = orig['Feet'].to_numpy(dtype=float)
tank = orig['Tank'].to_numpy(dtype=float)

# Interpolate missing values in 16~30
kf = ~np.isnan(feet)
kt = ~np.isnan(tank)
feet_i = interp1d(slots[kf], feet[kf], kind='linear', fill_value='extrapolate')
tank_i = interp1d(slots[kt], tank[kt], kind='linear', fill_value='extrapolate')
feet_f = feet.copy(); tank_f = tank.copy()
feet_f[np.isnan(feet_f)] = feet_i(slots[np.isnan(feet_f)])
tank_f[np.isnan(tank_f)] = tank_i(slots[np.isnan(tank_f)])
feet_f = np.round(feet_f, 1)
tank_f = np.round(tank_f, 1)

# Mirror axis between 15 and 16: slot 15 mirrors 16, 14 mirrors 17, ..., 1 mirrors 30
# So full slots 1..30 are: [30..16, 16..30]?? No duplication at 16/15 axis means left side 1..15 = reverse of 16..30
left_slots = np.arange(1, 16)
right_slots = np.arange(16, 31)
# left values correspond to right side slots 30..16 in reverse order when paired by mirror axis
left_feet = feet_f[::-1]
left_tank = tank_f[::-1]
full_slots = np.arange(1, 31)
full_feet = np.concatenate([left_feet, feet_f])
full_tank = np.concatenate([left_tank, tank_f])
diff = full_feet - full_tank
full = pd.DataFrame({'Slot': full_slots, 'Feet': full_feet, 'Tank': full_tank, 'Diff': diff})

output_dir = Path('output')
output_dir.mkdir(exist_ok=True)
np.savez('output/robot_coef.npz', slot=full_slots, feet=full_feet, tank=full_tank)
full.to_csv('output/RobotPressureCalibration_full.csv', index=False)

# Update script
script = '''import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

input_csv = "RobotPressureCalibration-2.csv"
out_npz = "robot_coef.npz"
out_csv = "RobotPressureCalibration_full.csv"

df = pd.read_csv(input_csv)
df['Feet'] = pd.to_numeric(df['Feet'], errors='coerce')
df['Tank'] = pd.to_numeric(df['Tank'], errors='coerce')

slots = df['Slot'].to_numpy(dtype=int)
feet = df['Feet'].to_numpy(dtype=float)
tank = df['Tank'].to_numpy(dtype=float)

known_feet = ~np.isnan(feet)
known_tank = ~np.isnan(tank)

feet_interp = interp1d(slots[known_feet], feet[known_feet], kind='linear', fill_value='extrapolate')
tank_interp = interp1d(slots[known_tank], tank[known_tank], kind='linear', fill_value='extrapolate')

feet_filled = feet.copy()
tank_filled = tank.copy()
feet_filled[np.isnan(feet_filled)] = feet_interp(slots[np.isnan(feet_filled)])
tank_filled[np.isnan(tank_filled)] = tank_interp(slots[np.isnan(tank_filled)])

feet_filled = np.round(feet_filled, 1)
tank_filled = np.round(tank_filled, 1)

# Symmetry axis is between slot 15 and 16:
# 15 mirrors 16, 14 mirrors 17, ..., 1 mirrors 30.
full_slots = np.arange(1, 31)
full_feet = np.concatenate([feet_filled[::-1], feet_filled])
full_tank = np.concatenate([tank_filled[::-1], tank_filled])

full_df = pd.DataFrame({'Slot': full_slots, 'Feet': full_feet, 'Tank': full_tank})
np.savez(out_npz, slot=full_slots, feet=full_feet, tank=full_tank)
full_df.to_csv(out_csv, index=False)
'''
with open('output/robot_calibration_script.py', 'w', encoding='utf-8') as f:
    f.write(script)

