import random
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "data" / "india_hospital_dataset.csv"

states_cities = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Karnataka": ["Bengaluru", "Mysuru"],
    "Tamil Nadu": ["Chennai", "Coimbatore"],
    "Delhi": ["New Delhi"],
    "Gujarat": ["Ahmedabad", "Surat"],
}

def main():
    rows = []
    hospital_id = 1

    for state, cities in states_cities.items():
        for city in cities:
            for _ in range(120):
                total_beds = random.randint(50, 1000)

                row = {
                    "hospital_id": hospital_id,
                    "hospital_name": f"{city} Hospital {hospital_id}",
                    "state": state,
                    "district": city,
                    "city": city,
                    "latitude": round(random.uniform(8.0, 28.0), 6),
                    "longitude": round(random.uniform(68.0, 88.0), 6),
                    "ownership_type": random.choice(["Government", "Private"]),
                    "hospital_level": random.choice(["Primary", "Secondary", "Tertiary"]),
                    "total_beds": total_beds,
                    "icu_beds": random.randint(5, int(total_beds * 0.2)),
                    "ventilators": random.randint(2, int(total_beds * 0.1)),
                    "cardiac_unit": random.choice(["Yes", "No"]),
                    "trauma_unit": random.choice(["Yes", "No"]),
                    "burn_unit": random.choice(["Yes", "No"]),
                    "current_icu_load_percent": random.randint(30, 95),
                    "emergency_load_score": round(random.uniform(0.1, 1.0), 2),
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }

                rows.append(row)
                hospital_id += 1

    df = pd.DataFrame(rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Dataset created at {OUTPUT_FILE}: {df.shape}")


if __name__ == "__main__":
    main()
