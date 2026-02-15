from __future__ import annotations
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def compute_outlier_scores(features: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Fit Isolation Forest on features and return normalized outlier score.

    Note: This is unsupervised and fits on the provided run's data.
    For production, fit on historical baseline and score forward.
    """
    cols = ["log_event_count","log_unique_images","log_net_touches","avg_event_severity","unique_users"]
    X = features[cols].astype(float).values
    model = IsolationForest(
        n_estimators=int(params.get("n_estimators", 200)),
        max_samples=params.get("max_samples", 0.75),
        contamination=params.get("contamination", "auto"),
        random_state=int(params.get("random_state", 42)),
    )
    model.fit(X)
    # decision_function: higher is more normal. We invert.
    s = -model.decision_function(X)
    # normalize to 0-1
    s = (s - s.min()) / (s.max() - s.min() + 1e-9)
    return pd.DataFrame({"unit_id": features["unit_id"], "subscore_outlier": s})
