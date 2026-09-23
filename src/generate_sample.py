from pathlib import Path

import numpy as np
import pandas as pd


def generate_transactions(rows: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    accounts = [f"ACC-{i:04d}" for i in range(1, 81)]
    counterparties = [f"CP-{i:04d}" for i in range(1, 151)]
    countries = np.array(["CA", "US", "GB", "AE", "JO"])
    timestamps = pd.Timestamp("2026-01-01") + pd.to_timedelta(
        rng.integers(0, 60 * 24 * 45, rows), unit="m"
    )
    amounts = np.round(rng.lognormal(mean=6.8, sigma=1.0, size=rows), 2)

    # Add a few deterministic edge cases so the demo always produces reviewable alerts.
    amounts[:5] = [25_000, 31_500, 48_000, 76_000, 120_000]

    frame = pd.DataFrame(
        {
            "transaction_id": [f"TX-{i:06d}" for i in range(1, rows + 1)],
            "account_id": rng.choice(accounts, rows),
            "counterparty_id": rng.choice(counterparties, rows),
            "timestamp": timestamps,
            "amount": amounts,
            "country": rng.choice(countries, rows, p=[0.72, 0.12, 0.06, 0.05, 0.05]),
            "counterparty_country": rng.choice(countries, rows),
            "transaction_type": rng.choice(["transfer", "wire", "card", "cash"], rows),
            "account_age_days": rng.integers(2, 3000, rows),
        }
    )
    frame.loc[:3, "account_age_days"] = [3, 8, 12, 20]
    return frame.sort_values("timestamp").reset_index(drop=True)


def main() -> None:
    output = Path("data/sample/transactions.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_transactions().to_csv(output, index=False)
    print(f"Wrote synthetic sample to {output}")


if __name__ == "__main__":
    main()
