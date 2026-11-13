"""FinWiseIQ retrieval: load the Q&A CSV, embed it, and find the top matches."""
from functools import lru_cache
from pathlib import Path

import pandas as pd
from sentence_transformers import SentenceTransformer

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample.csv"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 3
THRESHOLD = 0.5  # placeholder - calibrate with real data (KAN-18)
COLUMNS = ["id", "category", "question", "answer",
           "source", "source_section", "last_reviewed"]


def load_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the CSV, check the columns, and drop empty rows."""
    df = pd.read_csv(path)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    df = df.dropna(subset=["question", "answer"])
    df["question"] = df["question"].str.strip()
    df["answer"] = df["answer"].str.strip()
    df = df[(df["question"] != "") & (df["answer"] != "")]
    return df.reset_index(drop=True)
