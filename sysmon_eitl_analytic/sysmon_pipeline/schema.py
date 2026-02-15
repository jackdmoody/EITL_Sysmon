from __future__ import annotations
import pandas as pd

def normalize_events(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Normalize raw events into canonical schema.

    Expected canonical columns include:
    - timestamp, host, user, event_id
    - image, command_line, parent_image, parent_command_line
    - dest_ip, dest_port, proto

    TODO: extend mappings for EVTX JSON exports.
    """
    norm = cfg.get("schema", {}).get("normalize", {})
    # Basic cleanup
    if norm.get("coerce_types", True):
        if "event_id" in df.columns:
            df["event_id"] = pd.to_numeric(df["event_id"], errors="coerce").astype("Int64")
        if "dest_port" in df.columns:
            df["dest_port"] = pd.to_numeric(df["dest_port"], errors="coerce").astype("Int64")

    # Timestamp
    ts_col = cfg["ingest"]["timestamp_column"]
    if ts_col not in df.columns:
        raise ValueError(f"Missing timestamp column: {ts_col}")
    df = df.rename(columns={ts_col: "timestamp"})

    # Host
    host_col = cfg["ingest"]["host_column"]
    if host_col not in df.columns:
        raise ValueError(f"Missing host column: {host_col}")
    df = df.rename(columns={host_col: "host"})

    # Optional user
    user_col = cfg["ingest"].get("user_column", "user")
    if user_col in df.columns and user_col != "user":
        df = df.rename(columns={user_col: "user"})
    if "user" not in df.columns:
        df["user"] = None

    # Event id
    eid_col = cfg["ingest"]["event_id_column"]
    if eid_col in df.columns and eid_col != "event_id":
        df = df.rename(columns={eid_col: "event_id"})

    # Process fields mapping
    pf = cfg["ingest"].get("process_fields", {})
    for canon, raw in pf.items():
        if raw in df.columns and canon not in df.columns:
            df[canon] = df[raw]
        elif canon not in df.columns:
            df[canon] = None

    # Network fields mapping
    nf = cfg["ingest"].get("network_fields", {})
    for canon, raw in nf.items():
        if raw in df.columns and canon not in df.columns:
            df[canon] = df[raw]
        elif canon not in df.columns:
            df[canon] = None

    # Lowercase image paths if requested
    if norm.get("lowercase_images", True):
        for col in ["image", "parent_image"]:
            if col in df.columns:
                df[col] = df[col].astype("string").str.lower()

    # Parse timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    if norm.get("drop_missing_timestamp", True):
        df = df.dropna(subset=["timestamp"])
    if norm.get("drop_missing_host", True):
        df = df.dropna(subset=["host"])

    return df
