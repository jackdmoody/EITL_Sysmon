from __future__ import annotations
import pandas as pd
import numpy as np

def margin_uncertainty(R: pd.Series, center: float = 0.5) -> pd.Series:
    """High uncertainty near center; low at extremes."""
    dist = (R.astype(float) - float(center)).abs()
    u = 1.0 - (dist / (max(center, 1-center) + 1e-9))
    return u.clip(0,1)
