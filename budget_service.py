import requests
import time
from firebase_config import DATABASE_URL
from auth_service import get_session
from wallet_service import get_all_transactions

def _auth():
    session = get_session()
    if not session:
        return ""
    token = session.get("idToken")
    return f"?auth={token}" if token else ""

def _budget_path(uid, year, month):
    return f"{DATABASE_URL.rstrip('/')}/users/{uid}/budgets/{year}/{month}"

def set_budget(uid: str, year: int, month: int, category: str, limit: float):
    """Create/update a monthly budget category."""
    path = f"{_budget_path(uid, year, month)}/{category}.json{_auth()}"
    data = {
        "category": category,
        "limit": limit,
        "updated_at": int(time.time())
    }
    return requests.put(path, json=data).status_code in (200, 204)

def get_budgets(uid: str, year: int, month: int):
    """Retrieve all budgets for the given month."""
    path = f"{_budget_path(uid, year, month)}.json{_auth()}"
    r = requests.get(path)
    if r.status_code != 200:
        return {}
    return r.json() or {}

def compute_budget_status(uid: str, year: int, month: int):
    """Analyze budgets vs actual expenses."""
    budgets = get_budgets(uid, year, month)
    txs = get_all_transactions(uid)

    spending = {}

    for tx in txs:
        tx_type = tx.get("type")
        if tx_type not in ["withdrawal", "expense", "transfer_out"]:
            continue

        # Use date if exists; fallback on timestamp (not ideal but works)
        if "date" in tx:
            try:
                yr = int(tx["date"].split("-")[0])
                mo = int(tx["date"].split("-")[1])
            except:
                continue
            if yr != year or mo != month:
                continue

        category = tx.get("category", "General")
        amount = float(tx.get("amount", 0))
        spending[category] = spending.get(category, 0) + amount

    # Build final comparison
    result = {}

    for category, bdata in budgets.items():
        limit = bdata["limit"]
        spent = spending.get(category, 0)
        remaining = limit - spent
        result[category] = {
            "limit": limit,
            "spent": spent,
            "remaining": remaining,
            "status": "OK" if remaining >= 0 else "OVERSPENT"
        }

    return result
