# Triage Output Schema

This document defines stable output contracts for downstream dashboards and integrations.

## triage.csv (required columns)
- unit_id
- host
- window_start (ISO8601)
- window_end (ISO8601)
- host_role
- R (float)
- U (float)
- route (AUTO_CLEAR|AUTO_ESCALATE|EITL_REVIEW)
- priority (float)
- why_routed (string)

## triage.csv (recommended columns)
- subscore_drift
- subscore_outlier
- subscore_rules
- subscore_graph
- top_mitre (comma-separated)
- top_signals (semicolon-separated)
- packet_path

## Packets
A packet is a Markdown (or HTML) file under `packets/` for EITL items.
It is a one-screen decision bundle including summary, evidence, baseline comparisons, and raw event excerpt.
