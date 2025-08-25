CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  cost NUMERIC(12,4),
  price NUMERIC(12,4),
  currency TEXT DEFAULT 'EUR',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  country TEXT,
  segment TEXT,
  salesperson_id TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  customer_id TEXT REFERENCES customers(id),
  date DATE NOT NULL,
  product_id TEXT REFERENCES products(id),
  qty NUMERIC(12,4) NOT NULL,
  net_revenue NUMERIC(12,4) NOT NULL,
  cogs NUMERIC(12,4),
  currency TEXT DEFAULT 'EUR'
);

CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY,
  source TEXT,
  medium TEXT,
  campaign_name TEXT,
  date DATE,
  cost NUMERIC(12,4) DEFAULT 0,
  clicks INT,
  impressions INT,
  sessions INT,
  purchases INT,
  revenue NUMERIC(12,4)
);

CREATE TABLE IF NOT EXISTS ga_sessions (
  date DATE,
  source TEXT,
  medium TEXT,
  country TEXT,
  sessions INT,
  transactions INT,
  revenue NUMERIC(12,4),
  users INT,
  bounces INT,
  PRIMARY KEY(date, source, medium, country)
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingestion_logs (
  id TEXT PRIMARY KEY,
  source TEXT,
  target_table TEXT,
  mode TEXT,
  rows INT,
  status TEXT,
  message TEXT,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
