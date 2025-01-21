import re
import bcrypt
import tkinter as tk
from tkinter import messagebox


class Authentication:
    def hash_password(self, password):
        # Generate a salt and hash the password with the salt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password, salt


    def check_password_policy(self, username, password):
        # Check if the username is too short
        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters long!")
            return False

        # Password policy checks
        if len(password) < 14:
            messagebox.showerror("Error", "Password must be at least 14 characters long!")
            return False

        # Check if the password contains at least one number, one uppercase letter, 
        # and one symbol
        if not re.search(r"\d", password):  # At least one digit
            messagebox.showerror("Error", "Password must contain at least one number!")
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
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
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
                self.app.__init__  # Start mem_track.py
            else:
                messagebox.showerror("Authentication Failed", 
                        "Incorrect username or password.")

        root = tk.Tk()
        root.title("Login")

        tk.Label(root, text="Username").pack(padx=10, pady=5)
        entry_username = tk.Entry(root)
        entry_username.pack(padx=10, pady=5)

        tk.Label(root, text="Password").pack(padx=10, pady=5)
        entry_password = tk.Entry(root, show="*")
        entry_password.pack(padx=10, pady=5)

        tk.Button(root, text="Login", command=login_action).pack(padx=10, pady=20)
        root.mainloop()


    def create_user_form(self):
        def create_user_action():
            username = entry_username.get()
            password = entry_password.get()
            confirm_password = entry_confirm_password.get()
            role = entry_user_role.get()

            hashed_password, salt = self.hash_password(password)

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match!")
                root.lift()
                root.focus_force()
                return

            if not self.check_password_policy(username, password):
                root.lift()
                root.focus_force()
                return


            from db import Database
            db = Database()
            try:
                db.create_user(username, hashed_password, salt, role)
                messagebox.showinfo("Success", "New user created!")
                root.destroy()  # Close the window after user creation
            except Exception as e:
                messagebox.showerror("Error", e)

        root = tk.Tk()
        root.title("Create User")

        tk.Label(root, text="Username").pack(padx=10, pady=5)
        entry_username = tk.Entry(root)
        entry_username.pack(padx=10, pady=5)

        tk.Label(root, text="Password").pack(padx=10, pady=5)
        entry_password = tk.Entry(root, show="*")
        entry_password.pack(padx=10, pady=5)

        tk.Label(root, text="Confirm Password").pack(padx=10, pady=5)
        entry_confirm_password = tk.Entry(root, show="*")
        entry_confirm_password.pack(padx=10, pady=5)

        tk.Label(root, text="User Role").pack(padx=10, pady=5)
        entry_user_role = tk.Entry(root)
        entry_user_role.pack(padx=10, pady=5)
        
        tk.Button(root, text="Create User", 
                command=create_user_action).pack(padx=10, pady=20)
        root.mainloop()
