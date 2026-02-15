from __future__ import annotations
import pandas as pd
import numpy as np

def make_host_windows(events: pd.DataFrame, window_hours: int, slide_hours: int) -> pd.DataFrame:
    """Aggregate events into host-window units.

    Returns a unit table with unit_id, host, role, window_start/end and basic count features.
    """
    # align to slide boundary
    slide = f"{slide_hours}H"
    events = events.copy()
    events["window_start"] = events["timestamp"].dt.floor(slide)
    events["window_end"] = events["window_start"] + pd.Timedelta(hours=window_hours)
    events["unit_id"] = (
        events["host"].astype(str)
        + "_"
        + events["window_start"].dt.strftime("%Y-%m-%dT%H:%MZ")
        + f"_{window_hours}h"
    )

    # Basic rates
    grp = events.groupby(["unit_id","host","host_role","window_start","window_end"], dropna=False)
    units = grp.agg(
        event_count=("event_id","count"),
        unique_images=("image", lambda s: s.dropna().nunique()),
        unique_users=("user", lambda s: s.dropna().nunique()),
        net_touches=("dest_ip", lambda s: s.notna().sum()),
        avg_event_severity=("severity_event","mean"),
        top_mitre=("mitre_tags", lambda s: ",".join(sorted(set(",".join(s.dropna().astype(str)).split(",")) - {""}))),
    ).reset_index()

    # Fill empty MITRE
    units["top_mitre"] = units["top_mitre"].fillna("").astype(str)

    return units, events

def build_feature_matrix(units: pd.DataFrame) -> pd.DataFrame:
    """Create numeric feature matrix used by outlier detectors."""
    feats = units.copy()
    for col in ["event_count","unique_images","unique_users","net_touches","avg_event_severity"]:
        feats[col] = pd.to_numeric(feats[col], errors="coerce").fillna(0.0)
    # simple log transforms for heavy-tailed counts
    feats["log_event_count"] = np.log1p(feats["event_count"])
    feats["log_unique_images"] = np.log1p(feats["unique_images"])
    feats["log_net_touches"] = np.log1p(feats["net_touches"])
    return feats
