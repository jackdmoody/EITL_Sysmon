# Sysmon EITL Analytic

A Sysmon behavioral analytic redesigned as an **Expert-in-the-Loop (EITL)** system.

It produces, per **unit of work** (default: **host-window**, e.g., 6h):

- **Risk score** `R` — *how suspicious*
- **Uncertainty score** `U` — *how sure*
- **Routing decision** — `AUTO_CLEAR`, `AUTO_ESCALATE`, or `EITL_REVIEW`
- **Analyst decision packets** (Markdown/HTML) for EITL review items
- **Capacity tradeoff simulation** to quantify quality vs analyst workload

This repo is inspired by confidence-based routing designs used for AI+human triage in cybersecurity workflows (see the uploaded WSC 2025 paper for the architectural parallel). fileciteturn0file0

---

## Repo structure

```text
sysmon_eitl_analytic/
├── configs/
│   ├── default.yaml
│   ├── thresholds.yaml
│   ├── roles.yaml
│   └── allowlists/
│       ├── known_good_images.txt
│       ├── known_good_parents.txt
│       └── known_good_hashes.txt
├── data/
│   ├── raw/
│   ├── processed/
│   └── feedback/
├── docs/
│   ├── reason_codes.md
│   └── triage_schema.md
├── notebooks/
│   ├── 01_build_profiles.ipynb
│   ├── 02_score_uncertainty.ipynb
│   ├── 03_routing_simulation.ipynb
│   └── 04_analyst_packet_examples.ipynb
├── scripts/
│   ├── run_pipeline.py
│   ├── export_triage.py
│   └── simulate_eitl.py
└── sysmon_pipeline/
    ├── __init__.py
    ├── config.py
    ├── schema.py
    ├── ingest.py
    ├── enrich.py
    ├── profile.py
    ├── sequence.py
    ├── graph.py
    ├── scoring/
    │   ├── __init__.py
    │   ├── drift.py
    │   ├── outlier.py
    │   ├── rules.py
    │   ├── risk.py
    │   └── calibrate.py
    ├── uncertainty/
    │   ├── __init__.py
    │   ├── disagreement.py
    │   ├── boundary.py
    │   ├── density.py
    │   └── aggregate.py
    ├── routing/
    │   ├── __init__.py
    │   ├── policy.py
    │   ├── capacity.py
    │   └── explain.py
    ├── eitl/
    │   ├── __init__.py
    │   ├── packets.py
    │   ├── feedback_store.py
    │   └── active_learning.py
    └── evaluation/
        ├── __init__.py
        ├── metrics.py
        ├── curves.py
        └── ablation.py
```

---

## Quickstart

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) Add Sysmon data

Put exports in `data/raw/`. The reference runner expects a CSV with at least:

- `timestamp` (ISO8601 or epoch seconds)
- `host`
- `event_id` (Sysmon event id)
- `image` (process image, can be empty for non-process events)
- `parent_image` (optional)
- `command_line` (optional)
- `dest_ip`, `dest_port`, `proto` (optional)

> If your dataset uses different column names, update `configs/default.yaml` → `ingest.*_column` and `sysmon_pipeline/schema.py`.

### 3) Run the pipeline

```bash
python scripts/run_pipeline.py   --config configs/default.yaml   --thresholds configs/thresholds.yaml   --roles configs/roles.yaml   --input data/raw/sysmon_week.csv   --outdir data/processed/run_001
```

Outputs in `data/processed/run_001/`:
- `units.parquet` — host-window features
- `scores.parquet` — subscores + fused `R` and `U`
- `triage.csv` — routing + priority
- `packets/` — markdown packets for EITL items

### 4) Export triage + packets (optional)

```bash
python scripts/export_triage.py   --run_dir data/processed/run_001
```

### 5) Add analyst labels + simulate capacity tradeoffs

Create `data/feedback/labels.csv` (see template under `data/feedback/labels_example.csv`), then:

```bash
python scripts/simulate_eitl.py   --run_dir data/processed/run_001   --label_source data/feedback/labels.csv   --budgets 25 50 100 250 500   --outdir data/processed/run_001/eitl_sim
```

---

## EITL design: Risk vs Uncertainty vs Routing

- `R` answers: **“how bad?”**
- `U` answers: **“how sure are we?”**
- Routing uses both:
  - `AUTO_CLEAR` when low risk + low uncertainty
  - `AUTO_ESCALATE` when high risk + low uncertainty
  - `EITL_REVIEW` otherwise (ambiguous, novel, high-impact)

EITL queue ordering is budget-aware:

\[
P(x)=\alpha U(x) + \beta R(x) + \gamma \text{Impact}(x)
\]

See `configs/thresholds.yaml` for knobs.

---

## Notes & next steps (roadmap)

This repo ships with a **functional reference implementation** so you can run end-to-end quickly.
To harden for operations/research:

- Add richer Sysmon mappings (Event IDs 1/3/7/8/10/11/12/13/22/etc.)
- Expand rules with environment-aware allowlisting
- Replace the simple drift baseline with role-stratified, time-of-day stratified baselines
- Add clustering-based density uncertainty (HDBSCAN membership)
- Add a dashboard (Streamlit/Plotly) reading `triage.csv` + packet files

---

## License

MIT
