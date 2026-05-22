import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    DATASET_PATH = DATA_DIR / "india_hospital_dataset.csv"
    RAW_DATASET_PATH = DATA_DIR / "real_india_hospitals_raw.csv"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
