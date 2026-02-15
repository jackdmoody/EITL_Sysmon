from __future__ import annotations
from pathlib import Path
import pandas as pd

def read_labels(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=["unit_id","label","reason_code"])
    return pd.read_csv(path)

def write_labels(path: str | Path, labels: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    labels.to_csv(path, index=False)
