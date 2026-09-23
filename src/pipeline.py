import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


REQUIRED_COLUMNS = {
    "transaction_id",
    "account_id",
    "counterparty_id",
    "timestamp",
    "amount",
    "country",
    "counterparty_country",
    "transaction_type",
    "account_age_days",
}


def validate_transactions(frame: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if frame["transaction_id"].duplicated().any():
        raise ValueError("transaction_id must be unique")
    if (frame["amount"] <= 0).any():
        raise ValueError("amount must be positive")


def build_review_queue(frame: pd.DataFrame) -> pd.DataFrame:
    validate_transactions(frame)
    data = frame.copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
    data = data.sort_values("timestamp").reset_index(drop=True)

    amount_cutoff = data["amount"].quantile(0.98)
    data["large_amount"] = data["amount"] >= amount_cutoff
    data["cross_border"] = data["country"] != data["counterparty_country"]
    data["new_account"] = data["account_age_days"] <= 30
    data["transactions_24h"] = 0.0
    for indices in data.groupby("account_id").groups.values():
        account_rows = data.loc[indices].sort_values("timestamp")
        counts = account_rows.rolling("24h", on="timestamp", closed="both")[
            "transaction_id"
        ].count()
        data.loc[account_rows.index, "transactions_24h"] = counts.to_numpy()
    data["rapid_movement"] = data["transactions_24h"] >= 4

    model_features = data[["amount", "account_age_days", "transactions_24h"]]
    scaled = StandardScaler().fit_transform(np.log1p(model_features))
    model = IsolationForest(contamination=0.04, n_estimators=40, n_jobs=-1, random_state=42)
    model.fit(scaled)
    anomaly_raw = -model.score_samples(scaled)
    data["anomaly_score"] = (anomaly_raw - anomaly_raw.min()) / (
        anomaly_raw.max() - anomaly_raw.min() + 1e-9
    )

    data["risk_score"] = (
        30 * data["large_amount"].astype(int)
        + 20 * data["cross_border"].astype(int)
        + 15 * data["new_account"].astype(int)
        + 15 * data["rapid_movement"].astype(int)
        + 20 * data["anomaly_score"]
    ).round(1)
    data["risk_band"] = pd.cut(
        data["risk_score"], bins=[-1, 25, 50, 100], labels=["low", "medium", "high"]
    ).astype(str)

    signal_names = ["large_amount", "cross_border", "new_account", "rapid_movement"]
    data["risk_reason"] = data.apply(
        lambda row: ", ".join(name.replace("_", " ") for name in signal_names if row[name])
        or "statistical anomaly",
        axis=1,
    )
    data["review_status"] = "open"
    return data.sort_values(["risk_score", "amount"], ascending=False).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a ranked transaction review queue.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    queue = build_review_queue(pd.read_csv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(args.output, index=False)
    print(f"Wrote {len(queue)} ranked transactions to {args.output}")


if __name__ == "__main__":
    main()
