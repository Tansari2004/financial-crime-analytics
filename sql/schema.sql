CREATE TABLE transactions (
    transaction_id VARCHAR(32) PRIMARY KEY,
    account_id VARCHAR(32) NOT NULL,
    counterparty_id VARCHAR(32) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    country CHAR(2) NOT NULL,
    counterparty_country CHAR(2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    account_age_days INTEGER NOT NULL
);

CREATE TABLE review_queue (
    transaction_id VARCHAR(32) PRIMARY KEY REFERENCES transactions(transaction_id),
    risk_score NUMERIC(5, 2) NOT NULL,
    risk_band VARCHAR(10) NOT NULL,
    risk_reason TEXT NOT NULL,
    review_status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
