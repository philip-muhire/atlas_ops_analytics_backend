import sqlite3

DB_PATH = "saas_analytics.db"

def fetch_customer_safe(email_input: str):
    """
    SECURE: Uses parameterized query placeholders (?) to pass parameters safely.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Parameterized query — SQL syntax and data inputs are kept completely isolated
    query = "SELECT customer_id, company_name, email, tier FROM customers WHERE email = ?;"
    
    # Python sqlite3 safely escapes inputs regardless of malicious string content
    cursor.execute(query, (email_input,))
    result = cursor.fetchone()
    conn.close()
    return result

def create_ticket_safe(customer_id: str, category: str, priority: str, ticket_id: str):
    """
    SECURE: Uses parameterized inputs for state-changing write operations.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    query = """
        INSERT INTO support_tickets (ticket_id, customer_id, category, priority, status)
        VALUES (?, ?, ?, ?, 'open');
    """
    
    cursor.execute(query, (ticket_id, customer_id, category, priority))
    conn.commit()
    conn.close()
    print(f"Ticket '{ticket_id}' successfully created for Customer '{customer_id}'.")

if __name__ == "__main__":
    print("=" * 70)
    print(" SECURITY TEST: Simulating SQL Injection Attempt ")
    print("=" * 70)

    # Malicious string attempt designed to bypass email checks
    malicious_input = "billing@acme.com' OR '1'='1"

    print(f"Testing input: {malicious_input}")
    result = fetch_customer_safe(malicious_input)

    if result is None:
        print("\n[SUCCESS] Security Guardrail Active: Injection string was safely neutralized as a literal string value, returning NO match.")
    else:
        print(f"\n[VULNERABLE] Unexpected record returned: {result}")
