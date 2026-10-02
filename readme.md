# Project 3: SaaS Analytics Backend

An enterprise-grade relational database backend for Atlas Ops, handling customer accounts, subscriptions, billing invoices, payments, and operational support tickets. Built with strict 3NF normalization, transactional ACID guarantees, parameterized security, performance indexing, and comprehensive integration testing.

## System Architecture & Entity Relationship Diagram (ERD)

```text
 [ customers ] 1 ───< N [ subscriptions ] 1 ───< N [ invoices ] 1 ───< N [ payments ]
       │
       └───< N [ support_tickets ]

Relational Schema Design (3NF)
customers: Core account entity (customer_id, company_name, email, tier).

subscriptions: Recurring contracts (subscription_id, customer_id, plan_tier, mrr_amount, status).

invoices: Billing ledgers (invoice_id, subscription_id, amount_due, due_date, status).

payments: Transaction records (payment_id, invoice_id, amount_paid, payment_method).

support_tickets: Operations tracker (ticket_id, customer_id, category, priority, status).


Technical Highlights & Requirements Fulfilled
1. Data Integrity & Constraints
Referential integrity enforced at the schema level via FOREIGN KEY ... ON DELETE CASCADE.

Data value boundaries enforced using CHECK constraints (e.g., mrr_amount >= 0, tier enumerations).

Mandatory foreign key enforcement explicitly configured (PRAGMA foreign_keys = ON;).

2. Business Intelligence & Reporting Views
Saved database views (views.sql) for core business reporting:

v_customer_health_360: Consolidated metric combining account tier, active MRR, paid invoice volume, and open ticket count.

v_unresolved_sla_queue: SLA prioritization queue sorting tickets by customer tier and severity.


3. Performance Tuning (EXPLAIN QUERY PLAN)Index coverage applied to all natural join and lookup keys (idx_subscriptions_customer, idx_invoices_subscription, idx_audit_logs_user_id).Verified execution transformation from full table scans (SCAN) to $O(\log N)$ index searches (SEARCH USING INDEX).


4. Security & Access Control
Parameterized Queries Only: Strict ban on string interpolation; all variables bind via parameter placeholders (?).

Least-Privilege Roles: Read-only connections (mode=ro) isolated from transactional write operations.

5. ACID Transactional Engine
Operational state changes wrapped in explicit BEGIN TRANSACTION / COMMIT / ROLLBACK blocks.

Guaranteed all-or-nothing writes across invoices, payments, and subscription statuses.

Project Structure & Execution Guide
atlas_ops_analytics_backend/
├── schema.sql              # 3NF Schema & Index definitions
├── init_db.py              # Schema initialization script
├── seed_db.py              # Deterministic test dataset generator
├── queries.sql             # Analytics SQL reporting library (MRR, Churn, SLAs)
├── run_reports.py          # Reporting execution script
├── views.sql               # Database views definition file
├── run_views.py            # View execution runner
├── performance.py          # EXPLAIN QUERY PLAN benchmarking script
├── security_guard.py       # Parameterized SQL security verification script
├── transaction_engine.py   # Transactional backend processing engine
├── test_backend.py         # Pytest integration test suite
├── PERFORMANCE.md          # Query performance & security writeup
└── README.md               # Backend system documentation

Running the Backend Pipeline
1. Initialize & Seed Database:

python3 init_db.py
python3 seed_db.py


2. Execute Analytics Reports & Views:
python3 run_reports.py
python3 run_views.py

3. Run Transaction Engine & Security Checks:

python3 performance.py
python3 transaction_engine.py

4. Execute Automated Integration Tests: pytest test_backend.py -v

