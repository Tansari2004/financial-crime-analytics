SELECT
    q.transaction_id,
    t.account_id,
    t.counterparty_id,
    t.transaction_timestamp,
    t.amount,
    t.country,
    t.counterparty_country,
    q.risk_score,
    q.risk_band,
    q.risk_reason
FROM review_queue AS q
JOIN transactions AS t USING (transaction_id)
WHERE q.review_status = 'open'
ORDER BY q.risk_score DESC, t.amount DESC;
