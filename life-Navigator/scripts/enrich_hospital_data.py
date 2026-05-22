import random
from datetime import datetime
from pathlib import Path

import pandas as pd

# -----------------------------
# LOAD REAL HOSPITAL DATA
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "real_india_hospitals_raw.csv"
OUTPUT_FILE = BASE_DIR / "data" / "india_hospital_dataset.csv"

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def assign_hospital_level():
    return random.choices(
        ["Primary", "Secondary", "Tertiary"],
        weights=[0.4, 0.35, 0.25]
    )[0]

def estimate_beds(level):
    if level == "Primary":
        return random.randint(30, 100)
    if level == "Secondary":
        return random.randint(100, 400)
    return random.randint(400, 1200)

def estimate_icu_beds(total_beds, level):
    if level == "Primary":
        return int(total_beds * random.uniform(0.02, 0.05))
    if level == "Secondary":
        return int(total_beds * random.uniform(0.08, 0.12))
    return int(total_beds * random.uniform(0.15, 0.25))

# -----------------------------
# ENRICH DATA
# -----------------------------
def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Raw hospital dataset not found at {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    print("Loaded real hospitals:", df.shape)

    enriched_rows = []

    for _, row in df.iterrows():
        level = assign_hospital_level()
        total_beds = estimate_beds(level)
        icu_beds = estimate_icu_beds(total_beds, level)
        ventilators = int(icu_beds * random.uniform(0.6, 0.85))

        enriched_rows.append({
            "hospital_id": row["hospital_id"],
            "hospital_name": row["hospital_name"],
            "state": row["state"],
            "district": row["district"],
            "city": row["city"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "ownership_type": random.choice(["Government", "Private", "Trust"]),
            "hospital_level": level,
            "total_beds": total_beds,
            "icu_beds": icu_beds,
            "ventilators": ventilators,
            "cardiac_unit": random.choice(["Yes", "No"]),
            "trauma_unit": random.choice(["Yes", "No"]),
            "burn_unit": random.choice(["Yes", "No"]),
            "current_icu_load_percent": random.randint(30, 95),
            "emergency_load_score": round(random.uniform(0.1, 1.0), 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        })

    final_df = pd.DataFrame(enriched_rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUTPUT_FILE, index=False)

    print(f"Final enriched dataset saved at {OUTPUT_FILE}: {final_df.shape}")


if __name__ == "__main__":
    main()
