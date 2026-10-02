import sqlite3

DB_PATH = "saas_analytics.db"
VIEWS_FILE = "views.sql"

def apply_and_query_views():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # 1. Apply views script to database engine
    with open(VIEWS_FILE, "r") as f:
        views_script = f.read()
    
    cursor.executescript(views_script)
    conn.commit()
    print("Database Views successfully created and updated!\n")

    # 2. Query View 1: Customer Health 360
    print("=" * 75)
    print(" VIEW 1: CUSTOMER HEALTH 360 REPORT ")
    print("=" * 75)
    cursor.execute("SELECT * FROM v_customer_health_360;")
    headers = [desc[0] for desc in cursor.description]
    print(" | ".join(headers))
    print("-" * 75)
    for row in cursor.fetchall():
        print(" | ".join(str(item) for item in row))
    print("\n")

    # 3. Query View 2: Unresolved Support SLA Queue
    print("=" * 75)
    print(" VIEW 2: UNRESOLVED SLA QUEUE (PRIORITIZED BY TIER & SEVERITY) ")
    print("=" * 75)
    cursor.execute("SELECT * FROM v_unresolved_sla_queue;")
    headers = [desc[0] for desc in cursor.description]
    print(" | ".join(headers))
    print("-" * 75)
    for row in cursor.fetchall():
        print(" | ".join(str(item) for item in row))
    print("\n")

    conn.close()

if __name__ == "__main__":
    apply_and_query_views()
