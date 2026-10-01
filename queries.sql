-- ============================================================================
-- REPORT 1: Total Monthly Recurring Revenue (MRR) & Active Subscription Count
-- Business Value: Gives executives an accurate, real-time calculation of 
-- predictable monthly top-line revenue, excluding churned or past-due accounts.
-- ============================================================================
SELECT 
    plan_tier,
    COUNT(subscription_id) AS active_subscriptions,
    SUM(mrr_amount) AS total_mrr,
    AVG(mrr_amount) AS average_revenue_per_user
FROM subscriptions
WHERE status = 'active'
GROUP BY plan_tier
ORDER BY total_mrr DESC;


-- ============================================================================
-- REPORT 2: Subscription Churn Rate Analysis
-- Business Value: Identifies account losses by comparing active vs canceled 
-- accounts. High churn indicates product failure or customer dissatisfaction.
-- ============================================================================
SELECT 
    status,
    COUNT(subscription_id) AS subscription_count,
    ROUND(
        (COUNT(subscription_id) * 100.0 / (SELECT COUNT(*) FROM subscriptions)), 
        2
    ) AS percentage_of_total
FROM subscriptions
GROUP BY status;


-- ============================================================================
-- REPORT 3: Support Ticket Volume & SLA Workload by Category & Priority
-- Business Value: Shows Support Operations where bottlenecks lie. Filters 
-- specifically for high-demand areas having more than 1 ticket using HAVING.
-- ============================================================================
SELECT 
    category,
    priority,
    COUNT(ticket_id) AS total_tickets,
    SUM(CASE WHEN status IN ('open', 'in_progress') THEN 1 ELSE 0 END) AS unresolved_tickets
FROM support_tickets
GROUP BY category, priority
HAVING total_tickets >= 1
ORDER BY unresolved_tickets DESC, total_tickets DESC;
