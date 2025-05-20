import tkinter as tk
from tkinter import messagebox
from db import Database
from auth import Authentication
from membership_tracker import BusinessApp

def main():
    root = tk.Tk()
    root.withdraw()
    
    def launch_auth(): 
        try:
            db = Database()
            auth = Authentication(root)

            if db.are_users_exist():
                auth.login_form()
            else:
                auth.create_user_form(startup=True)
            
        except Exception as e:
            messagebox.showerror(f"Program failed to launch", str(e), 
                parent=root)
            root.destroy()
        
    root.after(0, launch_auth)
    root.mainloop()    
if __name__ == "__main__":
    main()
