from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "hospital_name",
    "state",
    "district",
    "city",
    "latitude",
    "longitude",
    "hospital_level",
    "icu_beds",
    "current_icu_load_percent",
    "cardiac_unit",
    "trauma_unit",
    "burn_unit"
}


def load_hospitals(path):
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    df = pd.read_csv(dataset_path)

    if df.empty:
        raise ValueError("Hospital dataset is empty")

    missing_columns = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        raise ValueError(
            "Hospital dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    # Normalize text fields for matching and avoid accidental "nan" lookups.
    for column in ("city", "state", "district", "hospital_name"):
        df[column] = df[column].fillna("").astype(str).str.strip()

    df["city"] = df["city"].str.lower()
    df["state"] = df["state"].str.lower()

    return df


def filter_by_city(df, city):
    normalized_city = city.strip().lower()

    if not normalized_city:
        return df.iloc[0:0]

    filtered = df[df["city"].str.contains(normalized_city, na=False, regex=False)]

    return filtered
