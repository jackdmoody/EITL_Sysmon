from __future__ import annotations
import pandas as pd

def compute_impact(row: pd.Series, thresholds_cfg: dict) -> float:
    impact_cfg = thresholds_cfg.get("impact", {})
    role_mult = impact_cfg.get("host_role_multiplier", {})
    role = row.get("host_role","unknown")
    return float(role_mult.get(role, role_mult.get("unknown", 1.0)))

def compute_priority(df: pd.DataFrame, thresholds_cfg: dict) -> pd.Series:
    cap = thresholds_cfg.get("capacity", {})
    w = cap.get("priority_weights", {})
    a = float(w.get("alpha_uncertainty", 0.55))
    b = float(w.get("beta_risk", 0.35))
    g = float(w.get("gamma_impact", 0.10))
    impacts = df.apply(lambda r: compute_impact(r, thresholds_cfg), axis=1)
    P = a*df["U"].astype(float) + b*df["R"].astype(float) + g*impacts.astype(float)
    return P
