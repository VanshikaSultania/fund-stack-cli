import json
import os
import requests
from firebase_config import (
    FIREBASE_AUTH_LOGIN,
    FIREBASE_AUTH_SIGNUP,
    DATABASE_URL
)

SESSION_FILE = "session.json"

def save_session(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def get_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def register_user(email, password, name, age, phone, pan):

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(FIREBASE_AUTH_SIGNUP, json=payload)
    data = response.json()

    if "error" in data:
        print("❌ Registration failed:", data["error"]["message"])
        return None

    uid = data["localId"]

    profile = {
        "name": name,
        "age": age,
        "phone": phone,
        "pan": pan,
        "email": email
    }

    requests.put(f"{DATABASE_URL}/users/{uid}.json", json=profile)

    print("✔ User registered and profile saved.")
    return data

def login_user(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(FIREBASE_AUTH_LOGIN, json=payload)
    data = response.json()

    if "error" in data:
        print("❌ Login failed:", data["error"]["message"])
        return None

    save_session(data)
    print("✔ Logged in successfully.")
    return data

def logout_user():
    clear_session()
    print("✔ Logged out successfully.")
