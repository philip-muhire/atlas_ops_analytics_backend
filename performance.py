import sqlite3
import time

DB_PATH = "saas_analytics.db"

def demonstrate_query_performance():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Setup unindexed performance test table
    cursor.execute("DROP TABLE IF EXISTS audit_logs;")
    cursor.execute("""
        CREATE TABLE audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Insert 20,000 dummy audit logs using parameterized batch inserts
    print("Populating 20,000 dummy logs for performance testing...")
    logs_data = [(f"user_{i % 500}", f"action_code_{i % 10}") for i in range(20000)]
    cursor.executemany("INSERT INTO audit_logs (user_id, action) VALUES (?, ?);", logs_data)
    conn.commit()

    test_query = "SELECT COUNT(*) FROM audit_logs WHERE user_id = ?;"
    target_user = ("user_250",)

    # 3. Diagnose BEFORE Indexing (Full Table Scan)
    print("\n" + "=" * 70)
    print(" 1. BEFORE INDEXING: Execution Plan Analysis ")
    print("=" * 70)
    cursor.execute(f"EXPLAIN QUERY PLAN {test_query}", target_user)
    plan_before = cursor.fetchall()
    for step in plan_before:
        print(f"Engine Plan Detail: {step[3]}")

    start_time = time.perf_counter()
    cursor.execute(test_query, target_user)
    result_before = cursor.fetchone()[0]
    time_before = (time.perf_counter() - start_time) * 1000  # convert to milliseconds
    print(f"Query Result Count: {result_before}")
    print(f"Execution Speed: {time_before:.4f} ms")

    # 4. Apply Covering Index
    print("\nApplying Index on column: user_id...")
    cursor.execute("CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);")
    conn.commit()

    # 5. Diagnose AFTER Indexing (Index Search)
    print("\n" + "=" * 70)
    print(" 2. AFTER INDEXING: Execution Plan Analysis ")
    print("=" * 70)
    cursor.execute(f"EXPLAIN QUERY PLAN {test_query}", target_user)
    plan_after = cursor.fetchall()
    for step in plan_after:
        print(f"Engine Plan Detail: {step[3]}")

    start_time = time.perf_counter()
    cursor.execute(test_query, target_user)
    result_after = cursor.fetchone()[0]
    time_after = (time.perf_counter() - start_time) * 1000
    print(f"Query Result Count: {result_after}")
    print(f"Execution Speed: {time_after:.4f} ms")

    conn.close()

if __name__ == "__main__":
    demonstrate_query_performance()
