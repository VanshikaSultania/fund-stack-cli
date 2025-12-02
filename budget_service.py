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