from __future__ import annotations
from pathlib import Path
import pandas as pd

def _render_packet_md(row: pd.Series, raw_events: pd.DataFrame, limit: int = 25) -> str:
    rows = raw_events.head(limit)
    table = []
    table.append("| time | event_id | image | parent_image | command_line | dest_ip:port |")
    table.append("|---|---:|---|---|---|---|")
    for _, r in rows.iterrows():
        dip = f"{r.get('dest_ip','')}"
        dpt = r.get('dest_port','')
        d = f"{dip}:{dpt}" if dip or str(dpt) != "nan" else ""
        table.append(
            f"| {r['timestamp']} | {r.get('event_id','')} | {str(r.get('image',''))[:60]} | {str(r.get('parent_image',''))[:60]} | {str(r.get('command_line',''))[:60]} | {d} |"
        )

    md = f"""# EITL Decision Packet

**Unit:** {row['unit_id']}  
**Host:** {row['host']} (role: {row.get('host_role','unknown')})  
**Window:** {row['window_start']} → {row['window_end']}  
**Route:** {row['route']} | **Priority:** {row.get('priority',0):.3f}  
**Risk (R):** {row.get('R',0):.3f} | **Uncertainty (U):** {row.get('U',0):.3f}

## Summary
- {row.get('why_routed','')}
- Top signals: {row.get('top_signals','')}
- MITRE: {row.get('top_mitre','')}

## Subscores
- Drift: {row.get('subscore_drift',0):.3f}
- Outlier: {row.get('subscore_outlier',0):.3f}
- Rules: {row.get('subscore_rules',0):.3f}
- Graph: {row.get('subscore_graph',0):.3f}

## Raw Events (excerpt)
""" + "\n".join(table) + f"""

## Recommended Next Step
- Confirm label (BENIGN/MALICIOUS/UNCLEAR) and assign a reason code in `data/feedback/labels.csv`.
- If MALICIOUS: pivot on `image`, `hashes`, and process ancestry.
"""
    return md

def write_packets(triage: pd.DataFrame, events: pd.DataFrame, outdir: str | Path, fmt: str = "md", raw_limit: int = 25) -> pd.DataFrame:
    """Write packets for EITL_REVIEW items and return triage with packet_path."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    triage = triage.copy()
    triage["packet_path"] = ""

    eitl = triage[triage["route"] == "EITL_REVIEW"]
    for _, row in eitl.iterrows():
        unit_id = row["unit_id"]
        raw = events[events["unit_id"] == unit_id].sort_values("timestamp")
        if fmt.lower() != "md":
            # TODO: add HTML rendering
            content = _render_packet_md(row, raw, limit=raw_limit)
            ext = "md"
        else:
            content = _render_packet_md(row, raw, limit=raw_limit)
            ext = "md"
        path = outdir / f"{unit_id}.{ext}"
        path.write_text(content, encoding="utf-8")
        triage.loc[triage["unit_id"] == unit_id, "packet_path"] = str(path)
    return triage
