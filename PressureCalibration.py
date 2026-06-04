import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def fit_from_csv(csv_file, degree=2):
    df = pd.read_csv(csv_file)
    df.columns = [c.strip() for c in df.columns]

    df["Slot"] = pd.to_numeric(df["Slot"], errors="coerce")
    df["Feet"] = pd.to_numeric(df["Feet"], errors="coerce")
    df["Tank"] = pd.to_numeric(df["Tank"], errors="coerce")

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

def build_slots_16_30(df, coef_feet, coef_tank):
    slots = np.arange(16, 31)

    out = pd.DataFrame({"Slot": slots})
    out["Feet_Fit"] = np.polyval(coef_feet, slots)
    out["Tank_Fit"] = np.polyval(coef_tank, slots)

    raw_map = df.set_index("Slot")[["Feet", "Tank"]]
    out["Feet_Raw"] = out["Slot"].map(raw_map["Feet"])
    out["Tank_Raw"] = out["Slot"].map(raw_map["Tank"])

    out["Feet_Final"] = out["Feet_Raw"].fillna(out["Feet_Fit"])
    out["Tank_Final"] = out["Tank_Raw"].fillna(out["Tank_Fit"])

    return out

def mirror_around_15_16(df_16_30):
    rows = []

    # 先產生 1~15，從 30~16 鏡射過來
    for s in range(1, 16):
        source_slot = 31 - s   # 1<-30, 2<-29, ..., 15<-16
        source_row = df_16_30[df_16_30["Slot"] == source_slot].iloc[0]

        rows.append({
            "Slot": s,
            "MirrorFrom": source_slot,
            "Feet_Final": source_row["Feet_Final"],
            "Tank_Final": source_row["Tank_Final"]
        })

    # 再加入 16~30 原本區段
    for _, row in df_16_30.iterrows():
        rows.append({
            "Slot": int(row["Slot"]),
            "MirrorFrom": int(row["Slot"]),
            "Feet_Final": row["Feet_Final"],
            "Tank_Final": row["Tank_Final"]
        })

    result = pd.DataFrame(rows).sort_values("Slot").reset_index(drop=True)
    return result

def plot_result(df_1_30, raw_df=None):
    plt.figure(figsize=(11, 6))

    plt.plot(df_1_30["Slot"], df_1_30["Feet_Final"], 'o-', label="Feet")
    plt.plot(df_1_30["Slot"], df_1_30["Tank_Final"], 's-', label="Tank")

    if raw_df is not None:
        raw_feet = raw_df.dropna(subset=["Feet"])
        raw_tank = raw_df.dropna(subset=["Tank"])
        plt.scatter(raw_feet["Slot"], raw_feet["Feet"], label="Feet raw", zorder=5)
        plt.scatter(raw_tank["Slot"], raw_tank["Tank"], label="Tank raw", zorder=5)

    plt.xlabel("Slot")
    plt.ylabel("Value")
    plt.title("Robot Pressure Calibration (Mirror around 15/16)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

# ===== main =====
csv_file = "RobotPressureCalibration.csv"

# 1. 從 CSV 擬合 16~30
raw_df, coef_feet, coef_tank = fit_from_csv(csv_file, degree=2)

# 2. 儲存 / 載入係數
save_model("robot_coef.npz", coef_feet, coef_tank)
coef_feet, coef_tank = load_model("robot_coef.npz")

# 3. 生成 16~30
df_16_30 = build_slots_16_30(raw_df, coef_feet, coef_tank)

# 4. 以 15/16 為中心鏡射成 1~30
df_1_30 = mirror_around_15_16(df_16_30)

# 5. 輸出
df_1_30.to_csv("RobotPressureCalibration_1_to_30_mirror_15_16.csv", index=False)

print(df_1_30)

# 6. 畫圖
plot_result(df_1_30, raw_df)