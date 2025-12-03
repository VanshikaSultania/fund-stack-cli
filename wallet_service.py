#========================
#FILE: wallet_service.py
#========================

import uuid, time, csv, os, requests
from rich.progress import Progress
from rich.console import Console
from firebase_config import DATABASE_URL
from auth_service import get_session

console = Console()


def _auth_query():
    session = get_session()
    if not session: return ""
    token = session.get("idToken")
    return f"?auth={token}" if token else ""


def _wallet_base(uid): return f"{DATABASE_URL}/users/{uid}/wallets"


def _log_csv(uid, wallet_id, tx):
    filename = f"transactions_{uid}.csv"
    exists = os.path.exists(filename)

    with open(filename, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["timestamp", "wallet_id", "type", "amount", "currency", "category", "note", "balance_after", "from_wallet", "to_wallet"])
        w.writerow([
            tx.get("timestamp"), wallet_id, tx.get("type"), tx.get("amount"), tx.get("currency"),
            tx.get("category", ""), tx.get("note", ""), tx.get("balance_after", ""),
            tx.get("from_wallet", ""), tx.get("to_wallet", "")
        ])


def create_wallet(uid, name, currency, initial):
    wallet_id = uuid.uuid4().hex
    wallet = {
        "id": wallet_id,
        "name": name,
        "currency": currency,
        "balance": float(initial),
        "created_at": int(time.time())
    }
    r = requests.put(f"{_wallet_base(uid)}/{wallet_id}.json{_auth_query()}", json=wallet)
    return wallet_id if r.status_code in (200, 204) else None


def list_wallets(uid):
    r = requests.get(f"{_wallet_base(uid)}.json{_auth_query()}")
    if r.status_code != 200: return []
    data = r.json() or {}
    return list(data.values())


def get_wallet(uid, wid):
    r = requests.get(f"{_wallet_base(uid)}/{wid}.json{_auth_query()}")
    return r.json() if r.status_code == 200 else None


def _update_balance(uid, wid, bal):
    r = requests.patch(f"{_wallet_base(uid)}/{wid}.json{_auth_query()}", json={"balance": bal})
    return r.status_code in (200, 204)


def _record_tx(uid, wid, tx):
    txid = uuid.uuid4().hex
    r = requests.put(f"{_wallet_base(uid)}/{wid}/transactions/{txid}.json{_auth_query()}", json=tx)
    return txid if r.status_code in (200, 204) else None


def deposit(uid, wid, amt, note, cat):
    with Progress() as p:
        task = p.add_task("[green]Processing deposit...", total=100)
        for _ in range(20): p.update(task, advance=5); time.sleep(0.02)

    w = get_wallet(uid, wid)
    new_bal = w["balance"] + amt
    _update_balance(uid, wid, new_bal)

    tx = {"type": "deposit", "amount": amt, "currency": w["currency"], "note": note,
          "category": cat, "timestamp": int(time.time()), "balance_after": new_bal}

    _record_tx(uid, wid, tx)
    _log_csv(uid, wid, tx)
    return True


def withdraw(uid, wid, amt, note, cat):
    with Progress() as p:
        task = p.add_task("[yellow]Processing withdrawal...", total=100)
        for _ in range(20): p.update(task, advance=5); time.sleep(0.02)

    w = get_wallet(uid, wid)
    if amt > w["balance"]: return False

    new_bal = w["balance"] - amt
    _update_balance(uid, wid, new_bal)

    tx = {"type": "withdrawal", "amount": amt, "currency": w["currency"], "note": note,
          "category": cat, "timestamp": int(time.time()), "balance_after": new_bal}

    _record_tx(uid, wid, tx)
    _log_csv(uid, wid, tx)
    return True


def transfer(uid, src, dst, amt, note, cat):
    with Progress() as p:
        task = p.add_task("[magenta]Processing transfer...", total=100)
        for _ in range(25): p.update(task, advance=4); time.sleep(0.02)

    s = get_wallet(uid, src)
    d = get_wallet(uid, dst)

    if amt > s["balance"]: return False

    new_s = s["balance"] - amt
    new_d = d["balance"] + amt

    _update_balance(uid, src, new_s)
    _update_balance(uid, dst, new_d)

    ts = int(time.time())

    tx_out = {"type": "transfer_out", "amount": amt, "currency": s["currency"], "note": note,
              "category": cat, "timestamp": ts, "balance_after": new_s, "to_wallet": dst}
    tx_in  = {"type": "transfer_in",  "amount": amt, "currency": d["currency"], "note": note,
              "category": cat, "timestamp": ts, "balance_after": new_d, "from_wallet": src}

    _record_tx(uid, src, tx_out)
    _record_tx(uid, dst, tx_in)
    _log_csv(uid, src, tx_out)
    _log_csv(uid, dst, tx_in)
    return True


def get_all_transactions(uid):
    r = requests.get(f"{_wallet_base(uid)}.json{_auth_query()}")
    if r.status_code != 200: return []

    data = r.json() or {}
    txs = []
    for wid, wdata in data.items():
        for txid, tx in (wdata.get("transactions", {}) or {}).items():
            tx["_wallet_id"] = wid
            tx["_txid"] = txid
            txs.append(tx)
    return txs