import sqlite3
from datetime import datetime, timedelta

DB_PATH = "saas_analytics.db"

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Clear existing records to ensure idempotent execution
    tables = ["payments", "invoices", "subscriptions", "support_tickets", "customers"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table};")

    # 1. Seed Customers
    customers = [
        ('cust_001', 'Acme Corp', 'billing@acme.com', 'enterprise', '2025-01-15 08:00:00'),
        ('cust_002', 'Beta Logistics', 'ops@betalogistics.com', 'pro', '2025-02-01 10:30:00'),
        ('cust_003', 'Gamma Media', 'finance@gammamedia.com', 'starter', '2025-03-10 11:15:00'),
        ('cust_004', 'Delta Tech', 'admin@deltatech.io', 'pro', '2025-04-05 14:20:00'),
        ('cust_005', 'Epsilon Retail', 'info@epsilon.com', 'starter', '2025-05-12 09:00:00')
    ]
    cursor.executemany(
        "INSERT INTO customers (customer_id, company_name, email, tier, created_at) VALUES (?, ?, ?, ?, ?);",
        customers
    )

    # 2. Seed Subscriptions
    subscriptions = [
        ('sub_101', 'cust_001', 'enterprise', 2500.00, 'active', '2025-01-15 08:00:00', None),
        ('sub_102', 'cust_002', 'pro', 499.00, 'active', '2025-02-01 10:30:00', None),
        ('sub_103', 'cust_003', 'starter', 99.00, 'canceled', '2025-03-10 11:15:00', '2025-08-01 00:00:00'),
        ('sub_104', 'cust_004', 'pro', 499.00, 'past_due', '2025-04-05 14:20:00', None),
        ('sub_105', 'cust_005', 'starter', 99.00, 'active', '2025-05-12 09:00:00', None)
    ]
    cursor.executemany(
        "INSERT INTO subscriptions (subscription_id, customer_id, plan_tier, mrr_amount, status, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?);",
        subscriptions
    )

    # 3. Seed Invoices
    invoices = [
        ('inv_501', 'sub_101', 2500.00, '2025-09-01 00:00:00', 'paid', '2025-08-25 00:00:00'),
        ('inv_502', 'sub_102', 499.00, '2025-09-01 00:00:00', 'paid', '2025-08-25 00:00:00'),
        ('inv_503', 'sub_104', 499.00, '2025-09-01 00:00:00', 'unpaid', '2025-08-25 00:00:00'),
        ('inv_504', 'sub_105', 99.00, '2025-09-01 00:00:00', 'paid', '2025-08-25 00:00:00')
    ]
    cursor.executemany(
        "INSERT INTO invoices (invoice_id, subscription_id, amount_due, due_date, status, created_at) VALUES (?, ?, ?, ?, ?, ?);",
        invoices
    )

    # 4. Seed Support Tickets
    tickets = [
        ('tkt_901', 'cust_001', 'technical', 'high', 'resolved', '2025-08-10 10:00:00', '2025-08-10 12:30:00'),
        ('tkt_902', 'cust_001', 'billing', 'medium', 'closed', '2025-08-15 14:00:00', '2025-08-15 15:00:00'),
        ('tkt_903', 'cust_002', 'technical', 'critical', 'in_progress', '2025-09-01 09:00:00', None),
        ('tkt_904', 'cust_003', 'onboarding', 'low', 'closed', '2025-03-12 11:00:00', '2025-03-12 16:00:00'),
        ('tkt_905', 'cust_004', 'billing', 'high', 'open', '2025-09-02 08:30:00', None),
        ('tkt_906', 'cust_002', 'technical', 'medium', 'resolved', '2025-08-20 11:00:00', '2025-08-20 14:00:00')
    ]
    cursor.executemany(
        "INSERT INTO support_tickets (ticket_id, customer_id, category, priority, status, created_at, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?);",
        tickets
    )

    conn.commit()
    print("Database seeded with sample operational data successfully!")
    conn.close()

if __name__ == "__main__":
    seed_database()
