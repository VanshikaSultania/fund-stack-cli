import re
import getpass
from auth_service import register_user, login_user, logout_user, get_session
from wallet_service import (
    create_wallet, list_wallets, get_wallet,
    deposit, withdraw, transfer
)
# ------------------
# VALIDATION HELPERS
# ------------------

def input_name():
    """Accepts only alphabets and spaces, minimum length 2."""
    while True:
        name = input("Full Name: ").strip()
        if re.match(r"^[A-Za-z ]{2,}$", name):
            return name
        print("❌ Invalid name. Use only letters and spaces (min. 2 characters). Try again.")

def input_age():
    """Age must be a valid number between 16 and 120."""
    while True:
        age = input("Age: ").strip()
        if age.isdigit() and 16 <= int(age) <= 100:
            return age
        print("❌ Invalid age. Enter a number between 16 and 120.")

def input_phone():
    """Phone must be numeric and at least 10 digits."""
    while True:
        phone = input("Phone Number: ").strip()
        if phone.isdigit() and len(phone) >= 10:
            return phone
        print("❌ Invalid phone number. Must be numeric and at least 10 digits.")

def input_pan():
    """PAN format: ABCDE1234F"""
    while True:
        pan = input("PAN: ").strip().upper()
        if re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan):
            return pan
        print("❌ Invalid PAN format. Expected format: ABCDE1234F")

def input_email():
    """Basic email validator."""
    while True:
        email = input("Email: ").strip()
        if "@" in email and "." in email:
            return email
        print("❌ Invalid email format. Try again.")

def input_password():
    """Password entry is hidden using getpass."""
    while True:
        pw = getpass.getpass("Password (min 6 characters): ").strip()
        if len(pw) >= 6:
            return pw
        print("❌ Password too short. Try again.")

# --------------------------------------------------------------------
# MENU DISPLAY
# --------------------------------------------------------------------

def show_menu():
    """Menu changes depending on whether user is logged in."""
    session = get_session()

    print("\n========== FUNDSTACK CLI ==========")

    if session:
        print(f"Logged in as → {session.get('email')}")
        print("-----------------------------------")
        print("3. Logout")
        print("4. Wallets → Create")
        print("5. Wallets → List")
        print("6. Wallets → Show Details")
        print("7. Wallets → Deposit Money")
        print("8. Wallets → Withdraw Money")
        print("9. Wallets → Transfer")
        print("10. Exit")
        print("11. Budget → Set Monthly Budget")
        print("12. Budget → View Budget Status")
        print("13. Reports → Generate Monthly Report (Gemini AI)")
    else:
        print("1. Register")
        print("2. Login")
        print("3. Exit")

    print("===================================")

def require_login_session():
    """Ensures user is logged in before wallet operations."""
    session = get_session()
    if not session:
        print("⚠ You must login first to access wallet features.")
        return None
    return session

# --------------------------------------------------------------------
# MAIN HANDLER
# --------------------------------------------------------------------

def handle_user_choice():
    """Main interactive loop."""
    while True:
        show_menu()
        session = get_session()

        # --------------------------------------------------
        # NOT LOGGED IN MODE
        # --------------------------------------------------
        if not session:
            choice = input("Select option (1-3): ").strip()

            if choice == "1":
                print("\n--- Secure Registration ---")
                name = input_name()
                age = input_age()
                phone = input_phone()
                pan = input_pan()
                email = input_email()
                pw = input_password()

                register_user(email, pw, name, age, phone, pan)

            elif choice == "2":
                print("\n--- Login ---")
                email = input("Email: ").strip()
                pw = getpass.getpass("Password: ").strip()
                login_user(email, pw)

            elif choice == "3":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid option. Try again.")
                continue

        # --------------------------------------------------
        # LOGGED IN MODE
        # --------------------------------------------------
        else:
            choice = input("Select option (3-10): ").strip()
            uid = session["localId"]

            # Logout
            if choice == "3":
                logout_user()

            # Create wallet
            elif choice == "4":
                print("\n--- Create Wallet ---")
                name = input("Wallet name (e.g., Savings): ").strip()
                currency = input("Currency (INR/USD/EUR): ").strip().upper() or "INR"
                initial = input("Initial balance (optional): ").strip()
                try:
                    initial_val = float(initial) if initial else 0.0
                except:
                    print("❌ Invalid initial balance.")
                    continue

                wid = create_wallet(uid, name, currency, initial_val)
                print("✔ Wallet created:", wid if wid else "❌ Failed")

            # List wallets
            elif choice == "5":
                print("\n--- Your Wallets ---")
                wallets = list_wallets(uid)
                if not wallets:
                    print("⚠ No wallets found.")
                else:
                    for w in wallets:
                        print(f"💰 {w['name']} ({w['currency']}): {w['balance']}   [ID: {w['id']}]")

            # Wallet details
            elif choice == "6":
                wid = input("Enter wallet ID: ").strip()
                w = get_wallet(uid, wid)
                if not w:
                    print("❌ Wallet not found.")
                else:
                    print("\n--- Wallet Details ---")
                    for k, v in w.items():
                        print(f"{k}: {v}")

            # Deposit
            elif choice == "7":
                wid = input("Wallet ID: ").strip()
                amt = input("Amount: ").strip()
                cat = input("Category (e.g., Salary, Refund): ").strip()
                note = input("Note: ").strip()

                try:
                    amt_val = float(amt)
                except:
                    print("❌ Invalid amount.")
                    continue

                ok = deposit(uid, wid, amt_val, note, cat)
                print("✔ Deposit successful." if ok else "❌ Failed.")

            # Withdraw
            elif choice == "8":
                wid = input("Wallet ID: ").strip()
                amt = input("Amount: ").strip()
                cat = input("Category (e.g., Food, Shopping): ").strip()
                note = input("Note: ").strip()

                try:
                    amt_val = float(amt)
                except:
                    print("❌ Invalid amount.")
                    continue

                ok = withdraw(uid, wid, amt_val, note, cat)
                print("✔ Withdrawal successful." if ok else "❌ Failed.")

            # Transfer
            elif choice == "9":
                src = input("From wallet ID: ").strip()
                dst = input("To wallet ID: ").strip()
                amt = input("Amount: ").strip()
                cat = input("Category (Optional): ").strip()
                note = input("Note: ").strip()

                try:
                    amt_val = float(amt)
                except:
                    print("❌ Invalid amount.")
                    continue

                ok = transfer(uid, src, dst, amt_val, note, cat)
                print("✔ Transfer complete." if ok else "❌ Transfer failed.")

            elif choice == "10":
                print("👋 Goodbye!")
                break

            elif choice == "11":
                from budget_service import set_budget
                year = int(input("Year (YYYY): "))
                month = int(input("Month (1-12): "))
                category = input("Category: ").strip()
                limit = float(input("Monthly limit: "))
                ok = set_budget(uid, year, month, category, limit)
                print("✔ Budget saved." if ok else "❌ Failed.")

            

            else:
                print("❌ Invalid option.")
                continue