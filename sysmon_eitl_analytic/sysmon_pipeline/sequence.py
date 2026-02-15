from __future__ import annotations
import pandas as pd
import numpy as np

def transition_counts(events: pd.DataFrame) -> pd.DataFrame:
    """Compute per-unit transition counts over event_id states.

    For each unit_id, sort by timestamp and count consecutive (prev_event_id -> event_id).
    Returns a dataframe with columns: unit_id, transition, count
    """
    ev = events.copy()
    ev = ev.sort_values(["unit_id","timestamp"])
    ev["prev_event_id"] = ev.groupby("unit_id")["event_id"].shift(1)
    ev = ev.dropna(subset=["prev_event_id","event_id"])
    ev["transition"] = ev["prev_event_id"].astype(str) + "->" + ev["event_id"].astype(str)
    tc = ev.groupby(["unit_id","transition"]).size().reset_index(name="count")
    return tc

def transition_distribution(tc: pd.DataFrame) -> pd.DataFrame:
    """Compute per-unit transition probability distribution."""
    total = tc.groupby("unit_id")["count"].sum().rename("total")
    out = tc.merge(total, on="unit_id", how="left")
    out["p"] = out["count"] / out["total"].replace(0, np.nan)
    out["p"] = out["p"].fillna(0.0)
    return out[["unit_id","transition","p","count"]]
