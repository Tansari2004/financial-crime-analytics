# Power BI dashboard specification

The pipeline export at `data/sample/investigator_queue.csv` is designed as the first dashboard input.

## Recommended pages

1. **Investigation overview** — open alerts, amount at risk, alerts by risk band and trend over time.
2. **Review queue** — sortable table with transaction, account, amount, score and explanation.
3. **Case detail** — account activity, counterparties and triggered indicators.

## Example measures

```DAX
Open Alerts = CALCULATE(COUNTROWS(ReviewQueue), ReviewQueue[review_status] = "open")

Open Financial Exposure =
CALCULATE(SUM(ReviewQueue[amount]), ReviewQueue[review_status] = "open")

High-Risk Alerts =
CALCULATE(COUNTROWS(ReviewQueue), ReviewQueue[risk_band] = "high")
```

No `.pbix` file is committed yet. A screenshot and downloadable report will be added once the dashboard is complete.
