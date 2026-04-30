CREATE TABLE IF NOT EXISTS sorts (
    id              SERIAL PRIMARY KEY,
    input_numbers   INT[] NOT NULL,
    sorted_numbers  INT[] NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
