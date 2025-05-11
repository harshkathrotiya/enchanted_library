
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from models.book import BookStatus
from services.recommendation import RecommendationService

class SearchFrame(ttk.Frame):

    def __init__(self, parent, controller):

        super().__init__(parent)
        self.controller = controller
        self.recommendation_service = RecommendationService(controller.catalog)

        self.create_search_layout()

    def create_search_layout(self):

        title_label = ttk.Label(self, text="Search & Recommendations", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        basic_search_frame = ttk.Frame(notebook)
        advanced_search_frame = ttk.Frame(notebook)
        recommendations_frame = ttk.Frame(notebook)

        notebook.add(basic_search_frame, text="Basic Search")
        notebook.add(advanced_search_frame, text="Advanced Search")
        notebook.add(recommendations_frame, text="Recommendations")

        self.create_basic_search(basic_search_frame)
        self.create_advanced_search(advanced_search_frame)
        self.create_recommendations(recommendations_frame)

    def create_basic_search(self, parent):

        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(form_frame, text="Search Term:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(form_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        search_button = ttk.Button(form_frame, text="Search", command=self.perform_basic_search)
        search_button.grid(row=0, column=2, padx=5, pady=5)

        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        columns = ('id', 'title', 'author', 'year', 'type', 'status', 'quantity', 'available')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        self.results_tree.heading('id', text='ID')
        self.results_tree.heading('title', text='Title')
        self.results_tree.heading('author', text='Author')
        self.results_tree.heading('year', text='Year')
        self.results_tree.heading('type', text='Type')
        self.results_tree.heading('status', text='Status')
        self.results_tree.heading('quantity', text='Quantity')
        self.results_tree.heading('available', text='Available')

        self.results_tree.column('id', width=250)
        self.results_tree.column('title', width=200)
        self.results_tree.column('author', width=150)
        self.results_tree.column('year', width=50)
        self.results_tree.column('type', width=100)
        self.results_tree.column('status', width=100)
        self.results_tree.column('quantity', width=70)
        self.results_tree.column('available', width=70)

        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(fill=tk.BOTH, expand=True)

        self.results_tree.bind("<Double-1>", self.view_book_details)

    def perform_basic_search(self):

        search_term = self.search_var.get()

        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return

        books = self.controller.catalog.search_books(title=search_term) + self.controller.catalog.search_books(author=search_term)

        unique_books = {}
        for book in books:
            unique_books[book.book_id] = book

        books = list(unique_books.values())

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        if not books:
            messagebox.showinfo("Search Results", f"No books found matching '{search_term}'")
            return

        for book in books:
            from models.book import GeneralBook, RareBook, AncientScript
            if isinstance(book, GeneralBook):
                book_type = "General"
            elif isinstance(book, RareBook):
                book_type = "Rare"
            elif isinstance(book, AncientScript):
                book_type = "Ancient"
            else:
                book_type = "Unknown"

            self.results_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name,
                book.quantity,
                book.available_quantity
            ))

    def create_advanced_search(self, parent):

        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=20, pady=20)

        fields = [
            ("Title:", "title"),
            ("Author:", "author"),
            ("Year:", "year"),
            ("ISBN:", "isbn")
        ]

        self.advanced_search_vars = {}

        for i, (label, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=5)

            self.advanced_search_vars[var_name] = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.advanced_search_vars[var_name], width=30).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(form_frame, text="Book Type:", font=('Helvetica', 10, 'bold')).grid(
            row=len(fields), column=0, sticky=tk.W, padx=5, pady=5)

        self.advanced_search_vars["book_type"] = tk.StringVar(value="any")
        book_types = [("Any", "any"), ("General", "general"), ("Rare", "rare"), ("Ancient", "ancient")]

        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=len(fields), column=1, sticky=tk.W, padx=5, pady=5)

        for i, (text, value) in enumerate(book_types):
            ttk.Radiobutton(type_frame, text=text, variable=self.advanced_search_vars["book_type"],
                           value=value).grid(row=0, column=i, padx=5)

        ttk.Label(form_frame, text="Status:", font=('Helvetica', 10, 'bold')).grid(
            row=len(fields)+1, column=0, sticky=tk.W, padx=5, pady=5)

        self.advanced_search_vars["status"] = tk.StringVar(value="any")
        statuses = [("Any", "any"), ("Available", "AVAILABLE"), ("Borrowed", "BORROWED")]

        status_frame = ttk.Frame(form_frame)
        status_frame.grid(row=len(fields)+1, column=1, sticky=tk.W, padx=5, pady=5)

        for i, (text, value) in enumerate(statuses):
            ttk.Radiobutton(status_frame, text=text, variable=self.advanced_search_vars["status"],
                           value=value).grid(row=0, column=i, padx=5)

        search_button = ttk.Button(form_frame, text="Search", command=self.perform_advanced_search)
        search_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=10)

        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        columns = ('id', 'title', 'author', 'year', 'type', 'status', 'quantity', 'available')
        self.advanced_results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        self.advanced_results_tree.heading('id', text='ID')
        self.advanced_results_tree.heading('title', text='Title')
        self.advanced_results_tree.heading('author', text='Author')
        self.advanced_results_tree.heading('year', text='Year')
        self.advanced_results_tree.heading('type', text='Type')
        self.advanced_results_tree.heading('status', text='Status')
        self.advanced_results_tree.heading('quantity', text='Quantity')
        self.advanced_results_tree.heading('available', text='Available')

        self.advanced_results_tree.column('id', width=250)
        self.advanced_results_tree.column('title', width=200)
        self.advanced_results_tree.column('author', width=150)
        self.advanced_results_tree.column('year', width=50)
        self.advanced_results_tree.column('type', width=100)
        self.advanced_results_tree.column('status', width=100)
        self.advanced_results_tree.column('quantity', width=70)
        self.advanced_results_tree.column('available', width=70)

        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.advanced_results_tree.yview)
        self.advanced_results_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.advanced_results_tree.xview)
        self.advanced_results_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.advanced_results_tree.pack(fill=tk.BOTH, expand=True)

        self.advanced_results_tree.bind("<Double-1>", self.view_book_details_advanced)

    def perform_advanced_search(self):

        criteria = {}

        for field in ["title", "author", "isbn"]:
            if self.advanced_search_vars[field].get():
                criteria[field] = self.advanced_search_vars[field].get()

        if self.advanced_search_vars["year"].get():
            try:
                criteria["year"] = int(self.advanced_search_vars["year"].get())
            except ValueError:
                messagebox.showerror("Error", "Year must be a number")
                return

        books = list(self.controller.catalog._books.values())

        for key, value in criteria.items():
            if key == "title":
                books = [book for book in books if value.lower() in book.title.lower()]
            elif key == "author":
                books = [book for book in books if value.lower() in book.author.lower()]
            elif key == "year":
                books = [book for book in books if book.year_published == value]
            elif key == "isbn":
                books = [book for book in books if book.isbn and value.lower() in book.isbn.lower()]

        book_type = self.advanced_search_vars["book_type"].get()
        if book_type != "any":
            from models.book import GeneralBook, RareBook, AncientScript
            if book_type == "general":
                books = [book for book in books if isinstance(book, GeneralBook)]
            elif book_type == "rare":
                books = [book for book in books if isinstance(book, RareBook)]
            elif book_type == "ancient":
                books = [book for book in books if isinstance(book, AncientScript)]

        status = self.advanced_search_vars["status"].get()
        if status != "any":
            books = [book for book in books if book.status.name == status]

        for item in self.advanced_results_tree.get_children():
            self.advanced_results_tree.delete(item)

        if not books:
            messagebox.showinfo("Search Results", "No books found matching your criteria")
            return

        for book in books:
            from models.book import GeneralBook, RareBook, AncientScript
            if isinstance(book, GeneralBook):
                book_type = "General"
            elif isinstance(book, RareBook):
                book_type = "Rare"
            elif isinstance(book, AncientScript):
                book_type = "Ancient"
            else:
                book_type = "Unknown"

            self.advanced_results_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name,
                book.quantity,
                book.available_quantity
            ))

    def create_recommendations(self, parent):

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if not self.controller.current_user:
            ttk.Label(frame, text="Please log in to view recommendations",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        ttk.Label(frame, text="Recommended Books", font=('Helvetica', 12, 'bold')).pack(
            anchor=tk.W, pady=(0, 10))

        books = self.recommendation_service.get_recommendations(
            self.controller.current_user.user_id)

        if not books:
            ttk.Label(frame, text="No recommendations available. Try borrowing some books first!",
                     font=('Helvetica', 10, 'italic')).pack(pady=20)
            return

        recommendations = []
        for book in books:
            from models.book import GeneralBook, RareBook, AncientScript
            if isinstance(book, GeneralBook):
                reason = "Popular general book"
                if hasattr(book, 'genre') and book.genre:
                    reason = f"Matches your interest in {book.genre} books"
            elif isinstance(book, RareBook):
                reason = f"Rare book (rarity level: {book.rarity_level}/10)"
            elif isinstance(book, AncientScript):
                reason = f"Ancient script from {book.origin}" if hasattr(book, 'origin') and book.origin else "Ancient script"
            else:
                reason = "Recommended based on your reading history"

            recommendations.append({
                'book': book,
                'reason': reason
            })

        columns = ('id', 'title', 'author', 'year', 'type', 'status', 'quantity', 'available', 'reason')
        self.recommendations_tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.recommendations_tree.heading('id', text='ID')
        self.recommendations_tree.heading('title', text='Title')
        self.recommendations_tree.heading('author', text='Author')
        self.recommendations_tree.heading('year', text='Year')
        self.recommendations_tree.heading('type', text='Type')
        self.recommendations_tree.heading('status', text='Status')
        self.recommendations_tree.heading('quantity', text='Quantity')
        self.recommendations_tree.heading('available', text='Available')
        self.recommendations_tree.heading('reason', text='Recommendation Reason')

        self.recommendations_tree.column('id', width=250)
        self.recommendations_tree.column('title', width=200)
        self.recommendations_tree.column('author', width=150)
        self.recommendations_tree.column('year', width=50)
        self.recommendations_tree.column('type', width=100)
        self.recommendations_tree.column('status', width=100)
        self.recommendations_tree.column('quantity', width=70)
        self.recommendations_tree.column('available', width=70)
        self.recommendations_tree.column('reason', width=200)

        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.recommendations_tree.yview)
        self.recommendations_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.recommendations_tree.xview)
        self.recommendations_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.recommendations_tree.pack(fill=tk.BOTH, expand=True)

        for recommendation in recommendations:
            book = recommendation['book']
            reason = recommendation['reason']

            from models.book import GeneralBook, RareBook, AncientScript
            if isinstance(book, GeneralBook):
                book_type = "General"
            elif isinstance(book, RareBook):
                book_type = "Rare"
            elif isinstance(book, AncientScript):
                book_type = "Ancient"
            else:
                book_type = "Unknown"

            self.recommendations_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name,
                book.quantity,
                book.available_quantity,
                reason
            ))

        self.recommendations_tree.bind("<Double-1>", self.view_book_details_recommendations)

        refresh_button = ttk.Button(frame, text="Refresh Recommendations",
                                   command=lambda: self.update_frame())
        refresh_button.pack(pady=10)

    def view_book_details(self, event):

        selection = self.results_tree.selection()
        if not selection:
            return

        book_id = self.results_tree.item(selection[0], 'values')[0]

        self.show_book_details(book_id)

    def view_book_details_advanced(self, event):

        selection = self.advanced_results_tree.selection()
        if not selection:
            return

        book_id = self.advanced_results_tree.item(selection[0], 'values')[0]

        self.show_book_details(book_id)

    def view_book_details_recommendations(self, event):

        selection = self.recommendations_tree.selection()
        if not selection:
            return

        book_id = self.recommendations_tree.item(selection[0], 'values')[0]

        self.show_book_details(book_id)

    def show_book_details(self, book_id):

        book = self.controller.catalog.get_book(book_id)

        if not book:
            messagebox.showerror("Error", f"Book not found: {book_id}")
            return

        details_window = tk.Toplevel(self)
        details_window.title(f"Book Details: {book.title}")
        details_window.geometry("600x500")
        details_window.minsize(500, 400)

        canvas = tk.Canvas(details_window)
        scrollbar = ttk.Scrollbar(details_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(scrollable_frame, text=book.title, font=('Helvetica', 16, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(10, 5))

        details = [
            ("Author:", book.author),
            ("Year Published:", str(book.year_published)),
            ("ISBN:", book.isbn or "N/A"),
            ("Condition:", book.condition.name),
            ("Status:", book.status.name),
            ("Location:", book.location or "N/A"),
            ("Total Quantity:", str(book.quantity)),
            ("Available Copies:", str(book.available_quantity)),
            ("Acquisition Date:", book._acquisition_date.strftime('%Y-%m-%d')),
            ("Last Maintenance:", book._last_maintenance.strftime('%Y-%m-%d'))
        ]

        preservation_schedules = self.controller.preservation_service.get_book_preservation_schedules(book.book_id)
        if preservation_schedules:
            next_actions = []
            for schedule in preservation_schedules:
                next_actions.append(f"{schedule.action.name}: {schedule.next_due.strftime('%Y-%m-%d')}")
            details.append(("Next Preservation:", ", ".join(next_actions)))

        from models.book import GeneralBook, RareBook, AncientScript

        if isinstance(book, GeneralBook):
            details.append(("Type:", "General Book"))
            details.append(("Genre:", book.genre or "N/A"))
            details.append(("Is Bestseller:", "Yes" if book.is_bestseller else "No"))
        elif isinstance(book, RareBook):
            details.append(("Type:", "Rare Book"))
            details.append(("Estimated Value:", f"${book.estimated_value or 'N/A'}"))
            details.append(("Rarity Level:", f"{book.rarity_level}/10"))
            details.append(("Requires Gloves:", "Yes" if book.requires_gloves else "No"))
            if book.special_handling_notes:
                details.append(("Handling Notes:", book.special_handling_notes))
        elif isinstance(book, AncientScript):
            details.append(("Type:", "Ancient Script"))
            details.append(("Origin:", book.origin or "N/A"))
            details.append(("Language:", book.language or "N/A"))
            details.append(("Translation:", "Available" if book.translation_available else "Not Available"))
            details.append(("Digital Copy:", "Available" if book.digital_copy_available else "Not Available"))
            if book.preservation_requirements:
                details.append(("Preservation Requirements:", ", ".join(book.preservation_requirements)))

        for i, (label, value) in enumerate(details):
            ttk.Label(scrollable_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i+1, column=0, sticky=tk.W, padx=10, pady=2)
            ttk.Label(scrollable_frame, text=value, font=('Helvetica', 10)).grid(
                row=i+1, column=1, sticky=tk.W, padx=10, pady=2)

        availability = self.controller.library.get_book_availability(book_id)
        ttk.Label(scrollable_frame, text="Availability:", font=('Helvetica', 10, 'bold')).grid(
            row=len(details)+1, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        ttk.Label(scrollable_frame, text=availability['message'], font=('Helvetica', 10)).grid(
            row=len(details)+1, column=1, sticky=tk.W, padx=10, pady=(10, 2))

        if book.status == BookStatus.BORROWED:
            lending_records = self.controller.catalog.get_book_lending_records(book_id)
            active_records = [r for r in lending_records if r.status.name == 'ACTIVE']

            if active_records:
                record = active_records[0]
                user = self.controller.catalog.get_user(record.user_id)

                ttk.Label(scrollable_frame, text="Currently borrowed by:", font=('Helvetica', 10, 'bold')).grid(
                    row=len(details)+2, column=0, sticky=tk.W, padx=10, pady=2)
                ttk.Label(scrollable_frame, text=user.name if user else "Unknown", font=('Helvetica', 10)).grid(
                    row=len(details)+2, column=1, sticky=tk.W, padx=10, pady=2)

                ttk.Label(scrollable_frame, text="Due date:", font=('Helvetica', 10, 'bold')).grid(
                    row=len(details)+3, column=0, sticky=tk.W, padx=10, pady=2)
                ttk.Label(scrollable_frame, text=record.due_date.strftime('%Y-%m-%d'), font=('Helvetica', 10)).grid(
                    row=len(details)+3, column=1, sticky=tk.W, padx=10, pady=2)

        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(details)+4, column=0, columnspan=2, pady=20)

        if book.available_quantity > 0 and self.controller.current_user:
            checkout_button = ttk.Button(button_frame, text="Checkout Book",
                                       command=lambda: self.checkout_book(book_id, details_window))
            checkout_button.pack(side=tk.LEFT, padx=5)

        close_button = ttk.Button(button_frame, text="Close", command=details_window.destroy)
        close_button.pack(side=tk.LEFT, padx=5)

    def checkout_book(self, book_id, details_window):

        if not self.controller.current_user:
            messagebox.showerror("Error", "Please log in first")
            return

        from patterns.behavioral.action_command import CheckoutBookCommand, CommandInvoker
        command_invoker = CommandInvoker()
        command = CheckoutBookCommand(self.controller.catalog, book_id, self.controller.current_user.user_id)
        result = command_invoker.execute_command(command)

        if result['success']:
            messagebox.showinfo("Success",
                              f"{result['message']}\nDue date: {result['due_date'].strftime('%Y-%m-%d')}")

            book = self.controller.catalog.get_book(book_id)
            self.controller.event_manager.book_borrowed(book, self.controller.current_user)

            details_window.destroy()

            self.update_frame()
        else:
            messagebox.showerror("Error", result['message'])

    def update_frame(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.create_search_layout()
