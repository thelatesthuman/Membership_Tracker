import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from db import Database

class BusinessApp:
    db = Database()
    def __init__(self, root, current_user):
        self.current_user = current_user
        self.is_admin = self.db.get_user_role(self.current_user) == 'admin' 

        self.root = root
        self.root.title("Memberships")
        
        self.frm = ttk.Frame(root, padding=200)
        self.frm.grid()

        bold_font = font.nametofont("TkDefaultFont")
        bold_font.actual()["weight"] = "bold"
            
        self.title = ttk.Label(self.frm, 
                text='Some Business',
                font=bold_font,
                foreground='blue')
        self.title.grid(column=1, row=0)

        self.first_name_label = ttk.Label(self.frm, text='First Name')
        self.first_name_label.grid(column=0, row=1, sticky=W)
        self.first_name_entry = ttk.Entry(self.frm)
        self.first_name_entry.grid(column=1, row=1)

        self.last_name_label = ttk.Label(self.frm, text='Last Name')
        self.last_name_label.grid(column=0, row=2, sticky=W)
        self.last_name_entry = ttk.Entry(self.frm)
        self.last_name_entry.grid(column=1, row=2)

        self.phone_number_label = ttk.Label(self.frm, text='Phone Number')
        self.phone_number_label.grid(column=0, row=3, sticky=W)
        self.phone_number_entry = ttk.Entry(self.frm)
        self.phone_number_entry.grid(column=1, row=3)

        self.search_button = ttk.Button(self.frm, text='Search', command=self.on_search)
        self.search_button.grid(column=1, row=4)
        
        self.search_all_button = ttk.Button(self.frm, text='Search All', 
                command=self.on_search_all)
        self.search_all_button.grid(column=2, row=4)
        
        self.close_button = ttk.Button(self.frm, text='Close', command=self.root.destroy)
        self.close_button.grid(column=0, row=4)

        self.add_mem_window_button = ttk.Button(self.frm, text="Add Member", 
                command=self.add_member_window)
        self.add_mem_window_button.grid(column=1, row=5)

        self.create_user_button = None
        if self.is_admin:
            from auth import Authentication
            auth = Authentication()
            self.create_user_button = tk.Button(self.frm, 
                    text="Create User", 
                    command=auth.create_user_form)
            self.create_user_button.grid(column=1, row=6) 
        
        self.search_all_flag = False

        # TODO: Need to fix right click/copy functionality
    #def show_right_click_menu(self, event):
    #    """Displays the right-click menu when a row is selected"""
    #    item = self.tree.identify('item', event.x, event.y) 
    #    if item:
    #        self.tree.selection_set(item)  
    #        self.context_menu.post(event.x_root, event.y_root)


        # TODO: Need to fix right click/copy functionality
    #def copy_to_clipboard(self):
    #    """Copies the selected row's data to the clipboard"""
    #    selected_item = self.tree.selection()
    #    if selected_item:
    #        row_data = self.tree.item(selected_item[0])['values']
    #        text_to_copy = "".join(str(row_data))
    #        self.root.clipboard_clear()
    #        self.root.clipboard_append(text_to_copy)
    #        self.root.update()


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
        
        self.search_frame = ttk.Frame(self.search_window, padding=100)
        self.search_frame.grid()
       
        self.search_all_flag = search_all

        if search_all == False:
            members = self.db.search_members(
                    first_name.lower(), 
                    last_name.lower(), 
                    phone_number)
        else:
            members = self.db.search_all_members()

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
                'Member Start', 
                'Member Expire', 
                'Store Credit',
                'Active')

        self.tree = ttk.Treeview(self.search_frame, columns=columns, show="headings")
        self.tree.grid(column=0, row=4, columnspan=5)

        self.tree.tag_configure('active', font=('Ariel', 10, 'bold'), foreground='green')
        self.tree.tag_configure('not active', font=('Ariel', 10, 'bold'), foreground='red')
        

        # TODO: Need to fix right click/copy functionality
        # Bind the right-click event to show the context menu
        #self.tree.bind("<Button-3>", self.show_right_click_menu)
        #self.context_menu = tk.Menu(self.root, tearoff=0)
        #self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)

        for col in columns:
            self.tree.heading(col, text=col)

        for member in members:
            expire_date_str = str(member[5])

            expire_date = datetime.strptime(expire_date_str, '%Y-%m-%d')

            if expire_date >= datetime.now():
                active_status = 'ACTIVE'
                status_tag = 'active'
            else:
                active_status = 'NOT ACTIVE'
                status_tag = 'not active'

            self.tree.insert("", "end", values=member + (active_status,), 
                    tags=(status_tag,))

        update_member_button = ttk.Button(self.search_frame, 
                text="Update Member", 
                command=self.on_update_member)
        update_member_button.grid(column=4, row=5, columnspan=1, sticky='ew')
        
        update_credit_button = ttk.Button(self.search_frame, 
                text="Update Credit", 
                command=self.on_update_credit)
        update_credit_button.grid(column=2, row=5, columnspan=1, sticky='ew')
        
        show_transactions_button = ttk.Button(self.search_frame, 
                text="Transaction History", 
                command=self.on_transactions)
        show_transactions_button.grid(column=2, row=6, columnspan=1, sticky='ew')

        delete_button = ttk.Button(self.search_frame, text="Delete", command=self.on_delete)
        delete_button.grid(column=0, row=5, columnspan=1, sticky='ew')
        
        close_button = ttk.Button(self.search_frame, text='Close', 
                command=self.search_window.destroy)
        close_button.grid(column=4, row=6, columnspan=1, sticky='ew')


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
    
        tran_tree = ttk.Treeview(transactions_frame, columns=columns, show="headings")
        tran_tree.grid(column=0, row=4, columnspan=5)
    
        for col in columns:
            tran_tree.heading(col, text=col)
        
        for transaction in transactions:
            tran_tree.insert("", "end", values=transaction)
   
        # TODO: Need to fix right click/copy functionality
        # Bind the right-click event to show the context menu
        #tran_tree.bind("<Button-3>", self.show_right_click_menu)
        #tran_context_menu = tk.Menu(self.root, tearoff=0)
        #tran_context_menu.add_command(label="Copy", command=self.copy_to_clipboard)


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
        
        # Maybe implement calendars for these inputs
        #update_member_start_entry = DateEntry(update_frame, date_pattern='yyyy-mm-dd')
        update_member_start_field = ttk.Label(update_member_frame, 
                text="Member Start: ")
        update_member_start_field.grid(column=0, row=3, sticky=W)
        update_member_start_entry = ttk.Entry(update_member_frame)
        update_member_start_entry.insert(0, selected_member[4])
        update_member_start_entry.grid(column=1, row=3)

        #update_member_expire_entry = DateEntry(update_frame, date_pattern='yyyy-mm-dd')
        update_member_expire_field = ttk.Label(update_member_frame, 
                text="Member Expire: ")
        update_member_expire_field.grid(column=0, row=4, sticky=W)
        update_member_expire_entry = ttk.Entry(update_member_frame)
        update_member_expire_entry.insert(0, selected_member[5])
        update_member_expire_entry.grid(column=1, row=4)


        def apply_update():
            updated_first_name = update_first_name_entry.get()
            updated_last_name = update_last_name_entry.get()
            updated_phone_number = update_phone_number_entry.get()
            updated_member_start = update_member_start_entry.get()
            updated_member_expire = update_member_expire_entry.get()

            try:
                self.db.update_member(
                        member_id, 
                        updated_first_name.lower(), 
                        updated_last_name.lower(), 
                        updated_phone_number,
                        updated_member_start, 
                        updated_member_expire)
                
                messagebox.showinfo("Success", "Member data updated successfully!")
                update_member_window.destroy()  
                self.search_window.destroy()
                if self.search_all_flag:
                    self.on_search_all()
                else:
                    self.on_search()
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update member: {e}")

        update_button = ttk.Button(update_member_frame, 
                text="Update", 
                command=apply_update)
        update_button.grid(column=1, row=6)

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
                messagebox.showerror("Error", f"Failed to update member: {e}")


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
        
        member_start_field = ttk.Label(add_mem_frame, text="Member Start: ")
        member_start_field.grid(column=0, row=3, sticky=W)
        member_start_entry = DateEntry(add_mem_frame, date_pattern='yyyy-mm-dd')
        member_start_entry.grid(column=1, row=3)
        
        member_expire_field = ttk.Label(add_mem_frame, text="Member Expire: ")
        member_expire_field.grid(column=0, row=4, sticky=W)
        member_expire_entry = DateEntry(add_mem_frame, date_pattern='yyyy-mm-dd')
        member_expire_entry.grid(column=1, row=4)
        
        store_credit_field = ttk.Label(add_mem_frame, text="Store Credit: ")
        store_credit_field.grid(column=0, row=5, sticky=W)
        store_credit_entry = ttk.Entry(add_mem_frame)
        store_credit_entry.grid(column=1, row=5)
        
        def on_submit():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            phone_number = phone_number_entry.get()
            member_start = member_start_entry.get()
            member_expire = member_expire_entry.get()
            store_credit = store_credit_entry.get()

            try:    
                self.db.add_member(
                        first_name.lower(),
                        last_name.lower(),
                        phone_number,
                        member_start,
                        member_expire,
                        store_credit)
                
                messagebox.showinfo("Success", "Member added successfully")
                
                # Clear form
                first_name_entry.delete(0, tk.END)
                last_name_entry.delete(0, tk.END)
                phone_number_entry.delete(0, tk.END)
                member_start_entry.delete(0, tk.END)
                member_expire_entry.delete(0, tk.END)
                store_credit_entry.delete(0, tk.END)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to add member: {e}")


        submit_button = ttk.Button(add_mem_frame, text="Submit", command=on_submit)
        submit_button.grid(column=1, row=6)

        close_button = ttk.Button(add_mem_frame, text='Close', 
                command=add_mem_window.destroy)
        close_button.grid(column=0, row=6)

