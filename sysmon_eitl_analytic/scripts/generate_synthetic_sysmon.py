from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    hosts = [f"WS{n:03d}" for n in range(1, 21)] + ["DC01","SRV01"]
    images = ["c:\\windows\\system32\\svchost.exe", "c:\\windows\\system32\\lsass.exe",
              "c:\\program files\\microsoft office\\root\\office16\\winword.exe",
              "c:\\windows\\system32\\windowsPowerShell\\v1.0\\powershell.exe",
              "c:\\windows\\system32\\rundll32.exe"]
    parents = ["c:\\windows\\explorer.exe", images[2], "unknown_parent"]
    eids = [1,3,7,10,11,12,13,22]

    base_time = np.datetime64("2026-02-08T00:00:00Z")
    ts = base_time + rng.integers(0, 7*24*3600, size=args.rows).astype("timedelta64[s]")

    df = pd.DataFrame({
        "timestamp": ts.astype("datetime64[ns]"),
        "host": rng.choice(hosts, size=args.rows),
        "user": rng.choice(["alice","bob","svc_patch","admin"], size=args.rows),
        "event_id": rng.choice(eids, size=args.rows, p=[.35,.12,.08,.05,.10,.08,.08,.14]),
        "image": rng.choice(images, size=args.rows, p=[.55,.05,.10,.20,.10]),
        "parent_image": rng.choice(parents, size=args.rows, p=[.75,.10,.15]),
        "command_line": "",
        "dest_ip": rng.choice([None,"8.8.8.8","1.1.1.1","10.0.0.5"], size=args.rows, p=[.70,.10,.10,.10]),
        "dest_port": rng.choice([None,53,80,443,445,3389], size=args.rows, p=[.70,.10,.05,.10,.03,.02]),
        "proto": rng.choice([None,"tcp","udp"], size=args.rows, p=[.70,.20,.10]),
        "signed": rng.choice(["true","false"], size=args.rows, p=[.92,.08]),
        "hashes": ""
    })

    # inject a few malicious-ish sequences: winword -> powershell -enc
    for _ in range(50):
        h = rng.choice(hosts)
        t0 = base_time + np.timedelta64(int(rng.integers(0, 7*24*3600)), "s")
        df = pd.concat([df, pd.DataFrame([
            {"timestamp": pd.Timestamp(t0).to_datetime64(), "host": h, "user":"alice", "event_id":1,
             "image": images[2], "parent_image":"c:\\windows\\explorer.exe", "command_line":"", "dest_ip":None, "dest_port":None, "proto":None, "signed":"true","hashes":""},
            {"timestamp": pd.Timestamp(t0 + np.timedelta64(60,"s")).to_datetime64(), "host": h, "user":"alice", "event_id":1,
             "image": images[3], "parent_image": images[2], "command_line":"powershell.exe -enc ZQB2AGkAbAA=", "dest_ip":"8.8.8.8", "dest_port":443, "proto":"tcp", "signed":"true","hashes":""},
        ])], ignore_index=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {out} ({len(df)} rows)")

if __name__ == "__main__":
    main()
