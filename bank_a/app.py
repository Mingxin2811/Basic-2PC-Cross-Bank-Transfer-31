from flask import Flask, jsonify
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
# Run Server
# =========================
if __name__ == '__main__':
    app.run(port=5001, debug=True)