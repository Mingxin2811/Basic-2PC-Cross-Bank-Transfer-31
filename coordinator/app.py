from flask import Flask, jsonify, request
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

BANK_A_URL = "http://127.0.0.1:5001"
BANK_B_URL = "http://127.0.0.1:5002"

LOG_FILE = "../logs/coordinator.log"
PENDING_FILE = "../logs/pending_transactions.json"

os.makedirs("../logs", exist_ok=True)

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

    try:
        response_a = requests.get(f"{BANK_A_URL}/accounts")
        result["Bank_A"] = "ONLINE" if response_a.status_code == 200 else "ERROR"
    except:
        result["Bank_A"] = "OFFLINE"

    try:
        response_b = requests.get(f"{BANK_B_URL}/accounts")
        result["Bank_B"] = "ONLINE" if response_b.status_code == 200 else "ERROR"
    except:
        result["Bank_B"] = "OFFLINE"

    return jsonify(result)


# =========================
# Get All Accounts
# =========================
@app.route('/all_accounts', methods=['GET'])
def all_accounts():
    data = {}

    try:
        response_a = requests.get(f"{BANK_A_URL}/accounts")
        data["Bank_A"] = response_a.json()
    except:
        data["Bank_A"] = "Cannot connect"

    try:
        response_b = requests.get(f"{BANK_B_URL}/accounts")
        data["Bank_B"] = response_b.json()
    except:
        data["Bank_B"] = "Cannot connect"

    return jsonify(data)


# =========================
# PREPARE Phase Test
# =========================
@app.route('/prepare_transfer', methods=['POST'])
def prepare_transfer():
    data = request.get_json()

    transaction = {
        "from_account": data.get("from_account"),
        "to_account": data.get("to_account"),
        "amount": data.get("amount")
    }

    result = {}

    try:
        response_a = requests.post(
            f"{BANK_A_URL}/prepare",
            json=transaction
        )
        result["Bank_A"] = response_a.json()
    except:
        result["Bank_A"] = {
            "status": "ABORT",
            "reason": "Cannot connect to Bank A"
        }

    try:
        response_b = requests.post(
            f"{BANK_B_URL}/prepare",
            json=transaction
        )
        result["Bank_B"] = response_b.json()
    except:
        result["Bank_B"] = {
            "status": "ABORT",
            "reason": "Cannot connect to Bank B"
        }

    if (
        result["Bank_A"]["status"] == "READY"
        and result["Bank_B"]["status"] == "READY"
    ):
        final_decision = "READY_TO_COMMIT"
    else:
        final_decision = "ABORT"

    return jsonify({
        "transaction": transaction,
        "participants": result,
        "coordinator_decision": final_decision
    })


# =========================
# Run Server
# =========================
# =========================
# =========================
# Write Transaction Log
# =========================
def write_log(transaction_id, state, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = f"{timestamp} | {transaction_id} | {state} | {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_line)

# =========================
# Pending Transaction Helpers
# =========================
def load_pending_transactions():
    if not os.path.exists(PENDING_FILE):
        return {}

    with open(PENDING_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def save_pending_transactions(pending):
    with open(PENDING_FILE, "w", encoding="utf-8") as file:
        json.dump(pending, file, indent=4)


def add_pending_transaction(transaction):
    pending = load_pending_transactions()
    pending[transaction["transaction_id"]] = transaction
    save_pending_transactions(pending)


def remove_pending_transaction(transaction_id):
    pending = load_pending_transactions()

    if transaction_id in pending:
        del pending[transaction_id]

    save_pending_transactions(pending)
# Full 2PC Transfer
# =========================
# =========================
# Full 2PC Transfer with Logging
# =========================
@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()

    transaction_id = data.get("transaction_id", "TXN001")

    transaction = {
        "transaction_id": transaction_id,
        "from_account": data.get("from_account"),
        "to_account": data.get("to_account"),
        "amount": data.get("amount")
    }

    result = {}

    # =========================
    # INITIAL
    # =========================
    write_log(
        transaction_id,
        "INITIAL",
        f"Transaction created: from={transaction['from_account']}, to={transaction['to_account']}, amount={transaction['amount']}"
    )

    # =========================
    # PHASE 1: PREPARE
    # =========================
    write_log(
        transaction_id,
        "PREPARE",
        "Coordinator sends PREPARE request to Bank A and Bank B"
    )

    try:
        response_a = requests.post(
            f"{BANK_A_URL}/prepare",
            json=transaction
        )
        result["Bank_A_prepare"] = response_a.json()
    except:
        result["Bank_A_prepare"] = {
            "status": "ABORT",
            "reason": "Cannot connect to Bank A"
        }

    try:
        response_b = requests.post(
            f"{BANK_B_URL}/prepare",
            json=transaction
        )
        result["Bank_B_prepare"] = response_b.json()
    except:
        result["Bank_B_prepare"] = {
            "status": "ABORT",
            "reason": "Cannot connect to Bank B"
        }

    # Nếu có node ABORT thì không commit
    if (
        result["Bank_A_prepare"]["status"] != "READY"
        or result["Bank_B_prepare"]["status"] != "READY"
    ):
        write_log(
            transaction_id,
            "ABORT",
            "At least one participant is not ready. Transaction aborted."
        )

        return jsonify({
            "transaction": transaction,
            "status": "ABORTED",
            "reason": "At least one participant is not ready",
            "details": result
        })

    # =========================
    # READY
    # =========================
    write_log(
        transaction_id,
        "READY",
        "All participants voted READY"
    )

    # =========================
    # PHASE 2: COMMIT
    # =========================
    write_log(
        transaction_id,
        "COMMIT",
        "Coordinator sends COMMIT request to Bank A and Bank B"
    )

    try:
        response_a_commit = requests.post(
            f"{BANK_A_URL}/commit",
            json=transaction
        )
        result["Bank_A_commit"] = response_a_commit.json()
    except:
        result["Bank_A_commit"] = {
            "status": "ERROR",
            "reason": "Cannot commit Bank A"
        }

    try:
        response_b_commit = requests.post(
            f"{BANK_B_URL}/commit",
            json=transaction
        )
        result["Bank_B_commit"] = response_b_commit.json()
    except:
        result["Bank_B_commit"] = {
            "status": "ERROR",
            "reason": "Cannot commit Bank B"
        }

    return jsonify({
        "transaction": transaction,
        "status": "COMMITTED",
        "details": result
    })
# =========================
# Simulate Coordinator Crash
# =========================
@app.route('/transfer_crash', methods=['POST'])
def transfer_crash():
    data = request.get_json()

    transaction_id = data.get("transaction_id", "TXN_CRASH")

    transaction = {
        "transaction_id": transaction_id,
        "from_account": data.get("from_account"),
        "to_account": data.get("to_account"),
        "amount": data.get("amount")
    }

    result = {}

    # =========================
    # INITIAL
    # =========================
    write_log(
        transaction_id,
        "INITIAL",
        f"Transaction created: from={transaction['from_account']}, to={transaction['to_account']}, amount={transaction['amount']}"
    )

    # =========================
    # PREPARE
    # =========================
    write_log(
        transaction_id,
        "PREPARE",
        "Coordinator sends PREPARE request to Bank A and Bank B"
    )

    try:
        response_a = requests.post(
            f"{BANK_A_URL}/prepare",
            json=transaction
        )
        result["Bank_A_prepare"] = response_a.json()
    except:
        result["Bank_A_prepare"] = {
            "status": "ABORT",
            "reason": "Cannot connect to Bank A"
        }

    try:
        response_b = requests.post(
            f"{BANK_B_URL}/prepare",
            json=transaction
        )
        result["Bank_B_prepare"] = response_b.json()
    except:
        result["Bank_B_prepare"] = {
            "status": "ABORT",
            "reason": "Cannot connect to Bank B"
        }

    # Nếu có node ABORT thì không crash giả lập nữa
    if (
        result["Bank_A_prepare"]["status"] != "READY"
        or result["Bank_B_prepare"]["status"] != "READY"
    ):
        write_log(
            transaction_id,
            "ABORT",
            "At least one participant is not ready. Transaction aborted before simulated crash."
        )

        return jsonify({
            "transaction": transaction,
            "status": "ABORTED",
            "reason": "At least one participant is not ready",
            "details": result
        })

    # =========================
    # READY
    # =========================
    write_log(
        transaction_id,
        "READY",
        "All participants voted READY"
    )

    # =========================
    # SIMULATED CRASH
    # =========================
    write_log(
        transaction_id,
        "CRASH",
        "Coordinator crashed after PREPARE/READY but before COMMIT",
       
    )
    add_pending_transaction(transaction)

    return jsonify({
        "transaction": transaction,
        "status": "COORDINATOR_CRASHED",
        "message": "Simulated crash after READY and before COMMIT. No COMMIT was sent.",
        "details": result
    })
# =========================
# Recovery After Coordinator Reboot
# =========================
@app.route('/recover', methods=['POST'])
def recover():
    pending = load_pending_transactions()

    if not pending:
        return jsonify({
            "status": "NO_PENDING_TRANSACTION",
            "message": "No transaction needs recovery."
        })

    recovery_results = {}

    for transaction_id, transaction in pending.copy().items():
        result = {}

        write_log(
            transaction_id,
            "RECOVERY",
            "Coordinator rebooted and found pending transaction"
        )

        # Send COMMIT to Bank A
        try:
            response_a_commit = requests.post(
                f"{BANK_A_URL}/commit",
                json=transaction
            )
            result["Bank_A_commit"] = response_a_commit.json()
        except:
            result["Bank_A_commit"] = {
                "status": "ERROR",
                "reason": "Cannot commit Bank A during recovery"
            }

        # Send COMMIT to Bank B
        try:
            response_b_commit = requests.post(
                f"{BANK_B_URL}/commit",
                json=transaction
            )
            result["Bank_B_commit"] = response_b_commit.json()
        except:
            result["Bank_B_commit"] = {
                "status": "ERROR",
                "reason": "Cannot commit Bank B during recovery"
            }

        if (
            result["Bank_A_commit"]["status"] == "COMMITTED"
            and result["Bank_B_commit"]["status"] == "COMMITTED"
        ):
            write_log(
                transaction_id,
                "COMMIT",
                "Pending transaction committed successfully after recovery"
            )

            remove_pending_transaction(transaction_id)

            recovery_results[transaction_id] = {
                "status": "RECOVERED_AND_COMMITTED",
                "details": result
            }
        else:
            recovery_results[transaction_id] = {
                "status": "RECOVERY_FAILED",
                "details": result
            }

    return jsonify({
        "status": "RECOVERY_COMPLETED",
        "results": recovery_results
    })
if __name__ == '__main__':
    app.run(port=5000, debug=True)