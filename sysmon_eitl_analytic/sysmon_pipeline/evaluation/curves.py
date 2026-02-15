from __future__ import annotations
import pandas as pd
from .metrics import compute_basic_metrics

def simulate_budgets(triage: pd.DataFrame, labels: pd.DataFrame, budgets: list[int]) -> pd.DataFrame:
    """Simulate different EITL budgets by forcing only top-B EITL items to remain EITL.

    Note: This is a simplified stand-in for more detailed simulation.
    """
    rows = []
    base = triage.copy()
    eitl = base[base["route"] == "EITL_REVIEW"].sort_values("priority", ascending=False)
    for B in budgets:
        t = base.copy()
        keep = set(eitl.head(B)["unit_id"])
        # spill remaining EITL to AUTO_CLEAR for simulation
        mask_spill = (t["route"] == "EITL_REVIEW") & (~t["unit_id"].isin(keep))
        t.loc[mask_spill, "route"] = "AUTO_CLEAR"
        m = compute_basic_metrics(t, labels)
        m.update({"budget": int(B)})
        rows.append(m)
    return pd.DataFrame(rows)
