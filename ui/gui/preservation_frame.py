import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from models.book import BookCondition
from services.preservation import PreservationService, PreservationAction, PreservationRecord

class PreservationFrame(ttk.Frame):


    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.preservation_service = PreservationService(controller.catalog, controller.event_manager)

        self.create_preservation_management()

    def create_preservation_management(self):


        title_label = ttk.Label(self, text="Preservation Management", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        if not self.controller.current_user or self.controller.current_user.get_role().name != 'LIBRARIAN':
            ttk.Label(self, text="Only librarians can access preservation management",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        schedule_frame = ttk.Frame(notebook)
        history_frame = ttk.Frame(notebook)
        recommendations_frame = ttk.Frame(notebook)
        due_actions_frame = ttk.Frame(notebook)

        notebook.add(schedule_frame, text="Schedule Preservation")
        notebook.add(history_frame, text="Preservation History")
        notebook.add(recommendations_frame, text="Recommendations")
        notebook.add(due_actions_frame, text="Due Actions")

        self.create_schedule_tab(schedule_frame)
        self.create_history_tab(history_frame)
        self.create_recommendations_tab(recommendations_frame)
        self.create_due_actions_tab(due_actions_frame)

    def create_schedule_tab(self, parent):


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Book:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.book_var = tk.StringVar()
        book_combo = ttk.Combobox(frame, textvariable=self.book_var, width=50)
        book_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        books = list(self.controller.catalog._books.values())
        book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

        ttk.Label(frame, text="Preservation Action:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.action_var = tk.StringVar()
        actions = [action.name for action in PreservationAction]
        action_combo = ttk.Combobox(frame, textvariable=self.action_var, values=actions, width=30)
        action_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Interval (days):", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.interval_var = tk.StringVar(value="90")
        interval_entry = ttk.Spinbox(frame, from_=1, to=365, textvariable=self.interval_var, width=10)
        interval_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Start After (days):", font=('Helvetica', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)

        self.start_after_var = tk.StringVar(value="0")
        start_after_entry = ttk.Spinbox(frame, from_=0, to=365, textvariable=self.start_after_var, width=10)
        start_after_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Notes:", font=('Helvetica', 10, 'bold')).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=5)

        self.notes_var = tk.StringVar()
        notes_entry = ttk.Entry(frame, textvariable=self.notes_var, width=50)
        notes_entry.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        schedule_button = ttk.Button(frame, text="Schedule Preservation",
                                   command=self.schedule_preservation,
                                   style='Primary.TButton')
        schedule_button.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Separator(frame, orient='horizontal').grid(
            row=6, column=0, columnspan=3, sticky=tk.EW, pady=20)

        ttk.Label(frame, text="Perform Immediate Action", font=('Helvetica', 12, 'bold')).grid(
            row=7, column=0, columnspan=3, sticky=tk.W, padx=5, pady=10)

        add_action_button = ttk.Button(frame, text="Perform Action Now",
                                     command=self.add_preservation_record,
                                     style='Primary.TButton')
        add_action_button.grid(row=8, column=0, columnspan=3, pady=10)

    def create_history_tab(self, parent):


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Book:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=5)

        self.history_book_var = tk.StringVar()
        history_book_combo = ttk.Combobox(frame, textvariable=self.history_book_var, width=50)
        history_book_combo.pack(fill=tk.X, padx=5, pady=5)

        books = list(self.controller.catalog._books.values())
        history_book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

        view_button = ttk.Button(frame, text="View History",
                               command=self.view_preservation_history,
                               style='Primary.TButton')
        view_button.pack(pady=10)

        columns = ('date', 'action', 'performed_by', 'notes', 'condition_before', 'condition_after')
        self.history_tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.history_tree.heading('date', text='Date')
        self.history_tree.heading('action', text='Action')
        self.history_tree.heading('performed_by', text='Performed By')
        self.history_tree.heading('notes', text='Notes')
        self.history_tree.heading('condition_before', text='Condition Before')
        self.history_tree.heading('condition_after', text='Condition After')

        self.history_tree.column('date', width=150)
        self.history_tree.column('action', width=150)
        self.history_tree.column('performed_by', width=150)
        self.history_tree.column('notes', width=200)
        self.history_tree.column('condition_before', width=120)
        self.history_tree.column('condition_after', width=120)

        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.history_tree.pack(fill=tk.BOTH, expand=True, pady=10)

    def create_recommendations_tab(self, parent):


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Book:", font=('Helvetica', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=5)

        self.recommend_book_var = tk.StringVar()
        recommend_book_combo = ttk.Combobox(frame, textvariable=self.recommend_book_var, width=50)
        recommend_book_combo.pack(fill=tk.X, padx=5, pady=5)

        books = list(self.controller.catalog._books.values())
        recommend_book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

        recommend_button = ttk.Button(frame, text="Get Recommendations",
                                    command=self.get_preservation_recommendations,
                                    style='Primary.TButton')
        recommend_button.pack(pady=10)

        self.recommendations_frame = ttk.LabelFrame(frame, text="Recommended Actions")
        self.recommendations_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(self.recommendations_frame, text="Select a book to view recommendations",
                 font=('Helvetica', 10, 'italic')).pack(pady=20)

    def create_due_actions_tab(self, parent):


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text="Preservation Actions Due",
                 font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)

        refresh_button = ttk.Button(header_frame, text="Refresh Due Actions",
                                  command=self.refresh_due_actions,
                                  style='Primary.TButton')
        refresh_button.pack(side=tk.RIGHT)

        columns = ('book', 'action', 'last_performed', 'next_due', 'days_overdue', 'interval', 'book_condition')
        self.due_actions_tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.due_actions_tree.heading('book', text='Book')
        self.due_actions_tree.heading('action', text='Action')
        self.due_actions_tree.heading('last_performed', text='Last Performed')
        self.due_actions_tree.heading('next_due', text='Next Due')
        self.due_actions_tree.heading('days_overdue', text='Days Overdue')
        self.due_actions_tree.heading('interval', text='Interval (days)')
        self.due_actions_tree.heading('book_condition', text='Book Condition')

        self.due_actions_tree.column('book', width=250)
        self.due_actions_tree.column('action', width=150)
        self.due_actions_tree.column('last_performed', width=150)
        self.due_actions_tree.column('next_due', width=150)
        self.due_actions_tree.column('days_overdue', width=100)
        self.due_actions_tree.column('interval', width=100)
        self.due_actions_tree.column('book_condition', width=120)

        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.due_actions_tree.yview)
        self.due_actions_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.due_actions_tree.xview)
        self.due_actions_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.due_actions_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        perform_button = ttk.Button(buttons_frame, text="Perform Selected Action",
                                  command=self.perform_due_action,
                                  style='Primary.TButton')
        perform_button.pack(side=tk.LEFT, padx=5)

        view_book_button = ttk.Button(buttons_frame, text="View Book Details",
                                    command=self.view_book_from_due_action)
        view_book_button.pack(side=tk.LEFT, padx=5)

        self.refresh_due_actions()

    def schedule_preservation(self):


        book_selection = self.book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        action_name = self.action_var.get()
        if not action_name:
            messagebox.showerror("Error", "Please select an action")
            return

        try:
            action = PreservationAction[action_name]
        except KeyError:
            messagebox.showerror("Error", "Invalid action")
            return

        try:
            interval = int(self.interval_var.get())
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid interval: {str(e)}")
            return

        try:
            start_after = int(self.start_after_var.get())
            if start_after < 0:
                raise ValueError("Start after must be non-negative")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid start after: {str(e)}")
            return

        try:
            schedule = self.preservation_service.schedule_preservation(
                book_id, action, interval, start_after)

            messagebox.showinfo("Success",
                              f"Preservation action {action.name} scheduled for book {book_id}\n"
                              f"Interval: {interval} days\n"
                              f"First action due: {schedule.next_due_date().strftime('%Y-%m-%d')}")

            self.book_var.set("")
            self.action_var.set("")
            self.interval_var.set("90")
            self.start_after_var.set("0")
            self.notes_var.set("")

            self.refresh_due_actions()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_preservation_record(self):


        book_selection = self.book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        action_name = self.action_var.get()
        if not action_name:
            messagebox.showerror("Error", "Please select an action")
            return

        try:
            action = PreservationAction[action_name]
        except KeyError:
            messagebox.showerror("Error", "Invalid action")
            return

        notes = self.notes_var.get()

        try:
            record = self.preservation_service.add_preservation_record(
                book_id, action, self.controller.current_user.user_id, notes)

            messagebox.showinfo("Success",
                              f"Preservation action {action.name} performed for book {book_id}")

            self.book_var.set("")
            self.action_var.set("")
            self.notes_var.set("")

            book = self.controller.catalog.get_book(book_id)
            if action in [PreservationAction.RESTORATION, PreservationAction.REPAIR]:
                conditions = list(BookCondition)
                current_index = conditions.index(book.condition)
                if current_index > 0:
                    book.condition = conditions[current_index - 1]
                    self.controller.catalog.update_book(book)
                    messagebox.showinfo("Book Condition",
                                      f"Book condition improved to {book.condition.name}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_preservation_history(self):


        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        book_selection = self.history_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        history = self.preservation_service.get_book_preservation_history(book_id)

        if not history:
            messagebox.showinfo("No History", "No preservation history found for this book")
            return

        for record in history:
            performed_by = "Unknown"
            if record.performed_by:
                user = self.controller.catalog.get_user(record.performed_by)
                if user:
                    performed_by = user.name

            self.history_tree.insert('', tk.END, values=(
                record.timestamp.strftime('%Y-%m-%d %H:%M'),
                record.action.name,
                performed_by,
                record.notes or "",
                record.before_condition.name if record.before_condition else "Unknown",
                record.after_condition.name if record.after_condition else "Unknown"
            ))

    def get_preservation_recommendations(self):


        for widget in self.recommendations_frame.winfo_children():
            widget.destroy()

        book_selection = self.recommend_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        recommendations = self.preservation_service.recommend_preservation_actions(book_id)

        if not recommendations:
            ttk.Label(self.recommendations_frame,
                     text="No recommendations available for this book",
                     font=('Helvetica', 10, 'italic')).pack(pady=20)
            return

        ttk.Label(self.recommendations_frame,
                 text=f"Recommendations for: {book.title}",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(self.recommendations_frame,
                 text=f"Current condition: {book.condition.name}",
                 font=('Helvetica', 10)).pack(anchor=tk.W, pady=(0, 10))

        for i, recommendation in enumerate(recommendations):
            action = recommendation['action']
            reason = recommendation['reason']
            priority = recommendation['priority']

            rec_frame = ttk.Frame(self.recommendations_frame)
            rec_frame.pack(fill=tk.X, pady=5)

            priority_color = "#00b894"
            if priority == "MEDIUM":
                priority_color = "#fdcb6e"
            elif priority == "HIGH":
                priority_color = "#e17055"

            priority_indicator = tk.Label(rec_frame, text="   ", bg=priority_color)
            priority_indicator.pack(side=tk.LEFT, padx=(0, 10))

            ttk.Label(rec_frame,
                     text=f"{i+1}. {action.name}",
                     font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))

            ttk.Label(rec_frame,
                     text=f"Priority: {priority}",
                     font=('Helvetica', 10)).pack(side=tk.LEFT, padx=(0, 10))

            perform_button = ttk.Button(rec_frame, text="Perform",
                                      command=lambda b=book_id, a=action: self.perform_recommended_action(b, a))
            perform_button.pack(side=tk.RIGHT, padx=5)

            reason_frame = ttk.Frame(self.recommendations_frame)
            reason_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(reason_frame, text="Reason:",
                     font=('Helvetica', 10, 'italic')).pack(side=tk.LEFT, padx=(25, 5))

            ttk.Label(reason_frame, text=reason).pack(side=tk.LEFT)

    def perform_recommended_action(self, book_id, action):


        if messagebox.askyesno("Confirm Action",
                             f"Perform {action.name} on book {book_id}?"):
            try:
                record = self.preservation_service.add_preservation_record(
                    book_id, action, self.controller.current_user.user_id,
                    f"Performed from recommendation")

                messagebox.showinfo("Success",
                                  f"Preservation action {action.name} performed for book {book_id}")

                book = self.controller.catalog.get_book(book_id)
                if action in [PreservationAction.RESTORATION, PreservationAction.REPAIR]:
                    conditions = list(BookCondition)
                    current_index = conditions.index(book.condition)
                    if current_index > 0:
                        book.condition = conditions[current_index - 1]
                        self.controller.catalog.update_book(book)
                        messagebox.showinfo("Book Condition",
                                          f"Book condition improved to {book.condition.name}")

                self.get_preservation_recommendations()

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def refresh_due_actions(self):


        for item in self.due_actions_tree.get_children():
            self.due_actions_tree.delete(item)

        due_actions = self.preservation_service.get_due_preservation_actions()

        if not due_actions:
            return

        for schedule in due_actions:
            book = self.controller.catalog.get_book(schedule.book_id)
            if not book:
                continue

            book_title = f"{book.title} ({book.book_id})"

            last_performed = "Never"
            if schedule.last_performed:
                last_performed = schedule.last_performed.strftime('%Y-%m-%d')

            next_due = schedule.next_due.strftime('%Y-%m-%d')

            days_overdue = schedule.days_overdue()

            interval = schedule.interval_days

            book_condition = book.condition.name

            tag = 'normal'
            if days_overdue > 30:
                tag = 'critical'
            elif days_overdue > 14:
                tag = 'high'
            elif days_overdue > 0:
                tag = 'medium'

            self.due_actions_tree.insert('', tk.END, values=(
                book_title,
                schedule.action.name,
                last_performed,
                next_due,
                days_overdue,
                interval,
                book_condition
            ), tags=(tag,))

        self.due_actions_tree.tag_configure('normal', background='white')
        self.due_actions_tree.tag_configure('medium', background='#fffacd')  # Light yellow
        self.due_actions_tree.tag_configure('high', background='#ffd700')    # Gold
        self.due_actions_tree.tag_configure('critical', background='#ff6347') # Tomato

    def perform_due_action(self):


        selection = self.due_actions_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select an action to perform")
            return

        values = self.due_actions_tree.item(selection[0], 'values')
        book_title = values[0]
        action_name = values[1]

        book_id = None
        for book in self.controller.catalog._books.values():
            if book.title == book_title:
                book_id = book.book_id
                break

        if not book_id:
            messagebox.showerror("Error", "Book not found")
            return

        try:
            action = PreservationAction[action_name]
        except KeyError:
            messagebox.showerror("Error", "Invalid action")
            return

        if messagebox.askyesno("Confirm Action",
                             f"Perform {action_name} on book '{book_title}'?"):
            try:
                record = self.preservation_service.add_preservation_record(
                    book_id, action, self.controller.current_user.user_id,
                    f"Performed from due actions")

                for schedule in self.preservation_service._preservation_schedules:
                    if schedule.book_id == book_id and schedule.action == action:
                        schedule.last_performed = datetime.now()
                        break

                messagebox.showinfo("Success",
                                  f"Preservation action {action_name} performed for book '{book_title}'")

                book = self.controller.catalog.get_book(book_id)
                if action in [PreservationAction.RESTORATION, PreservationAction.REPAIR]:
                    conditions = list(BookCondition)
                    current_index = conditions.index(book.condition)
                    if current_index > 0:
                        book.condition = conditions[current_index - 1]
                        self.controller.catalog.update_book(book)
                        messagebox.showinfo("Book Condition",
                                          f"Book condition improved to {book.condition.name}")

                self.refresh_due_actions()

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def view_book_from_due_action(self):

        selection = self.due_actions_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a book to view")
            return

        values = self.due_actions_tree.item(selection[0], 'values')
        book_title = values[0]

        book_id = book_title.split('(')[-1].split(')')[0]

        if not book_id:
            messagebox.showerror("Error", "Could not extract book ID")
            return

        self.controller.show_book_details(book_id)

    def update_frame(self):


        if hasattr(self, 'due_actions_tree'):
            self.refresh_due_actions()
