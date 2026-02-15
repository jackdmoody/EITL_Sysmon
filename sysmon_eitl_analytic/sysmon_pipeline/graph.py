from __future__ import annotations
import pandas as pd

def parent_child_edges(events: pd.DataFrame) -> pd.DataFrame:
    """Compute parent->child edges per unit.

    Uses parent_image and image columns (lowercased if configured).
    Returns: unit_id, edge, count
    """
    ev = events.copy()
    ev = ev.dropna(subset=["image"])
    ev["parent_image"] = ev["parent_image"].fillna("unknown_parent")
    ev["edge"] = ev["parent_image"].astype(str) + " -> " + ev["image"].astype(str)
    edges = ev.groupby(["unit_id","edge"]).size().reset_index(name="count")
    return edges
