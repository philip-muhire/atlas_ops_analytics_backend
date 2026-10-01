-- Enforce relational integrity in SQLite (disabled by default)
PRAGMA foreign_keys = ON;

-- 1. CUSTOMERS TABLE
-- Tracks enterprise accounts and primary contact info.
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL CHECK (tier IN ('starter', 'pro', 'enterprise')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. SUBSCRIPTIONS TABLE
-- Connects customers to recurring plans and tracks revenue streams (MRR).
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    plan_tier TEXT NOT NULL CHECK (plan_tier IN ('starter', 'pro', 'enterprise')),
    mrr_amount REAL NOT NULL CHECK (mrr_amount >= 0),
    status TEXT NOT NULL CHECK (status IN ('active', 'canceled', 'past_due')),
    start_date DATETIME NOT NULL,
    end_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 3. INVOICES TABLE
-- Financial billing records generated per subscription billing cycle.
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    amount_due REAL NOT NULL CHECK (amount_due >= 0),
    due_date DATETIME NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'unpaid', 'paid', 'void')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id) ON DELETE CASCADE
);

-- 4. PAYMENTS TABLE
-- Ledger of actual funds transferred against invoices (supports partial payments).
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    amount_paid REAL NOT NULL CHECK (amount_paid > 0),
    payment_method TEXT NOT NULL CHECK (payment_method IN ('stripe', 'wire', 'card')),
    paid_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE
);

-- 5. SUPPORT TICKETS TABLE
-- Operational support demand, used to evaluate ticket volume vs SLA metrics.
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('billing', 'technical', 'onboarding')),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- NATURAL JOIN INDEXES (Preempting Query Performance for Day 17)
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer ON subscriptions(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_subscription ON invoices(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_customer ON support_tickets(customer_id);
