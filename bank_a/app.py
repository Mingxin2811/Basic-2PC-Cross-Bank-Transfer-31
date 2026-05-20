from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = "../databases/bank_a.db"


# =========================
# Home Route
# =========================
@app.route('/')
def home():
    return "Bank A Service is running"


# =========================
# Get All Accounts
# =========================
@app.route('/accounts', methods=['GET'])
def get_accounts():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts")
    rows = cursor.fetchall()

    conn.close()

    accounts = []

    for row in rows:
        accounts.append({
            "account_id": row[0],
            "owner_name": row[1],
            "balance": row[2]
        })

    return jsonify(accounts)


# =========================
# PREPARE Phase
# =========================
@app.route('/prepare', methods=['POST'])
def prepare():
    data = request.get_json()

    from_account = data.get("from_account")
    amount = data.get("amount")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM accounts WHERE account_id = ?",
        (from_account,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({
            "bank": "Bank_A",
            "status": "ABORT",
            "reason": "Sender account not found"
        })

    balance = row[0]

    if balance >= amount:
        return jsonify({
            "bank": "Bank_A",
            "status": "READY",
            "reason": "Sufficient balance"
        })
    else:
        return jsonify({
            "bank": "Bank_A",
            "status": "ABORT",
            "reason": "Insufficient balance"
        })


# =========================
# Run Server
# =========================
# =========================
# COMMIT Phase
# =========================
@app.route('/commit', methods=['POST'])
def commit():
    data = request.get_json()

    from_account = data.get("from_account")
    amount = data.get("amount")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET balance = balance - ? WHERE account_id = ?",
        (amount, from_account)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "bank": "Bank_A",
        "status": "COMMITTED",
        "message": f"Deducted {amount} from {from_account}"
    })
if __name__ == '__main__':
    app.run(port=5001, debug=True)