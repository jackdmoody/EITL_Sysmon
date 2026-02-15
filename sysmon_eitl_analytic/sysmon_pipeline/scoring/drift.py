from __future__ import annotations
import pandas as pd
import numpy as np

def js_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-6) -> float:
    """Jensen-Shannon divergence between two discrete distributions."""
    p = np.clip(p, eps, 1.0); q = np.clip(q, eps, 1.0)
    p = p / p.sum(); q = q / q.sum()
    m = 0.5*(p+q)
    def kl(a,b):
        return float(np.sum(a * np.log(a/b)))
    return 0.5*kl(p,m) + 0.5*kl(q,m)

def compute_peer_transition_baseline(td: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    """Compute baseline transition distribution per host_role."""
    urole = units[["unit_id","host_role"]]
    t = td.merge(urole, on="unit_id", how="left")
    # average probability of transition across units in role
    base = t.groupby(["host_role","transition"])["p"].mean().reset_index()
    return base

def compute_transition_drift(td: pd.DataFrame, units: pd.DataFrame, baseline: pd.DataFrame, smoothing: float=1e-6) -> pd.DataFrame:
    """Compute JS drift per unit relative to host_role baseline."""
    # Build per-role vocab
    urole = units[["unit_id","host_role"]]
    t = td.merge(urole, on="unit_id", how="left")
    # pivot per unit
    # For efficiency on big data, replace with sparse representation later.
    all_trans = sorted(set(baseline["transition"]).union(set(t["transition"])))
    drift_rows = []
    for unit_id, g in t.groupby("unit_id"):
        role = g["host_role"].iloc[0] if "host_role" in g.columns else "unknown"
        p_map = dict(zip(g["transition"], g["p"]))
        b = baseline[baseline["host_role"]==role]
        q_map = dict(zip(b["transition"], b["p"]))
        p = np.array([p_map.get(tr, 0.0) for tr in all_trans], dtype=float) + smoothing
        q = np.array([q_map.get(tr, 0.0) for tr in all_trans], dtype=float) + smoothing
        d = js_divergence(p, q, eps=smoothing)
        drift_rows.append((unit_id, float(d)))
    return pd.DataFrame(drift_rows, columns=["unit_id","subscore_drift"])
