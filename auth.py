import re
import bcrypt
import tkinter as tk
from tkinter import ttk, messagebox


class Authentication:
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
                messagebox.showinfo("Welcome", f"Welcome, {username}!")
                root.destroy()  # Close the window after successful login
                
                from membership_tracker import BusinessApp
                add_mem_root = tk.Tk()
                self.app = BusinessApp(add_mem_root, username)
                self.app.__init__
            else:
                messagebox.showerror("Authentication Failed", 
                        "Incorrect username or password.")

        root = tk.Tk()
        root.title("Login")
        
        frm = ttk

        ttk.Label(root, text="Username").pack(padx=10, pady=5)
        entry_username = ttk.Entry(root)
        entry_username.pack(padx=10, pady=5)

        ttk.Label(root, text="Password").pack(padx=10, pady=5)
        entry_password = ttk.Entry(root, show="*")
        entry_password.pack(padx=10, pady=5)

        ttk.Button(root, text="Login", 
            command=login_action).pack(padx=10, pady=20)
        root.bind('<Return>', lambda event: login_action())
        root.mainloop()


    def create_user_form(self):
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
                root.lift()
                root.focus_force()
                return
            
            # Check password confirmation for match
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                root.lift()
                root.focus_force()
                return

            # Check password against password policy
            if not self.check_password_policy(username, password):
                root.lift()
                root.focus_force()
                return

            try:
                db.create_user(username, hashed_password, salt, role)
                messagebox.showinfo("Success", "New user created!")
                root.destroy()  # Close the window after user creation
            except Exception as e:
                messagebox.showerror("Error", e)

        root = tk.Tk()
        root.title("Create User")
        
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0,weight=1)

        frm = ttk.Frame(root, padding=40)
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
        root.mainloop()
