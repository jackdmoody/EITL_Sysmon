from __future__ import annotations
import pandas as pd
from .disagreement import variance_disagreement
from .boundary import margin_uncertainty
from .density import density_uncertainty_placeholder

def compute_uncertainty(scores: pd.DataFrame, cfg: dict, thresholds_cfg: dict) -> pd.DataFrame:
    """Compute uncertainty U and store component uncertainties."""
    ucfg = thresholds_cfg.get("uncertainty", {})
    src = ucfg.get("sources", {"disagreement":True,"boundary":True,"density":False})
    w = ucfg.get("aggregate_weights", {"disagreement":0.6,"boundary":0.4,"density":0.0})

    u_dis = variance_disagreement(scores) if src.get("disagreement", True) else 0.0
    center = float(cfg.get("uncertainty", {}).get("boundary", {}).get("margin_center", 0.5))
    u_bnd = margin_uncertainty(scores["R"], center=center) if src.get("boundary", True) else 0.0
    u_den = density_uncertainty_placeholder(scores) if src.get("density", False) else 0.0

    U = (
        float(w.get("disagreement",0.6))*u_dis
        + float(w.get("boundary",0.4))*u_bnd
        + float(w.get("density",0.0))*u_den
    )
    U = (U - U.min()) / (U.max() - U.min() + 1e-9)

    out = scores.copy()
    out["U"] = U
    out["U_disagreement"] = u_dis
    out["U_boundary"] = u_bnd
    out["U_density"] = u_den
    return out
