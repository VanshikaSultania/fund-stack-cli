# Purpose: Provides a text-based menu system for user interaction

from auth_service import register_user, login_user, logout_user, get_session
# Import the functions we created for handling authentication

# Display menu
def show_menu():
    print("\n====== Firebase CLI Authentication ======")
    print("1. Register")
    print("2. Login")
    print("3. Logout")
    print("4. Check Current User")
    print("5. Exit")
    print("=========================================")
# Prints a simple menu.

# Handle user choices
def handle_user_choice():
    while True: # We run an infinite loop until user selects Exit
        show_menu() # Show the menu options
        choice = input("Select an option (1-5): ") # Get user input

        if choice == "1": # Option 1 — Register
            print("\n--- Registration ---")
            name = input("Full Name: ")
            age = input("Age: ")
            phone = input("Phone Number: ")
            pan = input("PAN: ")
            # Collect additional profile info

            email = input("Email: ")
            pw = input("Password: ")
            # Collects Auth info

            register_user(email, pw, name, age, phone, pan) # Calls register_user() to store both Auth and Database data

        elif choice == "2": # Option 2 — Login
            print("\n--- Login ---")
            email = input("Email: ")
            pw = input("Password: ")
            login_user(email, pw) # Calls login_user() to authenticate and create a session

        elif choice == "3": # Option 3 — Logout
            logout_user() # Calls logout_user() to clear the session
 
        elif choice == "4": # Option 4 — Check Current User
            session = get_session() # Reads session file and checks if someone is logged in
            if session: # If session exists
                print("👍 Currently logged in as:", session.get("email", "Unknown"))
            else: # If no session exists
                print("⚠ No user logged in.")

        elif choice == "5": # Option 5 — Exit
            print("Goodbye!")
            break # Exit the loop and end the program

        else: # Invalid input
            print("❌ Invalid option. Try again.")
