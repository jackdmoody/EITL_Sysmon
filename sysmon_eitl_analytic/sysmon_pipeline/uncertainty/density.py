from __future__ import annotations
import pandas as pd

def density_uncertainty_placeholder(scores: pd.DataFrame) -> pd.Series:
    """Placeholder for clustering membership uncertainty (HDBSCAN, etc.)."""
    return pd.Series([0.0]*len(scores), index=scores.index)
