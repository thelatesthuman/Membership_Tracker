import os
import platform
import json
import tkinter as tk
from psycopg2 import errors
from tkinter import *
from tkinter import ttk, font, filedialog, messagebox
from tkcalendar import DateEntry
from datetime import datetime
from db import Database

class BusinessApp:
    db = Database()
    def __init__(self, root, current_user):
        self.system_info = platform.uname()
        self.user_login = os.getlogin()
        
        if self.system_info[0] == "Linux":
            config_path = "/home/" + self.user_login + "/.member_track/config.json"
        elif self.system_info[0] == "Windows":
            config_path = "C:/Users/" + self.user_login + "/AppData/Local/MembershipTracker/config.json"
        else:
            config_path = "config.json"

        with open(config_path, 'r') as f:
            config = json.load(f)

        self.business_name = config["business_name"]

        self.current_user = current_user
        self.is_admin = self.db.get_user_role(self.current_user) == 'admin' 

        self.root = root
        self.root.title("Memberships")
       
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.frm = ttk.Frame(root, padding=200)
        self.frm.grid(sticky="nsew")

        def export_data():
            # Open the save file dialog
            filepath = filedialog.asksaveasfilename(
                title="Export as...",  # Title of the dialog box
                #defaultextension=".csv",  # Default file extension
#                filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),  # Allowed file types
            )
            
            if filepath:  # If a file path is chosen
                messagebox.showinfo("Success", 
                    f"Saved file to: {filepath}")
                try:
                    db = Database()
                    db.export_data(filepath)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export file: {str(e)}")


        def close_app():
            self.root.destroy()

        menu_bar = tk.Menu(root)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export", command=export_data)
        file_menu.add_command(label="Close", command=close_app)

        menu_bar.add_cascade(label="File", menu=file_menu)
        
        root.config(menu=menu_bar)
    
        for i in range(7):
            self.frm.grid_rowconfigure(i, weight=1)
        
        for i in range(3):
            self.frm.grid_columnconfigure(i, weight=1)

        bold_font = font.nametofont("TkDefaultFont")
        bold_font.actual()["weight"] = "bold"
            
        self.title = ttk.Label(self.frm, 
                text=self.business_name,
                font=bold_font,
                foreground='blue')
        self.title.grid(column=1, row=0)

        self.first_name_label = ttk.Label(self.frm, text='First Name')
        self.first_name_label.grid(column=0, row=1, sticky=W)
        self.first_name_entry = ttk.Entry(self.frm)
        self.first_name_entry.grid(column=1, row=1, sticky="ew")

        self.last_name_label = ttk.Label(self.frm, text='Last Name')
        self.last_name_label.grid(column=0, row=2, sticky=W)
        self.last_name_entry = ttk.Entry(self.frm)
        self.last_name_entry.grid(column=1, row=2, sticky="ew")

        self.phone_number_label = ttk.Label(self.frm, text='Phone Number')
        self.phone_number_label.grid(column=0, row=3, sticky=W)
        self.phone_number_entry = ttk.Entry(self.frm)
        self.phone_number_entry.grid(column=1, row=3, sticky="ew")

        self.search_button = ttk.Button(self.frm, text='Search', command=self.on_search)
        self.search_button.grid(column=1, row=4, sticky="ew")
        self.search_button.bind('<Return>', lambda event: self.on_search())

        self.search_all_button = ttk.Button(self.frm, text='Search All', 
                command=self.on_search_all)
        self.search_all_button.grid(column=2, row=4, sticky="ew")
        self.search_all_button.bind('<Return>', lambda event: self.on_search_all())
        
#        self.close_button = ttk.Button(self.frm, text='Close', command=self.root.destroy)
#        self.close_button.grid(column=0, row=4, sticky="ew")
#        self.close_button.bind('<Return>', lambda event: self.root.destroy())

        self.add_mem_window_button = ttk.Button(self.frm, text="Add Member", 
                command=self.add_member_window)
        self.add_mem_window_button.grid(column=1, row=5, sticky="ew")
        self.add_mem_window_button.bind('<Return>', lambda event: self.add_member_window())
        

        self.create_user_button = None
        if self.is_admin:
            from auth import Authentication
            auth = Authentication()
            self.create_user_button = tk.Button(self.frm, 
                    text="Create User", 
                    command=auth.create_user_form)
            self.create_user_button.grid(column=1, row=6, sticky="ew") 
        
        self.search_all_flag = False

        # TODO: Need to fix right click/copy functionality
    def show_right_click_menu(self, event):
        """Displays the right-click menu when a row is selected"""
        item = self.tree.identify('item', event.x, event.y) 
        if item:
            self.tree.selection_set(item)  
            self.context_menu.post(event.x_root, event.y_root)


        # TODO: Need to fix right click/copy functionality
    def copy_to_clipboard(self):
        """Copies the selected row's data to the clipboard"""
        selected_item = self.tree.selection()
        if selected_item:
            row_data = self.tree.item(selected_item[0])['values']
            text_to_copy = "".join(str(row_data))
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)
            self.root.update()
        

    def on_search(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        phone_number = self.phone_number_entry.get()
        self.search_all_flag = False
        self.search_members(first_name, last_name, phone_number, search_all=False)


    def on_search_all(self):
        self.search_all_flag = True
        self.search_members(search_all=True)


    # Function to search database and allow editing
    def search_members(self, 
            first_name=None, 
            last_name=None, 
            phone_number=None, 
            search_all=False):

        self.search_window = Toplevel(self.root)
        self.search_window.title("Member Info")
        self.search_window.geometry("1700x500")

        self.search_window.grid_rowconfigure(0, weight=1)
        self.search_window.grid_columnconfigure(0, weight=1)

        self.search_frame = ttk.Frame(self.search_window, padding=10)
        self.search_frame.grid(sticky="nsew")
       
        self.search_frame.grid_rowconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_all_flag = search_all

        if search_all == False:
            members = self.db.search_members(
                    first_name.lower(), 
                    last_name.lower(), 
                    phone_number)
        else:
            members = self.db.search_all_members()

        # Create dropdowns for membership type and active status
        self.membership_filter = ttk.Combobox(self.search_frame,
                                               values=[
                                                   "All Memberships", 
                                                   "premium", 
                                                   "standard"],
                                               state="readonly")
        self.membership_filter.set("All Memberships")
        self.membership_filter.grid(column=4, row=1, sticky='w')

        self.active_filter = ttk.Combobox(self.search_frame,
                                          values=[
                                              "All Status", 
                                              "Active", 
                                              "Not Active"],
                                          state="readonly")
        self.active_filter.set("All Status")
        self.active_filter.grid(column=4, row=1, sticky='e')

        self.membership_filter.bind("<<ComboboxSelected>>", self.apply_filters)
        self.active_filter.bind("<<ComboboxSelected>>", self.apply_filters)


         # Clear previous results if any
        for widget in self.search_frame.winfo_children():
            if isinstance(widget, ttk.Treeview):
                widget.destroy()

        # Create a Treeview widget to display results
        columns = (
                'Member ID',
                'First Name', 
                'Last Name', 
                'Phone Number',
                'Email',
                'Member Start', 
                'Member Expire', 
                'Store Credit',
                'Membership Type',
                'Active')

        self.tree = ttk.Treeview(self.search_frame, columns=columns, show="headings")
        self.tree.grid(column=0, row=4, columnspan=5, sticky="nsew")

        self.search_frame.grid_rowconfigure(4, weight=1)
        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(1, weight=1)
        self.search_frame.grid_columnconfigure(2, weight=1)
        self.search_frame.grid_columnconfigure(3, weight=1)
        self.search_frame.grid_columnconfigure(4, weight=1)

        self.tree.tag_configure('active', font=('Ariel', 10, 'bold'), foreground='green')
        self.tree.tag_configure('not active', font=('Ariel', 10, 'bold'), foreground='red')
        
        self.tree.column('#1', minwidth=100, width=100)
        self.tree.column('#2', minwidth=100, width=100)
        self.tree.column('#3', minwidth=100, width=100)
        self.tree.column('#4', minwidth=100, width=100)
        self.tree.column('#5', minwidth=100, width=100)
        self.tree.column('#6', minwidth=100, width=100)
        self.tree.column('#7', minwidth=100, width=100)

        # TODO: Need to fix right click/copy functionality
        # Bind the right-click event to show the context menu
        self.tree.bind("<Button-3>", self.show_right_click_menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="View Profile", command=self.view_profile)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", stretch=True)

        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))

        self.members = members  # Store members data globally for sorting
        self.filtered_members = members
        self.display_members(members)  # Display members initially

        update_member_button = ttk.Button(self.search_frame, 
                text="Update Member", 
                command=self.on_update_member)
        update_member_button.grid(column=4, row=5, columnspan=1, sticky='ew')
        update_member_button.bind('<Return>', lambda event: self.on_update_member())

        update_credit_button = ttk.Button(self.search_frame, 
                text="Update Credit", 
                command=self.on_update_credit)
        update_credit_button.grid(column=2, row=5, columnspan=1, sticky='ew')
        update_credit_button.bind('<Return>', lambda event: self.on_update_credit())

        show_transactions_button = ttk.Button(self.search_frame, 
                text="Transaction History", 
                command=self.on_transactions)
        show_transactions_button.grid(column=2, row=6, columnspan=1, sticky='ew')
        show_transactions_button.bind('<Return>', lambda event: self.on_transactions())

        delete_button = ttk.Button(self.search_frame, text="Delete", 
                command=self.on_delete)
        delete_button.grid(column=0, row=5, columnspan=1, sticky='ew')
        delete_button.bind('<Return>', lambda event: self.on_delete())

        close_button = ttk.Button(self.search_frame, text='Close', 
                command=self.search_window.destroy)
        close_button.grid(column=4, row=6, columnspan=1, sticky='ew')
        close_button.bind('<Return>', lambda event: self.search_window.destroy())


    def apply_filters(self, event=None):
        """Applies the filters based on dropdown selections"""
        membership_filter = self.membership_filter.get()
        active_filter = self.active_filter.get()

        self.filtered_members = self.members

        # Filter by Membership Type
        if membership_filter != "All Memberships":
            self.filtered_members = [member for member in self.members if member[8] == membership_filter]

        # Filter by Active Status
        if active_filter != "All Status":
            if active_filter == "Active":
                self.filtered_members = [member for member in self.filtered_members if self.is_active(member)]
            elif active_filter == "Not Active":
                self.filtered_members = [member for member in self.filtered_members if not self.is_active(member)]

        # Clear the Treeview and display the filtered members
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.display_members(self.filtered_members)


    def is_active(self, member):
        """Check if the member is active based on the expire date"""
        expire_date_str = str(member[6])
        expire_date = datetime.strptime(expire_date_str, '%Y-%m-%d')
        return expire_date >= datetime.now()


    # This is where filtered data is officially displayed
    def display_members(self, members):
        for member in members:
            if self.is_active(member):
                active_status = 'ACTIVE'
                status_tag = 'active'
            else:
                active_status = 'NOT ACTIVE'
                status_tag = 'not active'

            self.tree.insert("", "end", 
                    values=member[:-1] + (active_status,), 
                    tags=(status_tag,))
            

    def sort_by_column(self, column):
        # Create the dropdown menu when you click on the "Last Name" column
        if column == "Last Name":
            self.show_sort_dropdown(column)
        else:
            pass


    def show_sort_dropdown(self, column):
        # Create a combobox to act as the dropdown in the header
        sort_dropdown = ttk.Combobox(self.tree, 
                values=["Sort by Last Name (A-Z)", 
                    "Sort by Last Name (Z-A)"], state="readonly")
        sort_dropdown.set("Sort by Last Name (A-Z)")
        
        # Place the combobox over the column header where the user clicked
        sort_dropdown.place(x=300, y=0) 

        def on_dropdown_selected(event):
            sort_order = sort_dropdown.get()
            self.on_sort_selected(sort_order)
            sort_dropdown.destroy()  

        sort_dropdown.bind("<<ComboboxSelected>>", on_dropdown_selected)


    # TODO: Refactor filtering and sorting to clean the code up
    def on_sort_selected(self, sort_order):
        """Handles the sorting based on the combobox selection"""
        #selected_sort = event.widget.get()

        if sort_order == "Sort by Last Name (A-Z)":
            # Sort the members alphabetically by last name
            self.members = sorted(self.members, key=lambda x: x[2].lower())
        elif sort_order == "Sort by Last Name (Z-A)":
            # Sort the members in reverse alphabetical order
            self.members = sorted(self.members, key=lambda x: x[2].lower(), 
                    reverse=True)

        # Clear the Treeview and display the sorted members
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.display_members(self.members)
    

    def on_transactions(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a member to check.")
            return

        selected_member = self.tree.item(selected_item)['values']
        member_id = selected_member[0]

        transactions_window = Toplevel(self.search_window)
        transactions_window.title("Transaction History")

        transactions_frame = ttk.Frame(transactions_window, padding=100)
        transactions_frame.grid()

        transactions = self.db.show_store_credit_transactions(member_id)

        # Clear previous results if any
        for widget in transactions_frame.winfo_children():
            if isinstance(widget, ttk.Treeview):
                widget.destroy()

        # Create a Treeview widget to display results
        columns = (
                'Transaction ID',
                'Member ID',
                'Amount',
                'Transaction Date',
                'Description')
    
        tran_tree = ttk.Treeview(transactions_frame, columns=columns, 
            show="headings")
        tran_tree.grid(column=0, row=4, columnspan=5)
    
        for col in columns:
            tran_tree.heading(col, text=col)
        
        for transaction in transactions:
            tran_tree.insert("", "end", values=transaction)
   
        # TODO: Need to fix right click/copy functionality
        # Bind the right-click event to show the context menu
        tran_tree.bind("<Button-3>", self.show_right_click_menu)
        tran_context_menu = tk.Menu(self.root, tearoff=0)
        tran_context_menu.add_command(label="Copy", command=self.copy_to_clipboard)


    def on_update_credit(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a member to update.")
            return

        selected_member = self.tree.item(selected_item)['values']
        member_id = selected_member[0]

        update_credit_window = Toplevel(self.search_window)
        update_credit_window.title("Update Member Credit")

        update_credit_frame = ttk.Frame(update_credit_window, padding=100)
        update_credit_frame.grid()
        
        update_amount_field = ttk.Label(update_credit_frame, 
                text="Update Amount: ")
        update_amount_field.grid(column=0, row=0, sticky=W)
        update_amount_entry = ttk.Entry(update_credit_frame)
        update_amount_entry.grid(column=1, row=0)
        
        add_description_field = ttk.Label(update_credit_frame, 
                text="Add Description: ")
        add_description_field.grid(column=0, row=1, sticky=W)
        add_description_entry = ttk.Entry(update_credit_frame)
        add_description_entry.grid(column=1, row=1)

        def apply_update():
            updated_amount = update_amount_entry.get()
            add_description = add_description_entry.get()

            if updated_amount == "":
                messagebox.showerror("Error", 
                        "Please fill required fields (Update Amount)")
                return

            try:
                self.db.update_store_credit_transactions(
                        member_id,
                        updated_amount,
                        add_description)
            
                messagebox.showinfo("Success", "Member credit updated successfully!")
                update_credit_window.destroy()  
                self.search_window.destroy()
                if self.search_all_flag:
                    self.on_search_all()
                else:
                    self.on_search()
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update credit: {e}")
        
        
        update_credit_button = ttk.Button(update_credit_frame, 
                text="Update", 
                command=apply_update)
        update_credit_button.grid(column=1, row=6)
        update_credit_button.bind('<Return>', lambda event: apply_update())

    # Function to allow for data editing
    def on_update_member(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a member to update.")
            return

        selected_member = self.tree.item(selected_item)['values']
        member_id = selected_member[0]

        update_member_window = Toplevel(self.search_window)
        update_member_window.title("Update Member Data")

        update_member_frame = ttk.Frame(update_member_window, padding=100)
        update_member_frame.grid()

        update_first_name_field = ttk.Label(update_member_frame, 
                text="First Name: ")
        update_first_name_field.grid(column=0, row=0, sticky=W)
        update_first_name_entry = ttk.Entry(update_member_frame)
        update_first_name_entry.insert(0, selected_member[1])
        update_first_name_entry.grid(column=1, row=0)

        update_last_name_field = ttk.Label(update_member_frame, 
                text="Last Name: ")
        update_last_name_field.grid(column=0, row=1, sticky=W)
        update_last_name_entry = ttk.Entry(update_member_frame)
        update_last_name_entry.insert(0, selected_member[2])
        update_last_name_entry.grid(column=1, row=1)

        update_phone_number_field = ttk.Label(update_member_frame, 
                text="Phone Number: ")
        update_phone_number_field.grid(column=0, row=2, sticky=W)
        update_phone_number_entry = ttk.Entry(update_member_frame)
        update_phone_number_entry.insert(0, selected_member[3])
        update_phone_number_entry.grid(column=1, row=2)
        
        update_email_field = ttk.Label(update_member_frame, 
                text="Email: ")
        update_email_field.grid(column=0, row=3, sticky=W)
        update_email_entry = ttk.Entry(update_member_frame)
        update_email_entry.insert(0, selected_member[4])
        update_email_entry.grid(column=1, row=3)
        
        update_member_start_field = ttk.Label(update_member_frame, 
                text="Member Start: ")
        update_member_start_field.grid(column=0, row=4, sticky=W)
        update_member_start_entry = DateEntry(update_member_frame, 
                date_pattern='yyyy-mm-dd')
        update_member_start_entry.delete(0, 'end')
        update_member_start_entry.insert(0, selected_member[5])
        update_member_start_entry.grid(column=1, row=4)

        update_member_expire_field = ttk.Label(update_member_frame, 
                text="Member Expire: ")
        update_member_expire_field.grid(column=0, row=5, sticky=W)
        update_member_expire_entry = DateEntry(update_member_frame, 
                date_pattern='yyyy-mm-dd')
        update_member_expire_entry.delete(0, 'end')
        update_member_expire_entry.insert(0, selected_member[6])
        update_member_expire_entry.grid(column=1, row=5)

        update_member_type_field = ttk.Label(update_member_frame, 
                text="Membership Type: ")
        update_member_type_field.grid(column=0, row=6, sticky=W)
        update_member_type_entry = ttk.Entry(update_member_frame)
        update_member_type_entry.insert(0, selected_member[8])
        update_member_type_entry.grid(column=1, row=6)

        def apply_update():
            # Collect updated data
            updated_data = {
                'first_name': update_first_name_entry.get().strip(),
                'last_name': update_last_name_entry.get().strip(),
                'phone_number': update_phone_number_entry.get().strip(),
                'email': update_email_entry.get(),
                'member_start': update_member_start_entry.get(),
                'member_expire': update_member_expire_entry.get(),
                'member_type': update_member_type_entry.get().lower()
            }

            # Validate required fields
            if not validate_required_fields(updated_data):
                return

            original_data = {
                'member_id': selected_member[0],    
                'first_name': selected_member[1],
                'last_name': selected_member[2],
                'phone_number': str(selected_member[3]),
                'email': selected_member[4],
                'member_start': selected_member[5],
                'member_expire': selected_member[6],
                'member_type': selected_member[7]
            }

            # Check for updates in the fields
            if not has_fields_updated(updated_data, original_data):
                print("No fields have been updated, skipping duplicate check")
                return

            # Perform duplicate check
            if is_duplicate(updated_data):
                return

            # Update member data in the database
            try:
                update_member_in_db(updated_data)
                messagebox.showinfo("Success", "Member data updated successfully!")
                close_windows_and_refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update member: {e}")

        def validate_required_fields(updated_data):
            if updated_data['first_name'] == "" or updated_data['last_name'] == "" or updated_data['phone_number'] == "":
                messagebox.showerror("Error", "Please fill required fields (First Name, Last Name, Phone Number)")
                return False
            return True

        def has_fields_updated(updated_data, original_data):
            return (updated_data['first_name'].lower() != original_data['first_name'].lower() or updated_data['last_name'].lower() != original_data['last_name'].lower() or updated_data['phone_number'] != original_data['phone_number'] or updated_data['email'] != original_data['email'] or updated_data['member_start'] != original_data['member_start'] or updated_data['member_expire'] != original_data['member_expire'] or updated_data['member_type'] != original_data['member_type'])

        def is_duplicate(updated_data):
            member_check_tuple = self.db.search_members(
                updated_data['first_name'].lower(),
                updated_data['last_name'].lower(),
                updated_data['phone_number']
            )

            for member in member_check_tuple:
                if member[0] != member_id and (
                    (updated_data['first_name'] == member[1] and updated_data['last_name'] == member[2]) or updated_data['phone_number'] == member[3]):
                    confirm = messagebox.askyesno("Warning!", "Member name or phone number exists!\nContinue?")
                    return not confirm  # return False if user cancels (stopping update)
            return False

        def update_member_in_db(updated_data):
            self.db.update_member(
                member_id,
                updated_data['first_name'],
                updated_data['last_name'],
                updated_data['phone_number'],
                updated_data['email'],
                updated_data['member_start'],
                updated_data['member_expire'],
                updated_data['member_type']
            )

        def close_windows_and_refresh():
            update_member_window.destroy()
            self.search_window.destroy()
            if self.search_all_flag:
                self.on_search_all()
            else:
                self.on_search()


        update_button = ttk.Button(update_member_frame, 
                text="Update", 
                command=apply_update)
        update_button.grid(column=1, row=7)
        update_button.bind('<Return>', lambda event: apply_update())

    # Function to delete member data
    def on_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a member to delete.")
            return

        selected_member = self.tree.item(selected_item)['values']
        member_id = selected_member[0]
        first_name = selected_member[1]
        last_name = selected_member[2]

        delete_confirm = messagebox.askyesno("Delete user?", 
                f"Are you sure you want to delete {first_name} {last_name}?")

        if delete_confirm == True:
            try:
                self.db.delete_member(member_id)

                messagebox.showinfo("Success", "Member data deleted successfully!")
                self.search_window.destroy()
                if self.search_all_flag:
                    self.on_search_all()
                else:
                    self.on_search()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete member: {e}")


    def add_member_window(self):
        add_mem_window = Toplevel(self.root)
        add_mem_window.title("Add Member")

        add_mem_frame = ttk.Frame(add_mem_window, padding=300)
        add_mem_frame.grid()

        first_name_field = ttk.Label(add_mem_frame, text="First Name: ")
        first_name_field.grid(column=0, row=0, sticky=W)
        first_name_entry = ttk.Entry(add_mem_frame)
        first_name_entry.grid(column=1, row=0)
        
        last_name_field = ttk.Label(add_mem_frame, text="Last Name: ")
        last_name_field.grid(column=0, row=1, sticky=W)
        last_name_entry = ttk.Entry(add_mem_frame)
        last_name_entry.grid(column=1, row=1)

        phone_number_field = ttk.Label(add_mem_frame, text="Phone Number: ")
        phone_number_field.grid(column=0, row=2, sticky=W)
        phone_number_entry = ttk.Entry(add_mem_frame)
        phone_number_entry.grid(column=1, row=2)
        
        email_field = ttk.Label(add_mem_frame, text="Email: ")
        email_field.grid(column=0, row=3, sticky=W)
        email_entry = ttk.Entry(add_mem_frame)
        email_entry.grid(column=1, row=3)
        
        member_start_field = ttk.Label(add_mem_frame, text="Member Start: ")
        member_start_field.grid(column=0, row=4, sticky=W)
        member_start_entry = DateEntry(add_mem_frame, date_pattern='yyyy-mm-dd')
        member_start_entry.grid(column=1, row=4)
        
        member_expire_field = ttk.Label(add_mem_frame, text="Member Expire: ")
        member_expire_field.grid(column=0, row=5, sticky=W)
        member_expire_entry = DateEntry(add_mem_frame, date_pattern='yyyy-mm-dd')
        member_expire_entry.grid(column=1, row=5)
        
        store_credit_field = ttk.Label(add_mem_frame, text="Store Credit: ")
        store_credit_field.grid(column=0, row=6, sticky=W)
        store_credit_entry = ttk.Entry(add_mem_frame)
        store_credit_entry.grid(column=1, row=6)
       
        member_type_field = ttk.Label(add_mem_frame, text="Membership Type: ")
        member_type_field.grid(column=0, row=7, sticky=W)
        member_type_entry = ttk.Entry(add_mem_frame)
        member_type_entry.grid(column=1, row=7)

        def on_submit():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            phone_number = phone_number_entry.get()
            email = email_entry.get()
            member_start = member_start_entry.get()
            member_expire = member_expire_entry.get()
            store_credit = store_credit_entry.get()
            member_type = member_type_entry.get()

            if first_name == "" or last_name == "" or phone_number == "":
                messagebox.showerror("Error", 
                        "Please fill required fields (First Name, Last Name, Phone Number)")
                return
            if email == "":
                email = "none"
            if store_credit == "":
                store_credit = 0
            if member_type == "":
                member_type = "standard"

            member_check_tuple = self.db.search_members(
                    first_name.lower(), 
                    last_name.lower(), 
                    phone_number)
           
            member_check_confirm = True

            for member in member_check_tuple:
                if (first_name == member[1] and last_name == member[2]) or phone_number == member[3]:
                    member_check_confirm = messagebox.askyesno("Warning!", 
                            f"Member name or phone number exists!\nContinue?")
                    break


            if member_check_confirm == True:
                try:    
                    self.db.add_member(
                            first_name.lower(),
                            last_name.lower(),
                            phone_number,
                            email,
                            member_start,
                            member_expire,
                            store_credit,
                            member_type.lower())
                    
                    messagebox.showinfo("Success", "Member added successfully")
                    
                    # Clear form
                    first_name_entry.delete(0, tk.END)
                    last_name_entry.delete(0, tk.END)
                    phone_number_entry.delete(0, tk.END)
                    email_entry.delete(0, tk.END)
                    member_start_entry.delete(0, tk.END)
                    member_expire_entry.delete(0, tk.END)
                    store_credit_entry.delete(0, tk.END)
                    member_type_entry.delete(0, tk.END)
                
                except errors.InvalidTextRepresentation:
                    messagebox.showerror("Error", "Please fill required fields (First Name, Last Name, Phone Number)")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add member: {e}")


        submit_button = ttk.Button(add_mem_frame, text="Submit", command=on_submit)
        submit_button.grid(column=1, row=8)
        submit_button.bind('<Return>', lambda event: on_submit())

        close_button = ttk.Button(add_mem_frame, text='Close', 
                command=add_mem_window.destroy)
        close_button.grid(column=0, row=8)
        close_button.bind('<Return>', lambda even: add_mem_window.destroy())
    

    def view_profile(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a member profile to view.")
            return

        selected_member = self.tree.item(selected_item)['values']
        
        # Create or refresh the profile window
        if hasattr(self, 'view_profile_window') and self.view_profile_window.winfo_exists():
        # If the window already exists, destroy it to refresh
            self.view_profile_window.destroy()

        self.view_profile_window = Toplevel(self.search_window)
        self.view_profile_window.title("View Profile")

        view_profile_frame = ttk.Frame(self.view_profile_window, 
            padding=100)
        view_profile_frame.grid()
        
        if self.is_active(selected_member):
            active_status = 'ACTIVE'
            #status_tag = 'active'
            status_color = 'green'
        else:
            active_status = 'NOT ACTIVE'
            #status_tag = 'not active'
            status_color = 'red'
        bold_font = ('Helvetica', 10, 'bold')
        
        db = Database()
        photo_data = db.get_member_photo(selected_member[0])

        from PIL import Image, ImageTk
        from io import BytesIO
        if photo_data:
            # Convert photo data (binary) to an image object
            photo_image = Image.open(BytesIO(photo_data))
            photo_image = photo_image.resize((200, 200))  # Resize to fit the profile window (optional)
            photo = ImageTk.PhotoImage(photo_image)
        else:
            # Set a default photo if no photo is found
            photo = ImageTk.PhotoImage(Image.open('pics/default_member_photo.jpg').resize((200, 200)))

        # Display the photo
        photo_label = ttk.Label(view_profile_frame, image=photo)
        photo_label.image = photo  # Keep a reference to the image to prevent it from being garbage collected
        photo_label.grid(column=1, row=0, rowspan=4, sticky=W)

        view_first_name_field = ttk.Label(view_profile_frame, 
                text="First Name: ")
        view_first_name_field.grid(column=0, row=5, sticky=W)
        view_first_name_label = ttk.Label(view_profile_frame,
                text=selected_member[1])
        view_first_name_label.grid(column=1, row=5)

        view_last_name_field = ttk.Label(view_profile_frame, 
                text="Last Name: ")
        view_last_name_field.grid(column=0, row=6, sticky=W)
        view_last_name_label = ttk.Label(view_profile_frame,
                text=selected_member[2])
        view_last_name_label.grid(column=1, row=6)

        view_phone_number_field = ttk.Label(view_profile_frame, 
                text="Phone Number: ")
        view_phone_number_field.grid(column=0, row=7, sticky=W)
        view_phone_number_label = ttk.Label(view_profile_frame,
                text=selected_member[3])
        view_phone_number_label.grid(column=1, row=7)
        
        view_email_field = ttk.Label(view_profile_frame, 
                text="Email: ")
        view_email_field.grid(column=0, row=8, sticky=W)
        view_email_label = ttk.Label(view_profile_frame,
                text=selected_member[4])
        view_email_label.grid(column=1, row=8)
        
        view_member_start_field = ttk.Label(view_profile_frame, 
                text="Member Start: ")
        view_member_start_field.grid(column=0, row=9, sticky=W)
        view_member_start_label = ttk.Label(view_profile_frame, 
                text=selected_member[5])
        view_member_start_label.grid(column=1, row=9)

        view_member_expire_field = ttk.Label(view_profile_frame, 
                text="Member Expire: ")
        view_member_expire_field.grid(column=0, row=10, sticky=W)
        view_member_expire_label = ttk.Label(view_profile_frame, 
                text=selected_member[6])
        view_member_expire_label.grid(column=1, row=10)

        view_store_credit_field = ttk.Label(view_profile_frame, 
                text="Store Credit: ")
        view_store_credit_field.grid(column=0, row=11, sticky=W)
        view_store_credit_label = ttk.Label(view_profile_frame, 
                text=selected_member[7])
        view_store_credit_label.grid(column=1, row=11)
        
        view_member_type_field = ttk.Label(view_profile_frame, 
                text="Membership Type: ")
        view_member_type_field.grid(column=0, row=12, sticky=W)
        view_member_type_label = ttk.Label(view_profile_frame, 
                text=selected_member[8])
        view_member_type_label.grid(column=1, row=12)

        view_member_status_field = ttk.Label(view_profile_frame, 
                text="Membership Status: ")
        view_member_status_field.grid(column=0, row=13, sticky=W)
        view_member_status_label = ttk.Label(view_profile_frame, 
                text=active_status, foreground=status_color, 
                    font=bold_font)
        view_member_status_label.grid(column=1, row=13)

        update_photo_button = ttk.Button(self.view_profile_window, 
            text="Update Photo", 
            command=lambda: self.update_photo(selected_member[0]))
        update_photo_button.grid(column=1, row=14, columnspan=2)
        
        #self.view_profile_window.after(100, 
        #    self.view_profile_window.lift())
        #self.view_profile_window.after(100, 
        #    self.view_profile_window.focus_set())
        #self.view_profile_window.grab_set()
        self.view_profile_window.lift()
        self.view_profile_window.focus_force()


    def update_photo(self, member_id):
        # Open file dialog to choose a new photo
        file_path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[("JPEG files", "*.jpg"),
                  ("JPEG files", "*.jpeg"), 
                  ("PNG files", "*.png"), 
                  ("GIF files", "*.gif"), 
                  ("All Image Files", "*.*")]
        )
        if not file_path:
            return  # User canceled the file dialog

        try:
            # Open the image and convert it to binary data
            with open(file_path, 'rb') as f:
                photo_data = f.read()

            # Store the new photo in the database
            db = Database()
            db.update_member_photo(member_id, photo_data)

            self.view_profile()

            messagebox.showinfo("Success", 
                "Profile photo updated successfully.")

        except Exception as e:
            messagebox.showerror("Error", 
                f"Failed to update photo: {str(e)}")
