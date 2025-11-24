# Purpose: Provides a text-based menu system for user interaction
# Updated to hide wallet options until user logs in.

from auth_service import register_user, login_user, logout_user, get_session
from wallet_service import (
    create_wallet,
    list_wallets,
    get_wallet,
    deposit,
    withdraw,
    transfer
)

def show_menu():
    session = get_session()

    print("\n====== FundStack CLI ======")

    if session:
        # Logged-in menu
        print("Logged in as:", session.get("email"))
        print("----------------------------------")
        print("3. Logout")
        print("4. Wallets: Create")
        print("5. Wallets: List")
        print("6. Wallets: Show Details")
        print("7. Wallets: Deposit")
        print("8. Wallets: Withdraw")
        print("9. Wallets: Transfer")
        print("10. Exit")
    else:
        # Logged-out menu
        print("1. Register")
        print("2. Login")
        print("3. Exit")

    print("==============================")


def require_login_session():
    session = get_session()
    if not session:
        print("⚠ You must login first to access wallet features.")
        return None
    return session


def handle_user_choice():
    while True:
        show_menu()
        session = get_session()

        if session:
            # Logged-in mode options
            choice = input("Select an option (3-10): ").strip()

            if choice == "3":
                logout_user()

            elif choice == "4":
                # Create wallet
                uid = session["localId"]
                name = input("Wallet name: ").strip()
                currency = input("Currency (INR/USD/etc): ").strip().upper() or "INR"
                initial = input("Initial balance (optional): ").strip()
                try:
                    initial_val = float(initial) if initial else 0.0
                except:
                    print("❌ Invalid initial balance.")
                    continue

                wid = create_wallet(uid, name, currency, initial_val)
                print("✔ Wallet created:", wid if wid else "❌ Failed")

            elif choice == "5":
                # List wallets
                uid = session["localId"]
                wallets = list_wallets(uid)
                print("\n--- Your Wallets ---")
                if not wallets:
                    print("No wallets found.")
                else:
                    for w in wallets:
                        print(
                            f"- id: {w.get('id')}  name: {w.get('name')} "
                            f"currency: {w.get('currency')}  balance: {w.get('balance')}"
                        )

            elif choice == "6":
                # Show wallet details
                uid = session["localId"]
                wid = input("Wallet id: ").strip()
                w = get_wallet(uid, wid)
                if not w:
                    print("❌ Wallet not found.")
                else:
                    print("\n--- Wallet Details ---")
                    for k, v in w.items():
                        print(f"{k}: {v}")

            elif choice == "7":
                # Deposit
                uid = session["localId"]
                wid = input("Wallet id: ").strip()
                amt = input("Amount: ").strip()
                try:
                    amt_val = float(amt)
                except:
                    print("❌ Invalid amount.")
                    continue
                note = input("Note: ")
                ok = deposit(uid, wid, amt_val, note)
                print("✔ Deposit successful." if ok else "❌ Failed.")

            elif choice == "8":
                # Withdraw
                uid = session["localId"]
                wid = input("Wallet id: ").strip()
                amt = input("Amount: ").strip()
                try:
                    amt_val = float(amt)
                except:
                    print("❌ Invalid amount.")
                    continue
                note = input("Note: ")
                ok = withdraw(uid, wid, amt_val, note)
                print("✔ Withdrawal successful." if ok else "❌ Failed.")

            elif choice == "9":
                # Transfer
                uid = session["localId"]
                from_w = input("From wallet id: ").strip()
                to_w = input("To wallet id: ").strip()
                amt = input("Amount: ").strip()
                try:
                    amt_val = float(amt)
                except:
                    print("❌ Invalid amount.")
                    continue
                note = input("Note: ")
                ok = transfer(uid, from_w, to_w, amt_val, note)
                print("✔ Transfer successful." if ok else "❌ Failed.")

            elif choice == "10":
                print("Goodbye!")
                break

            else:
                print("❌ Invalid option.")

        else:
            # Logged-out mode options
            choice = input("Select an option (1-3): ").strip()

            if choice == "1":
                print("\n--- Registration ---")
                name = input("Full Name: ")
                age = input("Age: ")
                phone = input("Phone Number: ")
                pan = input("PAN: ")
                email = input("Email: ")
                pw = input("Password: ")
                register_user(email, pw, name, age, phone, pan)

            elif choice == "2":
                print("\n--- Login ---")
                email = input("Email: ")
                pw = input("Password: ")
                login_user(email, pw)

            elif choice == "3":
                print("Goodbye!")
                break

            else:
                print("❌ Invalid option.")
