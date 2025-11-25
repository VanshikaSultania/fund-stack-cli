"""
wallet_service.py
Updated: 
- Now logs every wallet transaction to a CSV file per user.
- CSV format: timestamp, wallet_id, type, amount, currency, category, note, balance_after, from_wallet, to_wallet
"""

import uuid
import time
import csv
import os
import requests
from typing import Optional, Dict, List
from firebase_config import DATABASE_URL
from auth_service import get_session

def _auth_query():
    session = get_session()
    if not session:
        return ""
    token = session.get("idToken")
    return f"?auth={token}" if token else ""


def _wallet_base_path(uid: str) -> str:
    return f"{DATABASE_URL.rstrip('/')}/users/{uid}/wallets"


### NEW: CSV LOGGING FUNCTION
def _log_to_csv(uid: str, wallet_id: str, tx: Dict):
    filename = f"transactions_{uid}.csv"
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)

        # Write header once
        if not file_exists:
            writer.writerow([
                "timestamp", "wallet_id", "type",
                "amount", "currency", "category", 
                "note", "balance_after", "from_wallet", "to_wallet"
            ])

        writer.writerow([
            tx.get("timestamp"),
            wallet_id,
            tx.get("type"),
            tx.get("amount"),
            tx.get("currency"),
            tx.get("category", ""),   # may not exist before
            tx.get("note", ""),
            tx.get("balance_after", ""),
            tx.get("from_wallet", ""),
            tx.get("to_wallet", "")
        ])


def create_wallet(uid: str, name: str, currency: str, initial_balance: float = 0.0) -> Optional[str]:
    wallet_id = uuid.uuid4().hex
    wallet = {
        "id": wallet_id,
        "name": name,
        "currency": currency.upper(),
        "balance": float(initial_balance),
        "created_at": int(time.time())
    }
    path = f"{_wallet_base_path(uid)}/{wallet_id}.json{_auth_query()}"
    r = requests.put(path, json=wallet)
    return wallet_id if r.status_code in (200, 204) else None


def list_wallets(uid: str) -> List[Dict]:
    path = f"{_wallet_base_path(uid)}.json{_auth_query()}"
    r = requests.get(path)
    if r.status_code != 200:
        return []
    return list((r.json() or {}).values())


def get_wallet(uid: str, wallet_id: str) -> Optional[Dict]:
    path = f"{_wallet_base_path(uid)}/{wallet_id}.json{_auth_query()}"
    r = requests.get(path)
    return r.json() if r.status_code == 200 else None


def _write_wallet_balance(uid: str, wallet_id: str, new_balance: float) -> bool:
    path = f"{_wallet_base_path(uid)}/{wallet_id}.json{_auth_query()}"
    return requests.patch(path, json={"balance": new_balance}).status_code in (200, 204)


def _add_wallet_transaction(uid: str, wallet_id: str, tx: Dict) -> Optional[str]:
    txid = uuid.uuid4().hex
    path = f"{DATABASE_URL.rstrip('/')}/users/{uid}/wallets/{wallet_id}/transactions/{txid}.json{_auth_query()}"
    r = requests.put(path, json=tx)
    return txid if r.status_code in (200, 204) else None


# -------------------------
# UPDATED TRANSACTION METHODS
# -------------------------

def deposit(uid: str, wallet_id: str, amount: float, note: str = "", category: str = "General") -> bool:
    if amount <= 0:
        return False

    wallet = get_wallet(uid, wallet_id)
    if not wallet:
        return False

    new_balance = float(wallet["balance"]) + amount
    if not _write_wallet_balance(uid, wallet_id, new_balance):
        return False

    tx = {
        "type": "deposit",
        "amount": amount,
        "currency": wallet["currency"],
        "note": note,
        "category": category,  # NEW
        "timestamp": int(time.time()),
        "balance_after": new_balance
    }

    _add_wallet_transaction(uid, wallet_id, tx)
    _log_to_csv(uid, wallet_id, tx)  # NEW
    return True


def withdraw(uid: str, wallet_id: str, amount: float, note: str = "", category: str = "General") -> bool:
    wallet = get_wallet(uid, wallet_id)
    if not wallet or amount <= 0 or amount > float(wallet["balance"]):
        return False

    new_balance = float(wallet["balance"]) - amount
    if not _write_wallet_balance(uid, wallet_id, new_balance):
        return False

    tx = {
        "type": "withdrawal",
        "amount": amount,
        "currency": wallet["currency"],
        "note": note,
        "category": category,  # NEW
        "timestamp": int(time.time()),
        "balance_after": new_balance
    }

    _add_wallet_transaction(uid, wallet_id, tx)
    _log_to_csv(uid, wallet_id, tx)  # NEW
    return True


def transfer(uid: str, from_wallet_id: str, to_wallet_id: str, amount: float, note: str = "", category: str = "Transfer") -> bool:
    src = get_wallet(uid, from_wallet_id)
    dst = get_wallet(uid, to_wallet_id)

    if not src or not dst or amount <= 0 or amount > float(src["balance"]):
        return False

    # Update balances
    new_src_balance = float(src["balance"]) - amount
    new_dst_balance = float(dst["balance"]) + amount

    if not (_write_wallet_balance(uid, from_wallet_id, new_src_balance) and _write_wallet_balance(uid, to_wallet_id, new_dst_balance)):
        return False

    timestamp = int(time.time())

    tx_out = {
        "type": "transfer_out",
        "amount": amount,
        "currency": src["currency"],
        "note": note,
        "category": category,  # NEW
        "timestamp": timestamp,
        "balance_after": new_src_balance,
        "to_wallet": to_wallet_id
    }

    tx_in = {
        "type": "transfer_in",
        "amount": amount,
        "currency": dst["currency"],
        "note": note,
        "category": category,  # SAME category
        "timestamp": timestamp,
        "balance_after": new_dst_balance,
        "from_wallet": from_wallet_id
    }

    _add_wallet_transaction(uid, from_wallet_id, tx_out)
    _add_wallet_transaction(uid, to_wallet_id, tx_in)

    _log_to_csv(uid, from_wallet_id, tx_out)  # NEW
    _log_to_csv(uid, to_wallet_id, tx_in)    # NEW

    return True
