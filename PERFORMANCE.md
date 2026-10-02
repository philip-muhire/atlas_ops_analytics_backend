# Day 17 Performance & Security Writeup

## 1. Query Execution Plan Analysis (`EXPLAIN QUERY PLAN`)
- **Unindexed Execution Strategy:** `SCAN audit_logs`
  - **Behavior:** Full table scan requiring sequential inspection of all rows.
  - **Performance Impact:** High CPU overhead; scales linearly $O(N)$ with dataset growth.
- **Indexed Execution Strategy:** `SEARCH audit_logs USING INDEX idx_audit_logs_user_id (user_id=?)`
  - **Behavior:** B-Tree index lookup with targeted row fetches.
  - **Performance Impact:** Logarithmic time complexity $O(\log N)$, dramatically improving execution speed.

## 2. Security Mandate: Parameterized Queries
- **Standing Rule:** Zero string interpolation (`f"SELECT ... {var}"`) in database interaction layers.
- **Implementation:** All inputs bind through database driver placeholder tuples (`?` syntax in SQLite).
- **Protection:** Completely eliminates SQL Injection vectors by decoupling database command parsing from user-supplied data values.
