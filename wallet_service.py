"""
wallet_service.py

Provides wallet management for each user:
- create_wallet(uid, name, currency)
- list_wallets(uid)
- get_wallet(uid, wallet_id)
- deposit(uid, wallet_id, amount, note)
- withdraw(uid, wallet_id, amount, note)
- transfer(uid, from_wallet_id, to_wallet_id, amount, note)

Data layout (Realtime DB):
/users/<uid>/wallets/<wallet_id> -> { id, name, currency, balance, created_at }
/users/<uid>/wallets/<wallet_id>/transactions/<txid> -> { ...transaction fields... }

IMPORTANT: This module uses requests to PUT/PATCH/GET data to your Realtime DB using the DATABASE_URL.
If you lock your DB rules to require auth, you should append ?auth=<idToken> to requests.
"""

import uuid
import time
import requests
from typing import Optional, Dict, List
from firebase_config import DATABASE_URL
from auth_service import get_session  # uses local session.json

# Helper to append auth token if session exists and contains idToken
def _auth_query() -> str:
    session = get_session()
    if not session:
        return ""
    token = session.get("idToken")
    return f"?auth={token}" if token else ""

def _wallet_base_path(uid: str) -> str:
    # ensure DATABASE_URL has no trailing slash
    base = DATABASE_URL.rstrip("/")
    return f"{base}/users/{uid}/wallets"

def create_wallet(uid: str, name: str, currency: str, initial_balance: float = 0.0) -> Optional[str]:
    """
    Create a new wallet for user `uid`.
    Returns wallet_id on success, None on failure.
    """
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
    if r.status_code in (200, 204):
        return wallet_id
    # optionally return r.text for debugging
    return None

def list_wallets(uid: str) -> List[Dict]:
    """
    Return a list of wallet dicts for the user. If none or error returns [].
    """
    path = f"{_wallet_base_path(uid)}.json{_auth_query()}"
    r = requests.get(path)
    if r.status_code != 200:
        return []
    data = r.json() or {}
    # data is mapping wallet_id -> wallet dict
    return list(data.values())

def get_wallet(uid: str, wallet_id: str) -> Optional[Dict]:
    path = f"{_wallet_base_path(uid)}/{wallet_id}.json{_auth_query()}"
    r = requests.get(path)
    if r.status_code != 200:
        return None
    return r.json()

def _write_wallet_balance(uid: str, wallet_id: str, new_balance: float) -> bool:
    # patch only the balance field
    path = f"{_wallet_base_path(uid)}/{wallet_id}.json{_auth_query()}"
    r = requests.patch(path, json={"balance": new_balance})
    return r.status_code in (200, 204)

def _add_wallet_transaction(uid: str, wallet_id: str, tx: Dict) -> Optional[str]:
    """
    Add a transaction record under wallet transactions.
    Returns txid on success.
    """
    txid = uuid.uuid4().hex
    base = DATABASE_URL.rstrip("/")
    path = f"{base}/users/{uid}/wallets/{wallet_id}/transactions/{txid}.json{_auth_query()}"
    r = requests.put(path, json=tx)
    if r.status_code in (200, 204):
        return txid
    return None

def deposit(uid: str, wallet_id: str, amount: float, note: str = "") -> bool:
    """
    Adds amount to wallet balance and creates a transaction of type 'deposit'.
    """
    if amount <= 0:
        return False

    wallet = get_wallet(uid, wallet_id)
    if not wallet:
        return False

    new_balance = float(wallet.get("balance", 0.0)) + float(amount)
    ok = _write_wallet_balance(uid, wallet_id, new_balance)
    if not ok:
        return False

    tx = {
        "type": "deposit",
        "amount": float(amount),
        "currency": wallet.get("currency"),
        "note": note,
        "timestamp": int(time.time()),
        "balance_after": new_balance
    }
    _add_wallet_transaction(uid, wallet_id, tx)
    return True
