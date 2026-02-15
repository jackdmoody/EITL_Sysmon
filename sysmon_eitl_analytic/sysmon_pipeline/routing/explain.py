from __future__ import annotations
import pandas as pd

def why_routed(row: pd.Series) -> str:
    signals = row.get("top_signals","") or ""
    if row["route"] == "AUTO_ESCALATE":
        return f"High risk with low uncertainty. Signals: {signals}".strip()
    if row["route"] == "AUTO_CLEAR":
        return "Low risk with low uncertainty."
    return f"Ambiguous or novel behavior (uncertainty={row.get('U',0):.2f}). Signals: {signals}".strip()
