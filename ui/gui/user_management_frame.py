
import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from datetime import datetime, timedelta

from models.user import UserRole
from patterns.creational.user_factory import UserFactory

class UserManagementFrame(ttk.Frame):

    def __init__(self, parent, controller):

        super().__init__(parent)
        self.controller = controller

        self.create_user_management()

    def create_user_management(self):

        title_label = ttk.Label(self, text="User Management", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        if not self.controller.current_user or self.controller.current_user.get_role() != UserRole.LIBRARIAN:
            ttk.Label(self, text="Only librarians can manage users",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        user_list_frame = ttk.Frame(notebook)
        add_user_frame = ttk.Frame(notebook)
        user_details_frame = ttk.Frame(notebook)

        from ui.gui.user_modification_frame import UserModificationFrame
        modify_user_frame = UserModificationFrame(notebook, self.controller)

        notebook.add(user_list_frame, text="User List")
        notebook.add(add_user_frame, text="Add User")
        notebook.add(user_details_frame, text="User Details")
        notebook.add(modify_user_frame, text="Modify/Remove")

        self.create_user_list(user_list_frame)
        self.create_add_user_form(add_user_frame)
        self.create_user_details(user_details_frame)

    def create_user_list(self, parent):

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('id', 'name', 'email', 'role', 'active')
        self.user_tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.user_tree.heading('id', text='ID')
        self.user_tree.heading('name', text='Name')
        self.user_tree.heading('email', text='Email')
        self.user_tree.heading('role', text='Role')
        self.user_tree.heading('active', text='Active')

        self.user_tree.column('id', width=250)
        self.user_tree.column('name', width=150)
        self.user_tree.column('email', width=200)
        self.user_tree.column('role', width=100)
        self.user_tree.column('active', width=50)

        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.user_tree.xview)
        self.user_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.user_tree.pack(fill=tk.BOTH, expand=True)

        self.user_tree.bind("<Double-1>", self.on_user_selected)

        self.populate_user_list()

        refresh_button = ttk.Button(frame, text="Refresh", command=self.populate_user_list)
        refresh_button.pack(pady=10)

    def populate_user_list(self):

        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        for user in self.controller.catalog._users.values():
            self.user_tree.insert('', tk.END, values=(
                user.user_id,
                user.name,
                user.email,
                user.get_role().name,
                "Yes" if user.active else "No"
            ))

    def on_user_selected(self, event):

        selection = self.user_tree.selection()
        if not selection:
            return

        user_id = self.user_tree.item(selection[0], 'values')[0]

        self.update_user_details(user_id)

        parent_widget = self.nametowidget(self.winfo_parent())
        if hasattr(parent_widget, 'select'):
            parent_widget.select(2)

    def create_add_user_form(self, parent):

        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text="User Type:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.user_type_var = tk.StringVar(value="guest")
        user_types = [("Librarian", "librarian"), ("Scholar", "scholar"), ("Guest", "guest")]

        for i, (text, value) in enumerate(user_types):
            ttk.Radiobutton(form_frame, text=text, variable=self.user_type_var, value=value).grid(
                row=0, column=i+1, padx=5, pady=5)

        common_fields = [
            ("Name:", "name"),
            ("Email:", "email"),
            ("Password:", "password")
        ]

        self.user_vars = {}

        for i, (label, var_name) in enumerate(common_fields):
            ttk.Label(form_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i+1, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars[var_name] = tk.StringVar()

            if var_name == "password":
                ttk.Entry(form_frame, textvariable=self.user_vars[var_name], width=30, show="*").grid(
                    row=i+1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
            else:
                ttk.Entry(form_frame, textvariable=self.user_vars[var_name], width=30).grid(
                    row=i+1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)

        self.type_specific_frame = ttk.LabelFrame(form_frame, text="Type-Specific Information")
        self.type_specific_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=10)

        self.create_type_specific_fields()

        add_button = ttk.Button(form_frame, text="Add User", command=self.add_user)
        add_button.grid(row=5, column=0, columnspan=4, pady=20)

        self.user_type_var.trace_add("write", lambda *args: self.create_type_specific_fields())

    def create_type_specific_fields(self):

        for widget in self.type_specific_frame.winfo_children():
            widget.destroy()

        user_type = self.user_type_var.get()

        if user_type == "librarian":
            ttk.Label(self.type_specific_frame, text="Department:", font=('Helvetica', 10, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["department"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.user_vars["department"], width=30).grid(
                row=0, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.type_specific_frame, text="Staff ID:", font=('Helvetica', 10, 'bold')).grid(
                row=1, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["staff_id"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.user_vars["staff_id"], width=30).grid(
                row=1, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.type_specific_frame, text="Admin Level (1-3):", font=('Helvetica', 10, 'bold')).grid(
                row=2, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["admin_level"] = tk.StringVar(value="1")
            ttk.Spinbox(self.type_specific_frame, from_=1, to=3, textvariable=self.user_vars["admin_level"],
                       width=5).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        elif user_type == "scholar":
            ttk.Label(self.type_specific_frame, text="Institution:", font=('Helvetica', 10, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["institution"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.user_vars["institution"], width=30).grid(
                row=0, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.type_specific_frame, text="Field of Study:", font=('Helvetica', 10, 'bold')).grid(
                row=1, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["field_of_study"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.user_vars["field_of_study"], width=30).grid(
                row=1, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.type_specific_frame, text="Academic Level:", font=('Helvetica', 10, 'bold')).grid(
                row=2, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["academic_level"] = tk.StringVar(value="General")
            academic_levels = ["General", "Graduate", "Professor", "Distinguished"]
            ttk.Combobox(self.type_specific_frame, textvariable=self.user_vars["academic_level"],
                        values=academic_levels, width=15).grid(
                row=2, column=1, sticky=tk.W, padx=5, pady=5)

        elif user_type == "guest":
            ttk.Label(self.type_specific_frame, text="Address:", font=('Helvetica', 10, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["address"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.user_vars["address"], width=30).grid(
                row=0, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.type_specific_frame, text="Phone:", font=('Helvetica', 10, 'bold')).grid(
                row=1, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["phone"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.user_vars["phone"], width=30).grid(
                row=1, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.type_specific_frame, text="Membership Type:", font=('Helvetica', 10, 'bold')).grid(
                row=2, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["membership_type"] = tk.StringVar(value="Standard")
            membership_types = ["Standard", "Premium"]
            ttk.Combobox(self.type_specific_frame, textvariable=self.user_vars["membership_type"],
                        values=membership_types, width=15).grid(
                row=2, column=1, sticky=tk.W, padx=5, pady=5)

            ttk.Label(self.type_specific_frame, text="Membership Duration (days):", font=('Helvetica', 10, 'bold')).grid(
                row=3, column=0, sticky=tk.W, padx=5, pady=5)

            self.user_vars["membership_duration"] = tk.StringVar(value="365")
            ttk.Spinbox(self.type_specific_frame, from_=30, to=730, textvariable=self.user_vars["membership_duration"],
                       width=5).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

    def add_user(self):

        required_fields = ["name", "email", "password"]
        for field in required_fields:
            if not self.user_vars[field].get().strip():
                messagebox.showerror("Error", f"{field.capitalize()} is required")
                return

        email = self.user_vars["email"].get()
        if '@' not in email:
            messagebox.showerror("Error", "Invalid email format")
            return

        user_type = self.user_type_var.get()
        kwargs = {
            "name": self.user_vars["name"].get(),
            "email": self.user_vars["email"].get(),
            "password": self.user_vars["password"].get()
        }

        if user_type == "librarian":
            kwargs["department"] = self.user_vars["department"].get() or None
            kwargs["staff_id"] = self.user_vars["staff_id"].get() or None

            try:
                kwargs["admin_level"] = int(self.user_vars["admin_level"].get())
            except ValueError:
                messagebox.showerror("Error", "Admin level must be a number")
                return

        elif user_type == "scholar":
            kwargs["institution"] = self.user_vars["institution"].get() or None
            kwargs["field_of_study"] = self.user_vars["field_of_study"].get() or None
            kwargs["academic_level"] = self.user_vars["academic_level"].get()

        elif user_type == "guest":
            kwargs["address"] = self.user_vars["address"].get() or None
            kwargs["phone"] = self.user_vars["phone"].get() or None
            kwargs["membership_type"] = self.user_vars["membership_type"].get()

            try:
                duration = int(self.user_vars["membership_duration"].get())
                kwargs["membership_expiry"] = datetime.now() + timedelta(days=duration)
            except ValueError:
                messagebox.showerror("Error", "Membership duration must be a number")
                return

        try:
            user = UserFactory.create_user(user_type, **kwargs)

            self.controller.catalog.add_user(user)

            self.controller.event_manager.user_registered(user)

            messagebox.showinfo("Success", f"User '{user.name}' added successfully")

            for var_name in self.user_vars:
                if var_name not in ["admin_level", "membership_type", "academic_level", "membership_duration"]:
                    self.user_vars[var_name].set("")

            self.populate_user_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_user_details(self, parent):

        self.details_frame = ttk.Frame(parent)
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(self.details_frame, text="Select a user from the User List tab to view details",
                 font=('Helvetica', 12, 'italic')).pack(pady=50)

    def update_user_details(self, user_id):

        for widget in self.details_frame.winfo_children():
            widget.destroy()

        user = self.controller.catalog.get_user(user_id)

        if not user:
            ttk.Label(self.details_frame, text=f"User not found: {user_id}",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        ttk.Label(self.details_frame, text=user.name, font=('Helvetica', 16, 'bold')).pack(
            anchor=tk.W, padx=5, pady=(0, 10))

        details_frame = ttk.Frame(self.details_frame)
        details_frame.pack(fill=tk.X, padx=5, pady=5)

        details = [
            ("Email:", user.email),
            ("Role:", user.get_role().name),
            ("Registration Date:", user.registration_date.strftime('%Y-%m-%d')),
            ("Last Login:", user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else "Never"),
            ("Active:", "Yes" if user.active else "No")
        ]

        if user.get_role() == UserRole.LIBRARIAN:
            details.extend([
                ("Department:", user.department or "N/A"),
                ("Staff ID:", user.staff_id or "N/A"),
                ("Admin Level:", str(user.admin_level))
            ])
        elif user.get_role() == UserRole.SCHOLAR:
            details.extend([
                ("Institution:", user.institution or "N/A"),
                ("Field of Study:", user.field_of_study or "N/A"),
                ("Academic Level:", user.academic_level)
            ])
            if user.research_topics:
                details.append(("Research Topics:", ", ".join(user.research_topics)))
        elif user.get_role() == UserRole.GUEST:
            details.extend([
                ("Address:", user.address or "N/A"),
                ("Phone:", user.phone or "N/A"),
                ("Membership Type:", user.membership_type),
                ("Membership Expiry:", user.membership_expiry.strftime('%Y-%m-%d') if user.membership_expiry else "N/A"),
                ("Membership Valid:", "Yes" if user.is_membership_valid() else "No")
            ])

        for i, (label, value) in enumerate(details):
            ttk.Label(details_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(details_frame, text=value, font=('Helvetica', 10)).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2)

        borrowed_books = self.controller.library.get_user_borrowed_books(user_id)

        if borrowed_books:
            books_frame = ttk.LabelFrame(self.details_frame, text="Borrowed Books")
            books_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

            columns = ('title', 'author', 'due_date', 'status')
            tree = ttk.Treeview(books_frame, columns=columns, show='headings')

            tree.heading('title', text='Title')
            tree.heading('author', text='Author')
            tree.heading('due_date', text='Due Date')
            tree.heading('status', text='Status')

            tree.column('title', width=200)
            tree.column('author', width=150)
            tree.column('due_date', width=100)
            tree.column('status', width=80)

            scrollbar = ttk.Scrollbar(books_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            for item in borrowed_books:
                book = item['book']
                due_date = item['due_date']
                status = "Overdue" if due_date < datetime.now() else "On Time"

                tree.insert('', tk.END, values=(
                    book.title,
                    book.author,
                    due_date.strftime('%Y-%m-%d'),
                    status
                ))
        else:
            ttk.Label(self.details_frame, text="No borrowed books",
                     font=('Helvetica', 10, 'italic')).pack(padx=5, pady=10)

        button_frame = ttk.Frame(self.details_frame)
        button_frame.pack(pady=10)

        toggle_button = ttk.Button(button_frame,
                                  text="Deactivate User" if user.active else "Activate User",
                                  command=lambda: self.toggle_user_active(user_id))
        toggle_button.pack(side=tk.LEFT, padx=5)

    def toggle_user_active(self, user_id):

        user = self.controller.catalog.get_user(user_id)

        if not user:
            messagebox.showerror("Error", f"User not found: {user_id}")
            return

        user.active = not user.active

        self.controller.catalog.update_user(user)

        status = "activated" if user.active else "deactivated"
        messagebox.showinfo("Success", f"User '{user.name}' {status} successfully")

        self.update_user_details(user_id)

        self.populate_user_list()

    def update_frame(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.create_user_management()
