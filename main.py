import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def fit_from_csv(csv_file, degree=2):
    df = pd.read_csv(csv_file)

    # 確保欄位名稱正確
    df.columns = [c.strip() for c in df.columns]

    # 轉成數值，空白會變成 NaN
    df["Slot"] = pd.to_numeric(df["Slot"], errors="coerce")
    df["Feet"] = pd.to_numeric(df["Feet"], errors="coerce")
    df["Tank"] = pd.to_numeric(df["Tank"], errors="coerce")

    # 分別取有值的點來擬合
    feet_df = df.dropna(subset=["Slot", "Feet"])
    tank_df = df.dropna(subset=["Slot", "Tank"])

    coef_feet = np.polyfit(feet_df["Slot"], feet_df["Feet"], degree)
    coef_tank = np.polyfit(tank_df["Slot"], tank_df["Tank"], degree)

    return df, coef_feet, coef_tank

def save_model(filename, coef_feet, coef_tank):
    np.savez(filename, coef_feet=coef_feet, coef_tank=coef_tank)

def load_model(filename):
    data = np.load(filename)
    return data["coef_feet"], data["coef_tank"]

def predict_to_dataframe(df, coef_feet, coef_tank):
    out = df.copy()

    slots = out["Slot"].to_numpy(dtype=float)

    feet_pred = np.polyval(coef_feet, slots)
    tank_pred = np.polyval(coef_tank, slots)

    out["Feet_Fit"] = feet_pred
    out["Tank_Fit"] = tank_pred

    # 若原本為空，就補上擬合值；若原本已有值，就保留原值
    out["Feet_Final"] = out["Feet"].fillna(out["Feet_Fit"])
    out["Tank_Final"] = out["Tank"].fillna(out["Tank_Fit"])

    return out

def plot_result(df, coef_feet, coef_tank):
    slots = df["Slot"].to_numpy(dtype=float)

    feet_fit = np.polyval(coef_feet, slots)
    tank_fit = np.polyval(coef_tank, slots)

    feet_df = df.dropna(subset=["Feet"])
    tank_df = df.dropna(subset=["Tank"])

    plt.figure(figsize=(10, 6))

    plt.plot(slots, feet_fit, 'o-', label='Feet fit')
    plt.plot(slots, tank_fit, 's-', label='Tank fit')

    plt.scatter(feet_df["Slot"], feet_df["Feet"], label='Feet data', zorder=5)
    plt.scatter(tank_df["Slot"], tank_df["Tank"], label='Tank data', zorder=5)

    plt.xlabel("Slot")
    plt.ylabel("Value")
    plt.title("Robot Pressure Calibration")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

# ===== main =====
csv_file = "RobotPressureCalibration.csv"

df, coef_feet, coef_tank = fit_from_csv(csv_file, degree=2)

print("Feet coef:", coef_feet)
print("Tank coef:", coef_tank)

save_model("robot_coef.npz", coef_feet, coef_tank)

coef_feet, coef_tank = load_model("robot_coef.npz")

result_df = predict_to_dataframe(df, coef_feet, coef_tank)

print(result_df[["Slot", "Feet", "Tank", "Feet_Final", "Tank_Final"]])

result_df.to_csv("RobotPressureCalibration_filled.csv", index=False)

plot_result(df, coef_feet, coef_tank)