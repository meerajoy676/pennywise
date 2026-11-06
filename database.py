import sqlite3
from pathlib import Path
from datetime import date


class FinanceDatabase:
    """Handles all SQLite storage for the app."""

    def __init__(self, database_path=None):
        if database_path is None:
            database_path = Path(__file__).resolve().with_name("pennywise_data.db")
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT DEFAULT '',
                transaction_date TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                opening_balance REAL NOT NULL DEFAULT 0,
                expected_income REAL NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO settings
            (id, opening_balance, expected_income)
            VALUES (1, 0, 0)
        """)
        self.connection.commit()

    def get_settings(self):
        return self.connection.execute(
            "SELECT opening_balance, expected_income FROM settings WHERE id = 1"
        ).fetchone()

    def save_settings(self, opening_balance, expected_income):
        self.connection.execute("""
            UPDATE settings
            SET opening_balance = ?, expected_income = ?
            WHERE id = 1
        """, (opening_balance, expected_income))
        self.connection.commit()

    def fetch_transactions(self, month=None, limit=None):
        query = "SELECT * FROM transactions"
        params = []
        if month:
            query += " WHERE substr(transaction_date, 1, 7) = ?"
            params.append(month)
        query += " ORDER BY transaction_date DESC, id DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        return self.connection.execute(query, params).fetchall()

    def add_transaction(self, kind, amount, category, description, transaction_date):
        self.connection.execute("""
            INSERT INTO transactions
            (kind, amount, category, description, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (kind, amount, category, description, transaction_date))
        self.connection.commit()

    def delete_transaction(self, transaction_id):
        self.connection.execute(
            "DELETE FROM transactions WHERE id = ?", (transaction_id,)
        )
        self.connection.commit()

    def reset_all_data(self):
        """Delete all transactions and restore settings to their defaults."""
        self.connection.execute("DELETE FROM transactions")
        self.connection.execute("DELETE FROM sqlite_sequence WHERE name = 'transactions'")
        self.connection.execute("""
            UPDATE settings
            SET opening_balance = 0, expected_income = 0
            WHERE id = 1
        """)
        self.connection.commit()

    def close(self):
        self.connection.close()
