from tkinter import messagebox
from db import Database
from auth import Authentication
from membership_tracker import BusinessApp

def main():
    db = Database()
    auth = Authentication()
    
    try:
        if db.are_users_exist():
            auth.login_form()
        else:
            auth.create_user_form()
    except Exception as e:
        messagebox.showerror(f"Program failed to launch", e)

if __name__ == "__main__":
    main()
