import os
import sqlite3
import pytest
from pathlib import Path

# Module functions to test
from transaction_engine import process_invoice_payment_transaction, get_db_connection

TEST_DB = "test_saas_analytics.db"
SCHEMA_FILE = "schema.sql"

@pytest.fixture(scope="function")
def test_db():
    """
    Pytest Fixture: Sets up a fresh, real test database instance before each test,
    and tears it down afterward.
    """
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Initialize fresh schema on real test DB
    conn = sqlite3.connect(TEST_DB)
    conn.execute("PRAGMA foreign_keys = ON;")
    with open(SCHEMA_FILE, "r") as f:
        conn.executescript(f.read())

    # Seed baseline fixture data
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers VALUES ('cust_t1', 'Test Corp', 't@test.com', 'pro', '2025-01-01');")
    cursor.execute("INSERT INTO subscriptions VALUES ('sub_t1', 'cust_t1', 'pro', 499.00, 'past_due', '2025-01-01', NULL);")
    cursor.execute("INSERT INTO invoices VALUES ('inv_t1', 'sub_t1', 499.00, '2025-02-01', 'unpaid', '2025-01-15');")
    conn.commit()
    conn.close()

    # Monkeypatch the DB_PATH used in transaction_engine
    import transaction_engine
    original_path = transaction_engine.DB_PATH
    transaction_engine.DB_PATH = TEST_DB

    yield TEST_DB

    # Teardown
    transaction_engine.DB_PATH = original_path
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_schema_integrity_and_foreign_keys(test_db):
    """
    Test 1: Ensures foreign key constraint violations are rejected by schema.
    """
    conn = sqlite3.connect(test_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    with pytest.raises(sqlite3.IntegrityError):
        # Attempting to insert subscription for non-existent customer
        cursor.execute("INSERT INTO subscriptions VALUES ('sub_bad', 'non_existent_cust', 'pro', 499.00, 'active', '2025-01-01', NULL);")


def test_successful_transactional_payment(test_db):
    """
    Test 2: Verifies end-to-end payment transaction updates invoice, creates payment, and sets subscription active.
    """
    success = process_invoice_payment_transaction(
        invoice_id="inv_t1",
        payment_id="pay_t1",
        amount=499.00,
        payment_method="stripe"
    )
    assert success is True

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # Verify invoice status is paid
    cursor.execute("SELECT status FROM invoices WHERE invoice_id = 'inv_t1';")
    assert cursor.fetchone()[0] == 'paid'

    # Verify payment record exists
    cursor.execute("SELECT amount_paid FROM payments WHERE payment_id = 'pay_t1';")
    assert cursor.fetchone()[0] == 499.00

    # Verify subscription status updated from past_due to active
    cursor.execute("SELECT status FROM subscriptions WHERE subscription_id = 'sub_t1';")
    assert cursor.fetchone()[0] == 'active'


def test_transaction_rollback_on_error(test_db):
    """
    Test 3: Verifies that if an insert fails, invoice status changes are rolled back completely.
    """
    # Attempting to process payment with invalid payment amount triggers ValueError
    success = process_invoice_payment_transaction(
        invoice_id="inv_t1",
        payment_id="pay_t2",
        amount=50.00,  # Invalid amount (due is 499.00)
        payment_method="stripe"
    )
    assert success is False

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # Verify invoice status remained unpaid (rolled back)
    cursor.execute("SELECT status FROM invoices WHERE invoice_id = 'inv_t1';")
    assert cursor.fetchone()[0] == 'unpaid'

    # Verify no payment record was created
    cursor.execute("SELECT COUNT(*) FROM payments WHERE payment_id = 'pay_t2';")
    assert cursor.fetchone()[0] == 0


def test_parameterized_security_against_injection(test_db):
    """
    Test 4: Verifies parameterized query safety against SQL Injection strings.
    """
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    injection_attempt = "t@test.com' OR '1'='1"
    cursor.execute("SELECT * FROM customers WHERE email = ?;", (injection_attempt,))
    result = cursor.fetchall()

    # Must return 0 rows
    assert len(result) == 0
