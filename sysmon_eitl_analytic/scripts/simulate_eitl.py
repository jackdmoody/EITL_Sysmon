from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from sysmon_pipeline.eitl.feedback_store import read_labels
from sysmon_pipeline.evaluation.curves import simulate_budgets

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    ap.add_argument("--label_source", required=True)
    ap.add_argument("--budgets", nargs="+", type=int, required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    triage = pd.read_csv(run_dir / "triage.csv")
    labels = read_labels(args.label_source)

    curves = simulate_budgets(triage, labels, args.budgets)
    curves.to_csv(outdir / "curves.csv", index=False)
    print(f"Wrote {outdir/'curves.csv'}")
    print(curves.to_string(index=False))

if __name__ == "__main__":
    main()
