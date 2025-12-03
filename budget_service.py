#========================
#FILE: budget_service.py
#========================

import requests, time
from firebase_config import DATABASE_URL
from auth_service import get_session
from wallet_service import get_all_transactions
from rich.console import Console
console = Console()

def _auth():
    session = get_session()
    if not session: return ""
    token = session.get("idToken")
    return f"?auth={token}" if token else ""

def _budget_path(uid, year, month):
    return f"{DATABASE_URL}/users/{uid}/budgets/{year}/{month}"

def set_budget(uid, year, month, category, limit):
    data = {"category": category, "limit": limit, "updated_at": int(time.time())}
    r = requests.put(f"{_budget_path(uid,year,month)}/{category}.json{_auth()}", json=data)
    return r.status_code in (200,204)

def get_budgets(uid, year, month):
    r = requests.get(f"{_budget_path(uid,year,month)}.json{_auth()}")
    if r.status_code != 200: return {}
    return r.json() or {}

def compute_budget_status(uid, year, month):
    budgets = get_budgets(uid, year, month)
    txs = get_all_transactions(uid)

    spending = {}
    for tx in txs:
        t = tx.get("type")
        if t not in ["withdrawal","expense","transfer_out"]: continue
        cat = tx.get("category","General")
        amt = float(tx.get("amount",0))
        spending[cat] = spending.get(cat,0) + amt

    result = {}
    for cat, b in budgets.items():
        limit = b["limit"]
        spent = spending.get(cat,0)
        result[cat] = {
            "limit": limit,
            "spent": spent,
            "remaining": limit - spent,
            "status": "OK" if limit-spent >= 0 else "OVERSPENT"
        }
    return result