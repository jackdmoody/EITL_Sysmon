from __future__ import annotations
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

def compute_basic_metrics(triage: pd.DataFrame, labels: pd.DataFrame) -> dict:
    """Compute basic classification metrics from triage and labels.

    Mapping:
    - MALICIOUS -> 1
    - BENIGN -> 0
    UNCLEAR rows are dropped for metric computation.
    Predicted label is 1 if route is AUTO_ESCALATE or (EITL_REVIEW and R high).
    """
    lab = labels.copy()
    lab = lab[lab["label"].isin(["MALICIOUS","BENIGN"])].copy()
    if lab.empty:
        return {}

    df = triage.merge(lab[["unit_id","label"]], on="unit_id", how="inner")
    y_true = (df["label"] == "MALICIOUS").astype(int)

    # Conservative prediction: AUTO_ESCALATE => malicious; AUTO_CLEAR => benign; EITL_REVIEW predicted by R>0.5
    y_pred = (
        (df["route"] == "AUTO_ESCALATE")
        | ((df["route"] == "EITL_REVIEW") & (df["R"].astype(float) > 0.5))
    ).astype(int)

    return {
        "f1": float(f1_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "n": int(len(df)),
    }
