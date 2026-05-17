import sqlite3
import os

# Tạo thư mục databases nếu chưa có
os.makedirs("databases", exist_ok=True)

# =========================
# BANK A DATABASE
# =========================

conn_a = sqlite3.connect("databases/bank_a.db")
cursor_a = conn_a.cursor()

cursor_a.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    owner_name TEXT,
    balance REAL
)
""")

cursor_a.execute("DELETE FROM accounts")

bank_a_data = [
    ("A001", "Alice", 5000),
    ("A002", "David", 3000)
]

cursor_a.executemany(
    "INSERT INTO accounts VALUES (?, ?, ?)",
    bank_a_data
)

conn_a.commit()
conn_a.close()

# =========================
# BANK B DATABASE
# =========================

conn_b = sqlite3.connect("databases/bank_b.db")
cursor_b = conn_b.cursor()

cursor_b.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    owner_name TEXT,
    balance REAL
)
""")

cursor_b.execute("DELETE FROM accounts")

bank_b_data = [
    ("B001", "Bob", 2000),
    ("B002", "Tom", 4000)
]

cursor_b.executemany(
    "INSERT INTO accounts VALUES (?, ?, ?)",
    bank_b_data
)

conn_b.commit()
conn_b.close()

print("Databases created successfully!")