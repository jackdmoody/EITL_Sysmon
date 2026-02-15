from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

from sysmon_pipeline.config import load_configs
from sysmon_pipeline.ingest import read_input
from sysmon_pipeline.schema import normalize_events
from sysmon_pipeline.enrich import enrich_events
from sysmon_pipeline.profile import make_host_windows, build_feature_matrix
from sysmon_pipeline.sequence import transition_counts, transition_distribution
from sysmon_pipeline.graph import parent_child_edges
from sysmon_pipeline.scoring.risk import compute_risk
from sysmon_pipeline.uncertainty.aggregate import compute_uncertainty
from sysmon_pipeline.routing.policy import apply_routing
from sysmon_pipeline.eitl.packets import write_packets

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--thresholds", required=True)
    ap.add_argument("--roles", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    bundle = load_configs(args.config, args.thresholds, args.roles)
    cfg, thr, roles = bundle.config, bundle.thresholds, bundle.roles

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    raw = read_input(args.input, cfg)
    events = normalize_events(raw, cfg)
    events = enrich_events(events, cfg, roles)

    unit_cfg = cfg["pipeline"]["unit"]
    units, events2 = make_host_windows(events, int(unit_cfg["window_hours"]), int(unit_cfg["slide_hours"]))
    feats = build_feature_matrix(units)

    # attach features back to units for outlier (reference implementation uses columns produced in build_feature_matrix)
    units = feats

    # Sequence + graph artifacts
    tc = transition_counts(events2)
    td = transition_distribution(tc)
    edges = parent_child_edges(events2)

    # Risk
    scores = compute_risk(units, events2, td, edges, cfg)
    # Uncertainty
    scores = compute_uncertainty(scores, cfg, thr)
    # Routing
    triage = apply_routing(scores, thr)

    # Packets
    if thr.get("output", {}).get("packets", {}).get("format", "md"):
        fmt = thr.get("output", {}).get("packets", {}).get("format", "md")
    else:
        fmt = "md"
    pkt_dir = outdir / "packets"
    triage = write_packets(triage, events2, pkt_dir, fmt=fmt, raw_limit=int(thr.get("output", {}).get("packets", {}).get("include_raw_events_limit", 25)))

    # Persist
    if cfg.get("outputs", {}).get("write_parquet", True):
        units.to_parquet(outdir / "units.parquet", index=False)
        scores.to_parquet(outdir / "scores.parquet", index=False)
    triage.to_csv(outdir / "triage.csv", index=False)

    print(f"Wrote: {outdir/'triage.csv'}")
    print(f"Packets: {pkt_dir}")

if __name__ == "__main__":
    main()
