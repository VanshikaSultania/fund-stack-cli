import pyrebase

# This dictionary contains all the Firebase configuration details
# that you get from Firebase Console → Project Settings → Web API.
firebase_config = {
    "apiKey": "AIzaSyB8MsAaONyO3MRyQWfw5Qque6iaVtK4fjg",
    "authDomain": "fundstack-cli.firebaseapp.com",
    "databaseURL": "https://fundstack-cli-default-rtdb.firebaseio.com/",
    "projectId": "fundstack-cli",
    "storageBucket": "fundstack-cli.appspot.com",
    "messagingSenderId": "887689727012",
    "appId": "1:887689727012:web:27a13bc5e51ef429e0dcb1"
}

# Initialize a firebase application using the config settings
firebase = pyrebase.initialize_app(firebase_config)

# Authentication service (register, login, token handling)
auth = firebase.auth()

# Realtime Database service (read/write data)
db = firebase.database()