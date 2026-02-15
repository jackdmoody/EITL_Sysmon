from __future__ import annotations
import pandas as pd

LOLBINS = {
    "powershell.exe", "pwsh.exe", "cmd.exe", "rundll32.exe", "regsvr32.exe",
    "mshta.exe", "wscript.exe", "cscript.exe", "wmic.exe"
}

def add_host_role(df: pd.DataFrame, roles_cfg: dict) -> pd.DataFrame:
    """Add host_role based on exact map or prefix map."""
    exact = roles_cfg.get("host_role_map", {}) or {}
    prefix = roles_cfg.get("prefix_role_map", {}) or {}

    def role_of(h: str) -> str:
        if h in exact:
            return exact[h]
        for p, r in prefix.items():
            if str(h).startswith(p):
                return r
        return roles_cfg.get("default_role", "unknown") if isinstance(roles_cfg.get("default_role", None), str) else "unknown"

    df["host_role"] = df["host"].astype(str).map(role_of)
    return df

def add_simple_mitre_tags(df: pd.DataFrame) -> pd.DataFrame:
    """Very lightweight MITRE heuristic tags for demonstration.

    TODO: Replace with robust mapping table per Sysmon Event ID + context.
    """
    tags = []
    for img, cmd in zip(df["image"].fillna(""), df["command_line"].fillna("")):
        t = []
        if "powershell" in str(img):
            t.append("T1059.001")
            if "-enc" in str(cmd) or "encodedcommand" in str(cmd).lower():
                t.append("T1027")
        if "rundll32" in str(img):
            t.append("T1218.011")
        tags.append(",".join(sorted(set(t))) if t else "")
    df["mitre_tags"] = tags
    return df

def add_severity(df: pd.DataFrame) -> pd.DataFrame:
    """Assign a crude severity score per event for demo purposes."""
    sev = []
    for img, cmd in zip(df["image"].fillna(""), df["command_line"].fillna("")):
        s = 0.1
        if any(bin in str(img) for bin in LOLBINS):
            s += 0.3
        if "-enc" in str(cmd).lower() or "encodedcommand" in str(cmd).lower():
            s += 0.4
        sev.append(min(1.0, s))
    df["severity_event"] = sev
    return df

def enrich_events(df: pd.DataFrame, cfg: dict, roles_cfg: dict) -> pd.DataFrame:
    """Apply enrichments: roles, heuristic MITRE tags, severity."""
    df = add_host_role(df, roles_cfg)
    if cfg.get("enrich", {}).get("mitre_tagging", True):
        df = add_simple_mitre_tags(df)
    if cfg.get("enrich", {}).get("severity_scoring", True):
        df = add_severity(df)
    return df
