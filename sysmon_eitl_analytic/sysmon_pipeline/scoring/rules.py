from __future__ import annotations
import pandas as pd

LOLBINS = {
    "powershell.exe","pwsh.exe","cmd.exe","rundll32.exe","regsvr32.exe",
    "mshta.exe","wscript.exe","cscript.exe","wmic.exe"
}

def rule_hits_for_unit(events: pd.DataFrame) -> pd.DataFrame:
    """Compute simple rule-based subscores per unit and evidence strings."""
    ev = events.copy()
    ev["image"] = ev["image"].fillna("")
    ev["parent_image"] = ev["parent_image"].fillna("")
    ev["command_line"] = ev["command_line"].fillna("")

    # rule: suspicious parent-child chain (office -> powershell)
    office = ("winword.exe","excel.exe","outlook.exe","powerpnt.exe")
    chain = ev["parent_image"].str.contains("|".join(office), regex=True) & ev["image"].str.contains("powershell", regex=False)
    # rule: LOLBin execution
    lol = ev["image"].apply(lambda x: any(bin in str(x) for bin in LOLBINS))
    # rule: encoded powershell
    encps = ev["image"].str.contains("powershell", regex=False) & ev["command_line"].str.lower().str.contains("encodedcommand|-enc", regex=True)

    # rule: unsigned in system paths (toy check based on string)
    unsigned = ev.get("signed", pd.Series([None]*len(ev))).astype("string").fillna("").str.lower().isin(["false","unsigned","0"])
    sys_path = ev["image"].str.contains("windows\\system32|\\system32", regex=True)
    unsigned_sys = unsigned & sys_path

    rules_df = pd.DataFrame({
        "unit_id": ev["unit_id"],
        "hit_chain_office_ps": chain.astype(int),
        "hit_lolbin": lol.astype(int),
        "hit_encoded_ps": encps.astype(int),
        "hit_unsigned_system": unsigned_sys.astype(int),
    })

    agg = rules_df.groupby("unit_id").sum().reset_index()
    # subscore: capped linear combination then normalized later in risk fusion
    agg["subscore_rules_raw"] = (
        0.5*agg["hit_chain_office_ps"]
        + 0.3*agg["hit_encoded_ps"]
        + 0.2*agg["hit_lolbin"]
        + 0.2*agg["hit_unsigned_system"]
    )
    # squash to 0-1
    agg["subscore_rules"] = (agg["subscore_rules_raw"] / (agg["subscore_rules_raw"].max() + 1e-9)).clip(0,1)

    # evidence snippets (top signals)
    def mk_signals(row):
        s=[]
        if row["hit_chain_office_ps"]>0: s.append("office->powershell")
        if row["hit_encoded_ps"]>0: s.append("encoded_powershell")
        if row["hit_lolbin"]>0: s.append("lolbin_execution")
        if row["hit_unsigned_system"]>0: s.append("unsigned_in_system_paths")
        return ";".join(s)
    agg["top_signals"] = agg.apply(mk_signals, axis=1)
    return agg[["unit_id","subscore_rules","top_signals"]]
