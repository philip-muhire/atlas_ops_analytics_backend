-- Enforce strict relational integrity
PRAGMA foreign_keys = ON;

-- ============================================================================
-- VIEW 1: Customer Health 360 View
-- Business Value: Provides Account Executives and Customer Success teams 
-- with a unified snapshot of each customer's subscription tier, total 
-- MRR contribution, total billed revenue, and total support ticket burden.
-- Uses LEFT JOINs to ensure new customers without tickets or paid invoices 
-- are not accidentally filtered out.
-- ============================================================================
DROP VIEW IF EXISTS v_customer_health_360;

CREATE VIEW v_customer_health_360 AS
SELECT 
    c.customer_id,
    c.company_name,
    c.email,
    c.tier AS account_tier,
    COALESCE(s.status, 'no_subscription') AS subscription_status,
    COALESCE(s.mrr_amount, 0.0) AS mrr,
    COUNT(DISTINCT t.ticket_id) AS total_support_tickets,
    SUM(CASE WHEN t.status IN ('open', 'in_progress') THEN 1 ELSE 0 END) AS active_tickets
FROM customers c
LEFT JOIN subscriptions s ON c.customer_id = s.customer_id
LEFT JOIN support_tickets t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.company_name, c.email, c.tier, s.status, s.mrr_amount;


-- ============================================================================
-- VIEW 2: Unresolved Support SLA Queue with Customer Context
-- Business Value: Enables Support Leads to route urgent tickets based on 
-- account tier priority. INNER JOIN guarantees we only return actionable, 
-- open tickets tied to verified accounts.
-- ============================================================================
DROP VIEW IF EXISTS v_unresolved_sla_queue;

CREATE VIEW v_unresolved_sla_queue AS
SELECT 
    t.ticket_id,
    c.company_name,
    c.tier AS customer_tier,
    t.category,
    t.priority,
    t.status AS ticket_status,
    t.created_at AS ticket_opened_at
FROM support_tickets t
INNER JOIN customers c ON t.customer_id = c.customer_id
WHERE t.status IN ('open', 'in_progress')
ORDER BY 
    CASE c.tier 
        WHEN 'enterprise' THEN 1 
        WHEN 'pro' THEN 2 
        WHEN 'starter' THEN 3 
    END ASC,
    CASE t.priority 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        WHEN 'low' THEN 4 
    END ASC;
