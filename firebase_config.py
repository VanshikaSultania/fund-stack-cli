import requests

# Base Firebase project details
API_KEY = "AIzaSyB8MsAaONyO3MRyQWfw5Qque6iaVtK4fjg"

# Firebase Auth REST endpoints
FIREBASE_AUTH_SIGNUP = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
FIREBASE_AUTH_LOGIN = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

# Your Realtime Database URL
DATABASE_URL = "https://fundstack-cli-default-rtdb.firebaseio.com/"
