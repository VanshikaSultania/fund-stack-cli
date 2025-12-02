import requests
import time
from firebase_config import DATABASE_URL
from auth_service import get_session

def _auth():
    session = get_session()
    if not session:
        return ""
    token = session.get("idToken")
    return f"?auth={token}" if token else ""

def _budget_path(uid, year, month):
    return f"{DATABASE_URL.rstrip('/')}/users/{uid}/budgets/{year}/{month}"

def set_budget(uid: str, year: int, month: int, category: str, limit: float):
    """Set or update monthly budget for a category."""
    path = f"{_budget_path(uid, year, month)}/{category}.json{_auth()}"
    data = {
        "category": category,
        "limit": limit,
        "updated_at": int(time.time())
    }
    return requests.put(path, json=data).status_code in (200, 204)

def get_budgets(uid: str, year: int, month: int):
    """Retrieve all budgets for a given month."""
    path = f"{_budget_path(uid, year, month)}.json{_auth()}"
    r = requests.get(path)
    if r.status_code != 200:
        return {}
    return r.json() or {}

def compute_budget_status(uid: str, year: int, month: int, transactions: list):
    """Calculate remaining budget for each category."""
    budgets = get_budgets(uid, year, month)
    spending = {}

    for tx in transactions:
        if "date" not in tx: continue
        if "category" not in tx: continue
        if tx.get("type") != "expense":
            continue

        tx_year = int(tx["date"].split("-")[0])
        tx_month = int(tx["date"].split("-")[1])

        if tx_year == year and tx_month == month:
            cat = tx["category"]
            amt = float(tx["amount"])
            spending[cat] = spending.get(cat, 0) + amt

    result = {}
    for cat, details in budgets.items():
        limit = details["limit"]
        spent = spending.get(cat, 0)
        remaining = limit - spent
        result[cat] = {
            "limit": limit,
            "spent": spent,
            "remaining": remaining,
            "status": "OK" if remaining >= 0 else "OVERSPENT"
        }

    return result