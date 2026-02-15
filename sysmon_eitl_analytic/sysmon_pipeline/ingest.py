from __future__ import annotations
from pathlib import Path
import pandas as pd

def read_input(path: str | Path, cfg: dict) -> pd.DataFrame:
    """Read raw Sysmon export data."""
    fmt = cfg["ingest"].get("input_format", "csv").lower()
    path = Path(path)
    if fmt == "csv":
        return pd.read_csv(path)
    if fmt == "parquet":
        return pd.read_parquet(path)
    if fmt == "jsonl":
        return pd.read_json(path, lines=True)
    raise ValueError(f"Unsupported input_format: {fmt}")
