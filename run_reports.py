import sqlite3
from pathlib import Path

DB_PATH = "saas_analytics.db"
QUERY_FILE = "queries.sql"

def execute_reports():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(QUERY_FILE, "r") as f:
        sql_script = f.read()

    # Split individual queries separated by semicolons
    raw_queries = [q.strip() for q in sql_script.split(";") if q.strip()]

    report_titles = [
        "REPORT 1: Active Monthly Recurring Revenue (MRR) by Tier",
        "REPORT 2: Subscription Churn & Status Breakdown",
        "REPORT 3: Support Ticket Volume & SLA Workload"
    ]

    for index, query in enumerate(raw_queries):
        print("=" * 70)
        print(f" {report_titles[index]} ")
        print("=" * 70)

        cursor.execute(query)
        # Extract column header names from cursor description
        headers = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Format output cleanly
        print(f"{' | '.join(headers)}")
        print("-" * 70)
        for row in rows:
            print(" | ".join(str(item) for item in row))
        print("\n")

    conn.close()

if __name__ == "__main__":
    execute_reports()
