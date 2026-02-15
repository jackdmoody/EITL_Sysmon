from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    triage = pd.read_csv(run_dir / "triage.csv")
    print(triage.head(20).to_string(index=False))
    print(f"Packets dir: {run_dir/'packets'}")

if __name__ == "__main__":
    main()
