#========================
#FILE: auth_service.py
#========================

import json, os, requests
from rich.console import Console
from rich.panel import Panel
from firebase_config import FIREBASE_AUTH_LOGIN, FIREBASE_AUTH_SIGNUP, DATABASE_URL

console = Console()
SESSION_FILE = "session.json"

def save_session(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def get_session():
    if not os.path.exists(SESSION_FILE): return None
    with open(SESSION_FILE, "r") as f: return json.load(f)

def clear_session():
    if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)


def register_user(email, password, name, age, phone, pan):
    console.print(Panel("Creating your account...", style="cyan"))

    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(FIREBASE_AUTH_SIGNUP, json=payload)
    data = response.json()

    if "error" in data:
        console.print(Panel(f"❌ Registration failed: {data['error']['message']}", style="red"))
        return None

    uid = data["localId"]

    profile = {"name": name, "age": age, "phone": phone, "pan": pan, "email": email}
    requests.put(f"{DATABASE_URL}/users/{uid}/profile.json", json=profile)

    console.print(Panel("✔ Account created successfully!", style="green"))
    return data


def login_user(email, password):
    console.print(Panel("🔐 Logging in...", style="cyan"))

    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(FIREBASE_AUTH_LOGIN, json=payload)
    data = response.json()

    if "error" in data:
        console.print(Panel(f"❌ Login failed: {data['error']['message']}", style="red"))
        return None

    save_session(data)
    console.print(Panel("✔ Logged in successfully!", style="green"))
    return data


def logout_user():
    clear_session()
    console.print(Panel("✔ Logged out.", style="green"))