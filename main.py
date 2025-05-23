import os
import logging
import platform
import tkinter as tk
from tkinter import messagebox
from db import Database
from auth import Authentication
from membership_tracker import BusinessApp

def setup_logging():
    system_info = platform.uname()
    user_login = os.getlogin()
        
    if system_info[0] == "Linux":
        log_file_path = "/home/" + user_login + "/.member_track/member_track.log"
    elif system_info[0] == "Windows":
        log_file_path = "C:/Users/" + user_login + "/AppData/Local/MembershipTracker/member_track.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            #logging.StreamHandler()
        ]
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting the application")

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
