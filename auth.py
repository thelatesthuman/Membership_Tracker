import re
import bcrypt
import logging
import tkinter as tk
from tkinter import ttk, messagebox


class Authentication:
    def __init__(self, root):
        self.root = root
        self.logger = logging.getLogger(__name__)

    def hash_password(self, password):
        # Generate a salt and hash the password with the salt
        salt = bcrypt.gensalt()
        pass_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return pass_hash, salt


    def check_password_policy(self, username, password):
        # Check if the username is too short
        if len(username) < 3:
            messagebox.showerror("Error", 
                "Username must be at least 3 characters long!")
            return False

        # Password policy checks
        if len(password) < 14:
            messagebox.showerror("Error", 
                "Password must be at least 14 characters long!")
            return False

        # Check if the password contains at least one number, 
        # one uppercase letter, and one symbol
        if not re.search(r"\d", password):  # At least one digit
            messagebox.showerror("Error", 
                "Password must contain at least one number!")
            return False
        if not re.search(r"[A-Z]", password):  # At least one uppercase letter
            messagebox.showerror("Error", 
                    "Password must contain at least one uppercase letter!")
            return False
        if not re.search(r"[\W_]", password):  # At least one special character (symbol)
            messagebox.showerror("Error", 
                    "Password must contain at least one special character!")
            return False

        return True


    # Authenticate the user
    def authenticate_user(self, username, password):
        from db import Database
        db = Database()
        user = db.get_user_by_username(username)

        if user:
            stored_hash = user[2]  # stored password hash
            stored_salt = user[3]  # stored salt

            # Check if the provided password matches the stored hash
            if bcrypt.checkpw(password.encode('utf-8'), 
                stored_hash.encode('utf-8')):
                return True  # Authentication successful
            else:
                return False  # Incorrect password
        else:
            return False  # User not found


    def login_form(self):
        def login_action():
            username = entry_username.get()
            password = entry_password.get()

            if self.authenticate_user(username, password):
                self.logger.info("Authentication successful: %s",
                    (username))
                messagebox.showinfo("Welcome", f"Welcome, {username}!",
                    parent=login_win)
                login_win.destroy()  
                
                from membership_tracker import BusinessApp
                self.app = BusinessApp(self.root, username)
            else:
                self.logger.warning("Authentication failed")
                messagebox.showerror("Authentication Failed", 
                        "Incorrect username or password.",
                        parent=login_win)


        login_win = tk.Toplevel(self.root)
        login_win.title("Login")

        ttk.Label(login_win, text="Username").pack(padx=10, pady=5)
        entry_username = ttk.Entry(login_win)
        entry_username.pack(padx=10, pady=5)

        ttk.Label(login_win, text="Password").pack(padx=10, pady=5)
        entry_password = ttk.Entry(login_win, show="*")
        entry_password.pack(padx=10, pady=5)
        
        ttk.Button(login_win, text="Login", 
            command=login_action).pack(padx=10, pady=20)
        login_win.bind('<Return>', lambda event: login_action())
        login_win.protocol("WM_DELETE_WINDOW", self.root.destroy)


    def create_user_form(self, startup=False):
        def create_user_action():
            from db import Database
            db = Database()
            
            username = entry_username.get()
            password = entry_password.get()
            confirm_password = entry_confirm_password.get()
            role = entry_user_role.get()

            hashed_password, salt = self.hash_password(password)
            
            # Check if username exists
            if db.get_user_by_username(username):
                messagebox.showerror("Error", "Username already in use!")
                create_user_win.lift()
                create_user_win.focus_force()
                return
            
            # Check password confirmation for match
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                create_user_win.lift()
                create_user_win.focus_force()
                return

            # Check password against password policy
            if not self.check_password_policy(username, password):
                create_user_win.lift()
                create_user_win.focus_force()
                return

            try:
                db.create_user(username, hashed_password, salt, role)
                messagebox.showinfo("Success", "New user created!")
                create_user_win.destroy()

                if startup:
                    from membership_tracker import BusinessApp
                    self.app = BusinessApp(self.root, username)
            except Exception as e:
                messagebox.showerror("Error", e)


        create_user_win = tk.Toplevel(self.root)
        create_user_win.title("Create User")
        
        create_user_win.grid_rowconfigure(0, weight=1)
        create_user_win.grid_columnconfigure(0,weight=1)

        frm = ttk.Frame(create_user_win, padding=40)
        frm.grid(sticky='nsew')

        username_label = ttk.Label(frm, text="Username")
        username_label.grid(column=0, row=0, sticky='w')
        entry_username = ttk.Entry(frm)
        entry_username.grid(column=1, row=0)

        password_label = ttk.Label(frm, text="Password")
        password_label.grid(column=0, row=1, sticky='w')
        entry_password = ttk.Entry(frm, show="*")
        entry_password.grid(column=1, row=1)

        confirm_password_label = ttk.Label(frm, text="Confirm Password")
        confirm_password_label.grid(column=0, row=2, sticky='w')
        entry_confirm_password = ttk.Entry(frm, show="*")
        entry_confirm_password.grid(column=1, row=2)

        user_role_label = ttk.Label(frm, text="User Role")
        user_role_label.grid(column=0, row=3, sticky='w')
        entry_user_role = ttk.Entry(frm)
        entry_user_role.grid(column=1, row=3)
        
        create_user_button = ttk.Button(frm, text="Create User", 
                command=create_user_action)
        create_user_button.grid(column=1, row=4, sticky='w')
        create_user_button.bind('<Return>',
                lambda event: create_user_action())
