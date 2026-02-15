from __future__ import annotations
import pandas as pd
import numpy as np
from .drift import compute_peer_transition_baseline, compute_transition_drift
from .outlier import compute_outlier_scores
from .rules import rule_hits_for_unit

def compute_graph_subscore(edges: pd.DataFrame) -> pd.DataFrame:
    """Toy graph subscore: more unique edges -> higher score."""
    if edges.empty:
        return pd.DataFrame(columns=["unit_id","subscore_graph"])
    g = edges.groupby("unit_id")["edge"].nunique().reset_index(name="unique_edges")
    s = g["unique_edges"].astype(float)
    s = (s - s.min()) / (s.max() - s.min() + 1e-9)
    g["subscore_graph"] = s
    return g[["unit_id","subscore_graph"]]

def weighted_sum_fusion(df: pd.DataFrame, weights: dict) -> pd.Series:
    comps = ["subscore_drift","subscore_outlier","subscore_rules","subscore_graph"]
    w = {k: float(weights.get(k.split('_')[-1], weights.get(k, 0.0))) for k in comps}
    # weights in config are drift/outlier/rules/graph
    out = (
        w.get("drift", 0.35)*df["subscore_drift"].fillna(0.0)
        + w.get("outlier",0.30)*df["subscore_outlier"].fillna(0.0)
        + w.get("rules",0.25)*df["subscore_rules"].fillna(0.0)
        + w.get("graph",0.10)*df["subscore_graph"].fillna(0.0)
    )
    # normalize to 0-1
    out = (out - out.min()) / (out.max() - out.min() + 1e-9)
    return out

def compute_risk(units: pd.DataFrame, events: pd.DataFrame, td: pd.DataFrame, edges: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Compute risk subscores and fused risk score R."""
    scoring_cfg = cfg.get("scoring", {})
    smoothing = float(scoring_cfg.get("drift", {}).get("smoothing", 1e-6))

    # Drift
    baseline = compute_peer_transition_baseline(td, units)
    drift = compute_transition_drift(td, units, baseline, smoothing=smoothing)

    # Outlier
    out_params = scoring_cfg.get("outlier", {}).get("isolation_forest", {})
    outlier = compute_outlier_scores(units, out_params)

    # Rules
    rules = rule_hits_for_unit(events)

    # Graph
    graph = compute_graph_subscore(edges)

    # Merge
    df = units.merge(drift, on="unit_id", how="left")              .merge(outlier, on="unit_id", how="left")              .merge(rules, on="unit_id", how="left")              .merge(graph, on="unit_id", how="left")

    # Fill missing subscores
    for c in ["subscore_drift","subscore_outlier","subscore_rules","subscore_graph"]:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = df[c].fillna(0.0)

    # Normalize drift to 0-1
    d = df["subscore_drift"].astype(float)
    df["subscore_drift"] = ((d - d.min()) / (d.max() - d.min() + 1e-9)).fillna(0.0)

    # Fuse
    weights = scoring_cfg.get("risk_fusion", {}).get("weights", {"drift":0.35,"outlier":0.30,"rules":0.25,"graph":0.10})
    df["R"] = weighted_sum_fusion(df, weights)

    # Explanation helper fields
    if "top_signals" not in df.columns:
        df["top_signals"] = ""
    if "top_mitre" not in df.columns:
        df["top_mitre"] = ""

    return df
