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
