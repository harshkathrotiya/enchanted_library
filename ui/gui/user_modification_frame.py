import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from models.user import UserRole

class UserModificationFrame(ttk.Frame):
    

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.create_user_modification_ui()

    def create_user_modification_ui(self):
        

        title_label = ttk.Label(self, text="User Modification", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        if not self.controller.current_user or self.controller.current_user.get_role().name != 'LIBRARIAN':
            ttk.Label(self, text="Only librarians can modify users",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        update_frame = ttk.Frame(notebook)
        remove_frame = ttk.Frame(notebook)
        renew_frame = ttk.Frame(notebook)

        notebook.add(update_frame, text="Update User")
        notebook.add(remove_frame, text="Remove User")
        notebook.add(renew_frame, text="Renew Membership")

        self.create_update_tab(update_frame)
        self.create_remove_tab(remove_frame)
        self.create_renew_tab(renew_frame)

    def create_update_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select User:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.update_user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(frame, textvariable=self.update_user_var, width=50)
        self.user_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.update_user_combo()

        load_button = ttk.Button(frame, text="Load User",
                               command=self.load_user_for_update)
        load_button.grid(row=0, column=3, padx=5, pady=5)

        details_frame = ttk.LabelFrame(frame, text="User Details")
        details_frame.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW, padx=5, pady=10)

        ttk.Label(details_frame, text="Name:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, width=40).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="Email:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.email_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.email_var, width=40).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="Role:", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.role_var = tk.StringVar()
        roles = [role.name for role in UserRole]
        role_combo = ttk.Combobox(details_frame, textvariable=self.role_var,
                                values=roles, width=15)
        role_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="Membership Expiry:", font=('Helvetica', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)

        expiry_frame = ttk.Frame(details_frame)
        expiry_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        self.expiry_year_var = tk.StringVar()
        self.expiry_month_var = tk.StringVar()
        self.expiry_day_var = tk.StringVar()

        ttk.Entry(expiry_frame, textvariable=self.expiry_year_var, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(expiry_frame, text="-").pack(side=tk.LEFT)
        ttk.Entry(expiry_frame, textvariable=self.expiry_month_var, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(expiry_frame, text="-").pack(side=tk.LEFT)
        ttk.Entry(expiry_frame, textvariable=self.expiry_day_var, width=4).pack(side=tk.LEFT, padx=2)

        ttk.Label(expiry_frame, text="(YYYY-MM-DD)", font=('Helvetica', 8)).pack(side=tk.LEFT, padx=5)

        self.user_id_var = tk.StringVar()

        update_button = ttk.Button(frame, text="Update User",
                                 command=self.update_user,
                                 style='Primary.TButton')
        update_button.grid(row=2, column=0, columnspan=4, pady=20)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def create_remove_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select User to Remove:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.remove_user_var = tk.StringVar()
        remove_user_combo = ttk.Combobox(frame, textvariable=self.remove_user_var, width=50)
        remove_user_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        users = list(self.controller.catalog._users.values())
        remove_user_combo['values'] = [f"{user.name} ({user.email})" for user in users]

        details_frame = ttk.LabelFrame(frame, text="User Details")
        details_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=10)

        self.remove_details_text = tk.Text(details_frame, wrap=tk.WORD, height=10, width=60)
        self.remove_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.remove_details_text.config(state=tk.DISABLED)

        load_button = ttk.Button(frame, text="Load User Details",
                               command=self.load_user_for_removal)
        load_button.grid(row=2, column=0, columnspan=2, pady=10)

        remove_button = ttk.Button(frame, text="Remove User",
                                 command=self.remove_user,
                                 style='Error.TButton')
        remove_button.grid(row=3, column=0, columnspan=2, pady=10)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def create_renew_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Guest User:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.renew_user_var = tk.StringVar()
        self.renew_user_combo = ttk.Combobox(frame, textvariable=self.renew_user_var, width=50)
        self.renew_user_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        self.update_guest_combo()

        ttk.Label(frame, text="Current Expiry:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.current_expiry_var = tk.StringVar()
        current_expiry_label = ttk.Label(frame, textvariable=self.current_expiry_var,
                                       font=('Helvetica', 10))
        current_expiry_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Extend by (months):", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.extend_months_var = tk.StringVar(value="12")
        extend_months_entry = ttk.Spinbox(frame, from_=1, to=36,
                                        textvariable=self.extend_months_var, width=10)
        extend_months_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="New Expiry:", font=('Helvetica', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)

        self.new_expiry_var = tk.StringVar()
        new_expiry_label = ttk.Label(frame, textvariable=self.new_expiry_var,
                                   font=('Helvetica', 10))
        new_expiry_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        calculate_button = ttk.Button(frame, text="Calculate New Expiry",
                                    command=self.calculate_new_expiry)
        calculate_button.grid(row=4, column=0, columnspan=2, pady=10)

        renew_button = ttk.Button(frame, text="Renew Membership",
                                command=self.renew_membership,
                                style='Primary.TButton')
        renew_button.grid(row=5, column=0, columnspan=2, pady=10)

        frame.columnconfigure(1, weight=1)

    def update_user_combo(self):
        

        users = list(self.controller.catalog._users.values())

        self.user_combo['values'] = [f"{user.name} ({user.email})" for user in users]

    def update_guest_combo(self):
        

        guest_users = []
        for user in self.controller.catalog._users.values():
            if user.get_role().name == 'GUEST':
                guest_users.append(user)

        self.renew_user_combo['values'] = [
            f"{user.name} ({user.email}) - Expires: {user.membership_expiry.strftime('%Y-%m-%d') if user.membership_expiry else 'N/A'}"
            for user in guest_users
        ]

    def load_user_for_update(self):
        

        user_selection = self.update_user_var.get()
        if not user_selection:
            messagebox.showerror("Error", "Please select a user")
            return

        email = user_selection.split('(')[1].split(')')[0]

        user = None
        for u in self.controller.catalog._users.values():
            if u.email == email:
                user = u
                break

        if not user:
            messagebox.showerror("Error", "User not found")
            return

        self.user_id_var.set(user.user_id)
        self.name_var.set(user.name)
        self.email_var.set(user.email)
        self.role_var.set(user.get_role().name)

        if hasattr(user, 'membership_expiry') and user.membership_expiry:
            self.expiry_year_var.set(user.membership_expiry.year)
            self.expiry_month_var.set(f"{user.membership_expiry.month:02d}")
            self.expiry_day_var.set(f"{user.membership_expiry.day:02d}")
        else:
            self.expiry_year_var.set("")
            self.expiry_month_var.set("")
            self.expiry_day_var.set("")

    def update_user(self):
        

        user_id = self.user_id_var.get()
        if not user_id:
            messagebox.showerror("Error", "No user selected")
            return

        user = self.controller.catalog.get_user(user_id)
        if not user:
            messagebox.showerror("Error", "User not found")
            return

        name = self.name_var.get()
        email = self.email_var.get()
        role_name = self.role_var.get()

        if not name or not email:
            messagebox.showerror("Error", "Name and email are required")
            return

        for u in self.controller.catalog._users.values():
            if u.email == email and u.user_id != user_id:
                messagebox.showerror("Error", f"Email '{email}' is already in use")
                return

        try:
            role = UserRole[role_name]
        except KeyError:
            messagebox.showerror("Error", f"Invalid role: {role_name}")
            return

        membership_expiry = None
        if role == UserRole.GUEST:
            try:
                if (self.expiry_year_var.get() and
                    self.expiry_month_var.get() and
                    self.expiry_day_var.get()):

                    year = int(self.expiry_year_var.get())
                    month = int(self.expiry_month_var.get())
                    day = int(self.expiry_day_var.get())

                    membership_expiry = datetime(year, month, day)
            except ValueError:
                messagebox.showerror("Error", "Invalid expiry date format")
                return

        user.name = name
        user.email = email

        if user.get_role() != role:
            user.set_role(role)

        if role == UserRole.GUEST and hasattr(user, 'membership_expiry'):
            user.membership_expiry = membership_expiry

        self.controller.catalog.update_user(user)

        messagebox.showinfo("Success", f"User '{name}' updated successfully")

        self.user_id_var.set("")
        self.name_var.set("")
        self.email_var.set("")
        self.role_var.set("")
        self.expiry_year_var.set("")
        self.expiry_month_var.set("")
        self.expiry_day_var.set("")

        self.update_user_combo()
        self.update_guest_combo()

    def load_user_for_removal(self):
        

        user_selection = self.remove_user_var.get()
        if not user_selection:
            messagebox.showerror("Error", "Please select a user")
            return

        email = user_selection.split('(')[1].split(')')[0]

        user = None
        for u in self.controller.catalog._users.values():
            if u.email == email:
                user = u
                break

        if not user:
            messagebox.showerror("Error", "User not found")
            return

        self.remove_details_text.config(state=tk.NORMAL)

        self.remove_details_text.delete(1.0, tk.END)

        details = f"Name: {user.name}\n"
        details += f"Email: {user.email}\n"
        details += f"ID: {user.user_id}\n"
        details += f"Role: {user.get_role().name}\n"

        if hasattr(user, 'membership_expiry') and user.membership_expiry:
            details += f"Membership Expiry: {user.membership_expiry.strftime('%Y-%m-%d')}\n"

        borrowed_books = []
        for record in self.controller.catalog._lending_records.values():
            if record.user_id == user.user_id and record.status.name == 'ACTIVE':
                book = self.controller.catalog.get_book(record.book_id)
                if book:
                    borrowed_books.append(book.title)

        if borrowed_books:
            details += f"\nWARNING: This user has {len(borrowed_books)} borrowed books:\n"
            for title in borrowed_books:
                details += f"- {title}\n"
            details += "\nUser cannot be removed until all books are returned."

        self.remove_details_text.insert(tk.END, details)

        self.remove_details_text.config(state=tk.DISABLED)

    def remove_user(self):
        

        user_selection = self.remove_user_var.get()
        if not user_selection:
            messagebox.showerror("Error", "Please select a user")
            return

        email = user_selection.split('(')[1].split(')')[0]

        user = None
        for u in self.controller.catalog._users.values():
            if u.email == email:
                user = u
                break

        if not user:
            messagebox.showerror("Error", "User not found")
            return

        has_borrowed_books = False
        for record in self.controller.catalog._lending_records.values():
            if record.user_id == user.user_id and record.status.name == 'ACTIVE':
                has_borrowed_books = True
                break

        if has_borrowed_books:
            messagebox.showerror("Error", "Cannot remove user with borrowed books")
            return

        if not messagebox.askyesno("Confirm Removal",
                                 f"Are you sure you want to remove user '{user.name}'?\n\n"
                                 f"This action cannot be undone."):
            return

        self.controller.catalog.remove_user(user.user_id)

        messagebox.showinfo("Success", f"User '{user.name}' removed successfully")

        self.remove_user_var.set("")

        self.remove_details_text.config(state=tk.NORMAL)
        self.remove_details_text.delete(1.0, tk.END)
        self.remove_details_text.config(state=tk.DISABLED)

        self.update_user_combo()
        self.update_guest_combo()

    def calculate_new_expiry(self):
        

        user_selection = self.renew_user_var.get()
        if not user_selection:
            messagebox.showerror("Error", "Please select a user")
            return

        email = user_selection.split('(')[1].split(')')[0]

        user = None
        for u in self.controller.catalog._users.values():
            if u.email == email:
                user = u
                break

        if not user:
            messagebox.showerror("Error", "User not found")
            return

        try:
            months = int(self.extend_months_var.get())
            if months <= 0:
                raise ValueError("Months must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid months: {str(e)}")
            return

        if user.membership_expiry and user.membership_expiry > datetime.now():
            current_expiry = user.membership_expiry
            self.current_expiry_var.set(current_expiry.strftime('%Y-%m-%d'))
        else:
            current_expiry = datetime.now()
            self.current_expiry_var.set("New membership")

        new_expiry = current_expiry + timedelta(days=30*months)
        self.new_expiry_var.set(new_expiry.strftime('%Y-%m-%d'))

    def renew_membership(self):
        

        user_selection = self.renew_user_var.get()
        if not user_selection:
            messagebox.showerror("Error", "Please select a user")
            return

        email = user_selection.split('(')[1].split(')')[0]

        user = None
        for u in self.controller.catalog._users.values():
            if u.email == email:
                user = u
                break

        if not user:
            messagebox.showerror("Error", "User not found")
            return

        try:
            months = int(self.extend_months_var.get())
            if months <= 0:
                raise ValueError("Months must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid months: {str(e)}")
            return

        if user.membership_expiry and user.membership_expiry > datetime.now():
            new_expiry = user.membership_expiry + timedelta(days=30*months)
        else:
            new_expiry = datetime.now() + timedelta(days=30*months)

        user.membership_expiry = new_expiry
        self.controller.catalog.update_user(user)

        messagebox.showinfo("Membership Renewed",
                          f"Membership for {user.name} renewed successfully\n"
                          f"New expiry date: {new_expiry.strftime('%Y-%m-%d')}")

        self.update_guest_combo()

        self.renew_user_var.set("")
        self.current_expiry_var.set("")
        self.new_expiry_var.set("")

    def update_frame(self):
        

        self.update_user_combo()
        self.update_guest_combo()