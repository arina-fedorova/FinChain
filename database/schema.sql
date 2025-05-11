CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE currencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT,
    symbol TEXT,
    iso_number TEXT
);

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name TEXT NOT NULL,
    currency_id UUID REFERENCES currencies(id),
    initial_balance NUMERIC NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE,
    type TEXT,
    rate_source TEXT
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    account_id UUID REFERENCES accounts(id),
    amount NUMERIC NOT NULL,
    converted_amount NUMERIC,
    type TEXT,
    category_id UUID REFERENCES categories(id),
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE transfers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    from_account_id UUID REFERENCES accounts(id),
    to_account_id UUID REFERENCES accounts(id),
    amount NUMERIC NOT NULL,
    converted_amount NUMERIC,
    rate_used NUMERIC,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name TEXT NOT NULL,
    emoji TEXT
);

CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    category_id UUID REFERENCES categories(id),
    account_id UUID REFERENCES accounts(id),
    amount NUMERIC NOT NULL,
    period TEXT,
    start_date DATE,
    end_date DATE
);

CREATE TABLE exchange_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    from_currency_id UUID REFERENCES currencies(id),
    to_currency_id UUID REFERENCES currencies(id),
    rate NUMERIC NOT NULL,
    source TEXT,
    is_cash BOOLEAN DEFAULT FALSE
);

CREATE TABLE job_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT
);

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type_id UUID REFERENCES job_types(id),
    payload JSONB,
    max_run_at TIMESTAMPTZ,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE agent_prompt_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT
);

CREATE TABLE agent_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_id UUID REFERENCES agent_prompt_types(id),
    model TEXT NOT NULL,
    prompt TEXT NOT NULL,
    instructions TEXT,
    is_active BOOLEAN DEFAULT TRUE
);