from flask import Flask, jsonify
import requests

app = Flask(__name__)

BANK_A_URL = "http://127.0.0.1:5001"
BANK_B_URL = "http://127.0.0.1:5002"

# =========================
# Home Route
# =========================
@app.route('/')
def home():
    return "Coordinator is running"


# =========================
# Check All Nodes
# =========================
@app.route('/check_nodes', methods=['GET'])
def check_nodes():

    result = {}

    # Check Bank A
    try:
        response_a = requests.get(f"{BANK_A_URL}/accounts")

        if response_a.status_code == 200:
            result["Bank_A"] = "ONLINE"
        else:
            result["Bank_A"] = "ERROR"

    except:
        result["Bank_A"] = "OFFLINE"

    # Check Bank B
    try:
        response_b = requests.get(f"{BANK_B_URL}/accounts")

        if response_b.status_code == 200:
            result["Bank_B"] = "ONLINE"
        else:
            result["Bank_B"] = "ERROR"

    except:
        result["Bank_B"] = "OFFLINE"

    return jsonify(result)


# =========================
# Get All Accounts
# =========================
@app.route('/all_accounts', methods=['GET'])
def all_accounts():

    data = {}

    # Get Bank A accounts
    try:
        response_a = requests.get(f"{BANK_A_URL}/accounts")
        data["Bank_A"] = response_a.json()

    except:
        data["Bank_A"] = "Cannot connect"

    # Get Bank B accounts
    try:
        response_b = requests.get(f"{BANK_B_URL}/accounts")
        data["Bank_B"] = response_b.json()

    except:
        data["Bank_B"] = "Cannot connect"

    return jsonify(data)


# =========================
# Run Server
# =========================
if __name__ == '__main__':
    app.run(port=5000, debug=True)