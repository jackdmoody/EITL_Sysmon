from __future__ import annotations
import pandas as pd
import numpy as np

def variance_disagreement(scores: pd.DataFrame) -> pd.Series:
    """Compute disagreement as variance across subscores."""
    cols = ["subscore_drift","subscore_outlier","subscore_rules","subscore_graph"]
    X = scores[cols].astype(float)
    v = X.var(axis=1)
    v = (v - v.min()) / (v.max() - v.min() + 1e-9)
    return v
