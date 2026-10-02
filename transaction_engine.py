import sqlite3
import logging
from typing import Tuple, Optional

# Setup operational logging for slow-query and transaction auditing
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AnalyticsBackend")

DB_PATH = "saas_analytics.db"

def get_db_connection(readonly: bool = False) -> sqlite3.Connection:
    """
    Simulates Least-Privilege Access Roles.
    URI mode with 'ro' opens the database in strict read-only mode for reporting.
    """
    if readonly:
        # SQLite Read-Only connection
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def process_invoice_payment_transaction(invoice_id: str, payment_id: str, amount: float, payment_method: str) -> bool:
    """
    ATOMIC TRANSACTION: Updates invoice status and inserts a payment record.
    Guarantees ACID properties: if payment insertion fails, invoice status update rolls back.
    """
    conn = get_db_connection(readonly=False)
    cursor = conn.cursor()

    try:
        # 1. Begin explicit transaction
        cursor.execute("BEGIN TRANSACTION;")

        # 2. Verify invoice existence and amount
        cursor.execute("SELECT subscription_id, amount_due, status FROM invoices WHERE invoice_id = ?;", (invoice_id,))
        invoice = cursor.fetchone()

        if not invoice:
            raise ValueError(f"Invoice '{invoice_id}' does not exist.")

        sub_id, amount_due, status = invoice

        if status == 'paid':
            raise ValueError(f"Invoice '{invoice_id}' is already fully paid.")

        if amount < amount_due:
            raise ValueError(f"Payment amount (${amount}) is less than amount due (${amount_due}).")

        # 3. Update Invoice Status
        cursor.execute("UPDATE invoices SET status = 'paid' WHERE invoice_id = ?;", (invoice_id,))

        # 4. Record Payment Ledger
        cursor.execute("""
            INSERT INTO payments (payment_id, invoice_id, amount_paid, payment_method)
            VALUES (?, ?, ?, ?);
        """, (payment_id, invoice_id, amount, payment_method))

        # 5. Update Subscription Status to active (if it was past_due)
        cursor.execute("UPDATE subscriptions SET status = 'active' WHERE subscription_id = ?;", (sub_id,))

        # Commit all changes if all operations succeed
        conn.commit()
        logger.info(f"[TRANSACTION SUCCESS] Invoice '{invoice_id}' paid via Payment '{payment_id}'.")
        return True

    except Exception as e:
        # Rollback all changes if ANY error occurs
        conn.rollback()
        logger.error(f"[TRANSACTION ROLLBACK] Payment processing failed for Invoice '{invoice_id}'. Reason: {str(e)}")
        return False

    finally:
        conn.close()


def query_reporting_readonly(query: str, params: Tuple = ()) -> list:
    """
    Executes reporting queries using a Read-Only role connection.
    Attempts to mutate data via this function will throw an exception.
    """
    conn = get_db_connection(readonly=True)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print(" 1. TESTING SUCCESSFUL ATOMIC TRANSACTION ")
    print("=" * 70)
    # inv_503 is unpaid in our seed data ($499.00 due)
    success = process_invoice_payment_transaction(
        invoice_id="inv_503", 
        payment_id="pay_801", 
        amount=499.00, 
        payment_method="stripe"
    )

    print("\n" + "=" * 70)
    print(" 2. TESTING ROLLBACK ON FAILURE (Insufficient Payment Amount) ")
    print("=" * 70)
    # Attempting to pay an invoice with insufficient amount triggers failure and rollback
    failed_txn = process_invoice_payment_transaction(
        invoice_id="inv_501", 
        payment_id="pay_802", 
        amount=10.00, 
        payment_method="card"
    )

    print("\n" + "=" * 70)
    print(" 3. TESTING LEAST-PRIVILEGE READ-ONLY ROLE GUARDRAILS ")
    print("=" * 70)
    try:
        # Attempting an INSERT via read-only connection
        conn_ro = get_db_connection(readonly=True)
        conn_ro.cursor().execute("DELETE FROM customers;")
    except sqlite3.OperationalError as e:
        print(f"[SUCCESS] Read-Only Security Active: Action blocked. Reason: {e}")
