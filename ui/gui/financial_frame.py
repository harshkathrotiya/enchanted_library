import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import uuid

from models.book import BookCondition
from models.lending import LendingStatus
from services.fee_calculator import FeeCalculator

class FinancialFrame(ttk.Frame):
    

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.fee_calculator = FeeCalculator()

        self.create_financial_management()

    def create_financial_management(self):
        

        title_label = ttk.Label(self, text="Financial Management", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        if not self.controller.current_user or self.controller.current_user.get_role().name != 'LIBRARIAN':
            ttk.Label(self, text="Only librarians can access financial management",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        fees_frame = ttk.Frame(notebook)
        membership_frame = ttk.Frame(notebook)
        reports_frame = ttk.Frame(notebook)

        notebook.add(fees_frame, text="Late & Damage Fees")
        notebook.add(membership_frame, text="Membership Fees")
        notebook.add(reports_frame, text="Financial Reports")

        self.create_fees_tab(fees_frame)
        self.create_membership_tab(membership_frame)
        self.create_reports_tab(reports_frame)

    def create_fees_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Overdue Books & Late Fees",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        columns = ('record_id', 'book_title', 'user_name', 'due_date', 'days_overdue', 'late_fee')
        self.overdue_tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.overdue_tree.heading('record_id', text='Record ID')
        self.overdue_tree.heading('book_title', text='Book Title')
        self.overdue_tree.heading('user_name', text='Borrower')
        self.overdue_tree.heading('due_date', text='Due Date')
        self.overdue_tree.heading('days_overdue', text='Days Overdue')
        self.overdue_tree.heading('late_fee', text='Late Fee')

        self.overdue_tree.column('record_id', width=250)
        self.overdue_tree.column('book_title', width=200)
        self.overdue_tree.column('user_name', width=150)
        self.overdue_tree.column('due_date', width=100)
        self.overdue_tree.column('days_overdue', width=100)
        self.overdue_tree.column('late_fee', width=100)

        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.overdue_tree.yview)
        self.overdue_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.overdue_tree.xview)
        self.overdue_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.overdue_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        refresh_button = ttk.Button(button_frame, text="Refresh",
                                  command=self.populate_overdue_list,
                                  style='Primary.TButton')
        refresh_button.pack(side=tk.LEFT, padx=5)

        send_reminder_button = ttk.Button(button_frame, text="Send Reminder",
                                        command=self.send_fee_reminder)
        send_reminder_button.pack(side=tk.LEFT, padx=5)

        waive_fee_button = ttk.Button(button_frame, text="Waive Fee",
                                    command=self.waive_late_fee)
        waive_fee_button.pack(side=tk.LEFT, padx=5)

        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)

        ttk.Label(frame, text="Calculate Damage Fee",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        damage_frame = ttk.Frame(frame)
        damage_frame.pack(fill=tk.X, pady=10)

        ttk.Label(damage_frame, text="Original Condition:",
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.original_condition_var = tk.StringVar()
        conditions = [condition.name for condition in BookCondition]
        original_combo = ttk.Combobox(damage_frame, textvariable=self.original_condition_var,
                                    values=conditions, width=15)
        original_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(damage_frame, text="New Condition:",
                 font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.new_condition_var = tk.StringVar()
        new_combo = ttk.Combobox(damage_frame, textvariable=self.new_condition_var,
                               values=conditions, width=15)
        new_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        calculate_button = ttk.Button(damage_frame, text="Calculate Fee",
                                    command=self.calculate_damage_fee,
                                    style='Primary.TButton')
        calculate_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.damage_fee_result = ttk.Label(damage_frame, text="", font=('Helvetica', 12))
        self.damage_fee_result.grid(row=3, column=0, columnspan=2, pady=5)

        self.populate_overdue_list()

    def create_membership_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Membership Fee Calculator",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        calc_frame = ttk.Frame(frame)
        calc_frame.pack(fill=tk.X, pady=10)

        ttk.Label(calc_frame, text="Membership Type:",
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.membership_type_var = tk.StringVar(value="Standard")
        membership_types = ["Standard", "Premium"]
        membership_combo = ttk.Combobox(calc_frame, textvariable=self.membership_type_var,
                                      values=membership_types, width=15)
        membership_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(calc_frame, text="Duration (months):",
                 font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.duration_var = tk.StringVar(value="12")
        duration_entry = ttk.Spinbox(calc_frame, from_=1, to=36, textvariable=self.duration_var, width=10)
        duration_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(calc_frame, text="Season (for discounts):",
                 font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.season_var = tk.StringVar()
        seasons = ["Spring", "Summer", "Fall", "Winter", "Library Week"]
        season_combo = ttk.Combobox(calc_frame, textvariable=self.season_var,
                                  values=seasons, width=15)
        season_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        calculate_button = ttk.Button(calc_frame, text="Calculate Fee",
                                    command=self.calculate_membership_fee,
                                    style='Primary.TButton')
        calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.membership_fee_result = ttk.Label(calc_frame, text="", font=('Helvetica', 12))
        self.membership_fee_result.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)

        ttk.Label(frame, text="Renew User Membership",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        renew_frame = ttk.Frame(frame)
        renew_frame.pack(fill=tk.X, pady=10)

        ttk.Label(renew_frame, text="Select User:",
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.renew_user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(renew_frame, textvariable=self.renew_user_var, width=40)
        self.user_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        self.update_user_combo()

        ttk.Label(renew_frame, text="Extend by (months):",
                 font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.extend_duration_var = tk.StringVar(value="12")
        extend_duration_entry = ttk.Spinbox(renew_frame, from_=1, to=36,
                                          textvariable=self.extend_duration_var, width=10)
        extend_duration_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        renew_button = ttk.Button(renew_frame, text="Renew Membership",
                                command=self.renew_membership,
                                style='Primary.TButton')
        renew_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_reports_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Generate Financial Report",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        report_frame = ttk.Frame(frame)
        report_frame.pack(fill=tk.X, pady=10)

        ttk.Label(report_frame, text="Report Type:",
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.report_type_var = tk.StringVar(value="Late Fees")
        report_types = ["Late Fees", "Damage Fees", "Membership Fees", "All Fees"]
        report_combo = ttk.Combobox(report_frame, textvariable=self.report_type_var,
                                  values=report_types, width=20)
        report_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(report_frame, text="Date Range:",
                 font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        range_frame = ttk.Frame(report_frame)
        range_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        self.date_range_var = tk.StringVar(value="Last 30 Days")
        date_ranges = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"]
        range_combo = ttk.Combobox(range_frame, textvariable=self.date_range_var,
                                 values=date_ranges, width=15)
        range_combo.pack(side=tk.LEFT)

        generate_button = ttk.Button(report_frame, text="Generate Report",
                                   command=self.generate_financial_report,
                                   style='Primary.TButton')
        generate_button.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Report Results",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(20, 10))

        report_display_frame = ttk.Frame(frame)
        report_display_frame.pack(fill=tk.BOTH, expand=True)

        self.report_text = tk.Text(report_display_frame, wrap=tk.WORD, height=20, width=80)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        report_scrollbar = ttk.Scrollbar(report_display_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        export_button = ttk.Button(frame, text="Export Report",
                                 command=self.export_report)
        export_button.pack(anchor=tk.E, pady=10)

    def populate_overdue_list(self):
        

        for item in self.overdue_tree.get_children():
            self.overdue_tree.delete(item)

        overdue_books = self.controller.library.get_overdue_books()

        if not overdue_books:
            messagebox.showinfo("No Overdue Books", "There are no overdue books at this time")
            return

        for item in overdue_books:
            record = item['record']
            book = item['book']
            user = item['user']
            days_overdue = item['days_overdue']
            late_fee = item['late_fee']

            self.overdue_tree.insert('', tk.END, values=(
                record.record_id,
                book.title,
                user.name,
                record.due_date.strftime('%Y-%m-%d'),
                days_overdue,
                f"${late_fee:.2f}"
            ))

    def send_fee_reminder(self):
        

        selection = self.overdue_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an overdue book")
            return

        record_id = self.overdue_tree.item(selection[0], 'values')[0]

        record = None
        for r in self.controller.catalog._lending_records.values():
            if r.record_id == record_id:
                record = r
                break

        if not record:
            messagebox.showerror("Error", "Record not found")
            return

        book = self.controller.catalog.get_book(record.book_id)
        user = self.controller.catalog.get_user(record.user_id)

        if not book or not user:
            messagebox.showerror("Error", "Book or user not found")
            return

        days_overdue = record.days_overdue()
        late_fee = book.get_late_fee(days_overdue)

        from patterns.behavioral.notification_observer import NotificationService
        notification_service = NotificationService()

        subject = "Library Late Fee Reminder"
        message = (f"Dear {user.name},\n\n"
                  f"This is a reminder that the book '{book.title}' is overdue by {days_overdue} days.\n"
                  f"The current late fee is ${late_fee:.2f}.\n\n"
                  f"Please return the book as soon as possible to avoid additional fees.\n\n"
                  f"Thank you,\nEnchanted Library")

        notification_service.send_notification(user.email, subject, message)

        messagebox.showinfo("Reminder Sent", f"Late fee reminder sent to {user.name} ({user.email})")

    def waive_late_fee(self):
        

        selection = self.overdue_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an overdue book")
            return

        record_id = self.overdue_tree.item(selection[0], 'values')[0]

        record = None
        for r in self.controller.catalog._lending_records.values():
            if r.record_id == record_id:
                record = r
                break

        if not record:
            messagebox.showerror("Error", "Record not found")
            return

        book = self.controller.catalog.get_book(record.book_id)
        user = self.controller.catalog.get_user(record.user_id)

        if not book or not user:
            messagebox.showerror("Error", "Book or user not found")
            return

        if not messagebox.askyesno("Confirm Waive",
                                 f"Are you sure you want to waive the late fee for '{book.title}' "
                                 f"borrowed by {user.name}?"):
            return

        record.late_fee = 0.0
        self.controller.catalog.update_lending_record(record)

        messagebox.showinfo("Fee Waived", f"Late fee for '{book.title}' has been waived")

        self.populate_overdue_list()

    def calculate_damage_fee(self):
        

        original_condition_name = self.original_condition_var.get()
        new_condition_name = self.new_condition_var.get()

        if not original_condition_name or not new_condition_name:
            messagebox.showerror("Error", "Please select both original and new conditions")
            return

        try:
            original_condition = BookCondition[original_condition_name]
            new_condition = BookCondition[new_condition_name]
        except KeyError:
            messagebox.showerror("Error", "Invalid condition")
            return

        fee = self.fee_calculator.calculate_damage_fee(original_condition, new_condition)

        if fee > 0:
            self.damage_fee_result.configure(
                text=f"Damage Fee: ${fee:.2f}",
                foreground="#e17055"
            )
        else:
            self.damage_fee_result.configure(
                text="No damage fee applicable",
                foreground="#00b894"
            )

    def calculate_membership_fee(self):
        

        membership_type = self.membership_type_var.get()

        try:
            duration = int(self.duration_var.get())
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid duration: {str(e)}")
            return

        season = self.season_var.get() or None

        base_fee = self.fee_calculator.calculate_membership_fee(membership_type, duration)

        if season:
            discounted_fee = self.fee_calculator.calculate_seasonal_discount(base_fee, season)
            discount = base_fee - discounted_fee
            discount_percentage = (discount / base_fee) * 100

            self.membership_fee_result.configure(
                text=f"Base Fee: ${base_fee:.2f}\n"
                     f"{season} Discount: ${discount:.2f} ({discount_percentage:.1f}%)\n"
                     f"Final Fee: ${discounted_fee:.2f}"
            )
        else:
            self.membership_fee_result.configure(
                text=f"Membership Fee: ${base_fee:.2f}"
            )

    def update_user_combo(self):
        

        guest_users = []
        for user in self.controller.catalog._users.values():
            if user.get_role().name == 'GUEST':
                guest_users.append(user)

        self.user_combo['values'] = [
            f"{user.name} ({user.email}) - Expires: {user.membership_expiry.strftime('%Y-%m-%d') if user.membership_expiry else 'N/A'}"
            for user in guest_users
        ]

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
            duration = int(self.extend_duration_var.get())
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid duration: {str(e)}")
            return

        if user.membership_expiry and user.membership_expiry > datetime.now():
            new_expiry = user.membership_expiry + timedelta(days=30*duration)
        else:
            new_expiry = datetime.now() + timedelta(days=30*duration)

        user.membership_expiry = new_expiry
        self.controller.catalog.update_user(user)

        messagebox.showinfo("Membership Renewed",
                          f"Membership for {user.name} renewed successfully\n"
                          f"New expiry date: {new_expiry.strftime('%Y-%m-%d')}")

        self.update_user_combo()

    def generate_financial_report(self):
        

        self.report_text.delete(1.0, tk.END)

        report_type = self.report_type_var.get()
        date_range = self.date_range_var.get()

        end_date = datetime.now()
        if date_range == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif date_range == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        elif date_range == "Last Year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime(1900, 1, 1)

        report = f"Financial Report: {report_type}\n"
        report += f"Date Range: {date_range} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 80 + "\n\n"

        if report_type in ["Late Fees", "All Fees"]:
            report += self.generate_late_fees_report(start_date, end_date)

        if report_type in ["Damage Fees", "All Fees"]:
            report += self.generate_damage_fees_report(start_date, end_date)

        if report_type in ["Membership Fees", "All Fees"]:
            report += self.generate_membership_fees_report(start_date, end_date)

        self.report_text.insert(tk.END, report)

    def generate_late_fees_report(self, start_date, end_date):
        

        report = "LATE FEES\n"
        report += "-" * 80 + "\n"

        late_fee_records = []
        total_late_fees = 0.0

        for record in self.controller.catalog._lending_records.values():
            if (record.status == LendingStatus.RETURNED and
                record.return_date and
                start_date <= record.return_date <= end_date and
                record.late_fee > 0):

                book = self.controller.catalog.get_book(record.book_id)
                user = self.controller.catalog.get_user(record.user_id)

                if book and user:
                    late_fee_records.append({
                        'record': record,
                        'book': book,
                        'user': user,
                        'late_fee': record.late_fee
                    })
                    total_late_fees += record.late_fee

        if not late_fee_records:
            report += "No late fees collected in this period.\n\n"
        else:
            report += f"Total Late Fees: ${total_late_fees:.2f}\n"
            report += f"Number of Overdue Returns: {len(late_fee_records)}\n"
            report += f"Average Late Fee: ${(total_late_fees / len(late_fee_records)):.2f}\n\n"

            report += "Details:\n"
            for item in late_fee_records:
                record = item['record']
                book = item['book']
                user = item['user']
                late_fee = item['late_fee']

                report += f"- {book.title} (borrowed by {user.name})\n"
                report += f"  Due: {record.due_date.strftime('%Y-%m-%d')}, "
                report += f"Returned: {record.return_date.strftime('%Y-%m-%d')}, "
                report += f"Days Overdue: {(record.return_date - record.due_date).days}, "
                report += f"Fee: ${late_fee:.2f}\n"

        report += "\n"
        return report

    def generate_damage_fees_report(self, start_date, end_date):
        

        report = "DAMAGE FEES\n"
        report += "-" * 80 + "\n"

        report += "Damage fee tracking is not implemented in the current system.\n"
        report += "This would require extending the LendingRecord class to track condition changes.\n\n"

        return report

    def generate_membership_fees_report(self, start_date, end_date):
        

        report = "MEMBERSHIP FEES\n"
        report += "-" * 80 + "\n"

        report += "Membership fee tracking is not implemented in the current system.\n"
        report += "This would require adding a payment tracking system.\n\n"

        report += "Sample Calculations:\n"
        report += f"Standard Membership (12 months): ${self.fee_calculator.calculate_membership_fee('Standard', 12):.2f}\n"
        report += f"Premium Membership (12 months): ${self.fee_calculator.calculate_membership_fee('Premium', 12):.2f}\n"

        return report

    def export_report(self):
        

        report_content = self.report_text.get(1.0, tk.END)

        if not report_content.strip():
            messagebox.showerror("Error", "No report to export")
            return

        filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filename, 'w') as f:
                f.write(report_content)

            messagebox.showinfo("Export Successful", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def update_frame(self):
        

        if hasattr(self, 'overdue_tree'):
            self.populate_overdue_list()

        if hasattr(self, 'user_combo'):
            self.update_user_combo()
