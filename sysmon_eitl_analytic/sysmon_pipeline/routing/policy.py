from __future__ import annotations
import pandas as pd
from .capacity import compute_priority
from .explain import why_routed

def apply_routing(scores: pd.DataFrame, thresholds_cfg: dict) -> pd.DataFrame:
    """Apply certainty-based routing and capacity-aware prioritization."""
    routing = thresholds_cfg.get("routing", {})
    r_low = float(routing.get("r_low", 0.2))
    r_high = float(routing.get("r_high", 0.8))
    u_low = float(routing.get("u_low", 0.25))

    df = scores.copy()
    df["route"] = "EITL_REVIEW"
    df.loc[(df["R"] < r_low) & (df["U"] < u_low), "route"] = "AUTO_CLEAR"
    df.loc[(df["R"] > r_high) & (df["U"] < u_low), "route"] = "AUTO_ESCALATE"

    df["priority"] = compute_priority(df, thresholds_cfg)
    df["why_routed"] = df.apply(why_routed, axis=1)

    # Budget enforcement: keep EITL queue to daily_budget highest-priority; spill rest to AUTO_CLEAR-ish
    if routing.get("enforce_budget", True):
        B = int(thresholds_cfg.get("capacity", {}).get("daily_budget", 100))
        eitl = df[df["route"] == "EITL_REVIEW"].copy()
        if len(eitl) > B:
            keep_ids = eitl.sort_values("priority", ascending=False).head(B)["unit_id"]
            spill = eitl[~eitl["unit_id"].isin(keep_ids)].index
            df.loc[spill, "route"] = "AUTO_CLEAR"
            df.loc[spill, "why_routed"] = "EITL budget exceeded; deprioritized and auto-cleared."
    return df
