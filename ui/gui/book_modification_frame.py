import tkinter as tk
from tkinter import ttk, messagebox
import uuid

from models.book import BookStatus, BookCondition, GeneralBook, RareBook, AncientScript

class BookModificationFrame(ttk.Frame):


    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.create_book_modification_ui()

    def create_book_modification_ui(self):


        title_label = ttk.Label(self, text="Book Modification", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        if not self.controller.current_user or self.controller.current_user.get_role().name != 'LIBRARIAN':
            ttk.Label(self, text="Only librarians can modify books",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        update_frame = ttk.Frame(notebook)
        remove_frame = ttk.Frame(notebook)
        condition_frame = ttk.Frame(notebook)

        notebook.add(update_frame, text="Update Book")
        notebook.add(remove_frame, text="Remove Book")
        notebook.add(condition_frame, text="Update Condition")

        self.create_update_tab(update_frame)
        self.create_remove_tab(remove_frame)
        self.create_condition_tab(condition_frame)

    def create_update_tab(self, parent):


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Book:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.update_book_var = tk.StringVar()
        self.book_combo = ttk.Combobox(frame, textvariable=self.update_book_var, width=50)
        self.book_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.update_book_combo()

        load_button = ttk.Button(frame, text="Load Book",
                               command=self.load_book_for_update)
        load_button.grid(row=0, column=3, padx=5, pady=5)

        details_frame = ttk.LabelFrame(frame, text="Book Details")
        details_frame.grid(row=1, column=0, columnspan=4, sticky=tk.NSEW, padx=5, pady=10)

        ttk.Label(details_frame, text="Title:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.title_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.title_var, width=40).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="Author:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.author_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.author_var, width=40).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="Year Published:", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.year_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.year_var, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="ISBN:", font=('Helvetica', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)

        self.isbn_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.isbn_var, width=20).grid(
            row=3, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="Description:", font=('Helvetica', 10, 'bold')).grid(
            row=4, column=0, sticky=tk.NW, padx=5, pady=5)

        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(details_frame, textvariable=self.description_var, width=50)
        description_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(details_frame, text="Quantity:", font=('Helvetica', 10, 'bold')).grid(
            row=5, column=0, sticky=tk.W, padx=5, pady=5)

        self.quantity_var = tk.StringVar()
        ttk.Spinbox(details_frame, from_=1, to=100, textvariable=self.quantity_var, width=10).grid(
            row=5, column=1, sticky=tk.W, padx=5, pady=5)

        self.type_fields_frame = ttk.LabelFrame(frame, text="Type-Specific Details")
        self.type_fields_frame.grid(row=2, column=0, columnspan=4, sticky=tk.NSEW, padx=5, pady=10)

        self.book_id_var = tk.StringVar()

        self.book_type_var = tk.StringVar()

        update_button = ttk.Button(frame, text="Update Book",
                                 command=self.update_book,
                                 style='Primary.TButton')
        update_button.grid(row=3, column=0, columnspan=4, pady=20)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

    def create_remove_tab(self, parent):


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Book to Remove:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.remove_book_var = tk.StringVar()
        remove_book_combo = ttk.Combobox(frame, textvariable=self.remove_book_var, width=50)
        remove_book_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        books = list(self.controller.catalog._books.values())
        remove_book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

        details_frame = ttk.LabelFrame(frame, text="Book Details")
        details_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=10)

        self.remove_details_text = tk.Text(details_frame, wrap=tk.WORD, height=10, width=60)
        self.remove_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.remove_details_text.config(state=tk.DISABLED)

        load_button = ttk.Button(frame, text="Load Book Details",
                               command=self.load_book_for_removal)
        load_button.grid(row=2, column=0, columnspan=2, pady=10)

        remove_button = ttk.Button(frame, text="Remove Book",
                                 command=self.remove_book,
                                 style='Error.TButton')
        remove_button.grid(row=3, column=0, columnspan=2, pady=10)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

    def create_condition_tab(self, parent):


        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Book:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.condition_book_var = tk.StringVar()
        condition_book_combo = ttk.Combobox(frame, textvariable=self.condition_book_var, width=50)
        condition_book_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        books = list(self.controller.catalog._books.values())
        condition_book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

        load_button = ttk.Button(frame, text="Load Book",
                               command=self.load_book_for_condition)
        load_button.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Current Condition:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.current_condition_var = tk.StringVar()
        current_condition_label = ttk.Label(frame, textvariable=self.current_condition_var,
                                          font=('Helvetica', 10))
        current_condition_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="New Condition:", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.new_condition_var = tk.StringVar()
        conditions = [condition.name for condition in BookCondition]
        new_condition_combo = ttk.Combobox(frame, textvariable=self.new_condition_var,
                                         values=conditions, width=15)
        new_condition_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Notes:", font=('Helvetica', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)

        self.condition_notes_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.condition_notes_var, width=50).grid(
            row=3, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        update_button = ttk.Button(frame, text="Update Condition",
                                 command=self.update_book_condition,
                                 style='Primary.TButton')
        update_button.grid(row=4, column=0, columnspan=3, pady=20)

        frame.columnconfigure(1, weight=1)

    def update_book_combo(self):


        books = list(self.controller.catalog._books.values())

        self.book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

    def load_book_for_update(self):


        book_selection = self.update_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        self.book_id_var.set(book.book_id)
        self.title_var.set(book.title)
        self.author_var.set(book.author)
        self.year_var.set(str(book.year_published))
        self.isbn_var.set(book.isbn if hasattr(book, 'isbn') and book.isbn else "")
        self.description_var.set(book.description if hasattr(book, 'description') and book.description else "")
        self.quantity_var.set(str(book.quantity))

        for widget in self.type_fields_frame.winfo_children():
            widget.destroy()

        if isinstance(book, GeneralBook):
            self.book_type_var.set("general")
            self.add_general_book_fields(book)
        elif isinstance(book, RareBook):
            self.book_type_var.set("rare")
            self.add_rare_book_fields(book)
        elif isinstance(book, AncientScript):
            self.book_type_var.set("ancient")
            self.add_ancient_script_fields(book)

    def add_general_book_fields(self, book=None):


        ttk.Label(self.type_fields_frame, text="Genre:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.genre_var = tk.StringVar()
        if book and hasattr(book, 'genre'):
            self.genre_var.set(book.genre)

        ttk.Entry(self.type_fields_frame, textvariable=self.genre_var, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(self.type_fields_frame, text="Publisher:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.publisher_var = tk.StringVar()
        if book and hasattr(book, 'publisher'):
            self.publisher_var.set(book.publisher)

        ttk.Entry(self.type_fields_frame, textvariable=self.publisher_var, width=30).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

    def add_rare_book_fields(self, book=None):


        ttk.Label(self.type_fields_frame, text="Origin:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.origin_var = tk.StringVar()
        if book and hasattr(book, 'origin'):
            self.origin_var.set(book.origin)

        ttk.Entry(self.type_fields_frame, textvariable=self.origin_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(self.type_fields_frame, text="Estimated Value ($):", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.value_var = tk.StringVar()
        if book and hasattr(book, 'estimated_value'):
            self.value_var.set(str(book.estimated_value))

        ttk.Entry(self.type_fields_frame, textvariable=self.value_var, width=15).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

    def add_ancient_script_fields(self, book=None):


        ttk.Label(self.type_fields_frame, text="Language:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.language_var = tk.StringVar()
        if book and hasattr(book, 'language'):
            self.language_var.set(book.language)

        ttk.Entry(self.type_fields_frame, textvariable=self.language_var, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(self.type_fields_frame, text="Period:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.period_var = tk.StringVar()
        if book and hasattr(book, 'period'):
            self.period_var.set(book.period)

        ttk.Entry(self.type_fields_frame, textvariable=self.period_var, width=20).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(self.type_fields_frame, text="Preservation Requirements:", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.preservation_var = tk.StringVar()
        if book and hasattr(book, 'preservation_requirements'):
            self.preservation_var.set(book.preservation_requirements)

        ttk.Entry(self.type_fields_frame, textvariable=self.preservation_var, width=40).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5)

    def update_book(self):


        book_id = self.book_id_var.get()
        if not book_id:
            messagebox.showerror("Error", "No book selected")
            return

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        title = self.title_var.get()
        author = self.author_var.get()

        try:
            year_published = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Error", "Year must be a number")
            return

        isbn = self.isbn_var.get()
        description = self.description_var.get()

        if not title or not author:
            messagebox.showerror("Error", "Title and author are required")
            return

        book.title = title
        book.author = author
        book.year_published = year_published

        if hasattr(book, 'isbn'):
            book.isbn = isbn

        if hasattr(book, 'description'):
            book.description = description

        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be a positive number")
                return
            book.quantity = quantity
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return

        book_type = self.book_type_var.get()

        if book_type == "general":
            if hasattr(book, 'genre'):
                book.genre = self.genre_var.get()

            if hasattr(book, 'publisher'):
                book.publisher = self.publisher_var.get()

        elif book_type == "rare":
            if hasattr(book, 'origin'):
                book.origin = self.origin_var.get()

            if hasattr(book, 'estimated_value'):
                try:
                    book.estimated_value = float(self.value_var.get()) if self.value_var.get() else 0.0
                except ValueError:
                    messagebox.showerror("Error", "Estimated value must be a number")
                    return

        elif book_type == "ancient":
            if hasattr(book, 'language'):
                book.language = self.language_var.get()

            if hasattr(book, 'period'):
                book.period = self.period_var.get()

            if hasattr(book, 'preservation_requirements'):
                book.preservation_requirements = self.preservation_var.get()

        self.controller.catalog.update_book(book)

        messagebox.showinfo("Success", f"Book '{title}' updated successfully")

        self.update_book_var.set("")
        self.book_id_var.set("")
        self.title_var.set("")
        self.author_var.set("")
        self.year_var.set("")
        self.isbn_var.set("")
        self.description_var.set("")
        self.quantity_var.set("")
        self.book_type_var.set("")

        for widget in self.type_fields_frame.winfo_children():
            widget.destroy()

        self.update_book_combo()

    def load_book_for_removal(self):


        book_selection = self.remove_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        self.remove_details_text.config(state=tk.NORMAL)

        self.remove_details_text.delete(1.0, tk.END)

        details = f"Title: {book.title}\n"
        details += f"Author: {book.author}\n"
        details += f"Year: {book.year_published}\n"
        details += f"ID: {book.book_id}\n"
        details += f"Status: {book.status.name}\n"
        details += f"Condition: {book.condition.name}\n"
        details += f"Total Quantity: {book.quantity}\n"
        details += f"Available Copies: {book.available_quantity}\n"
        details += f"Acquisition Date: {book._acquisition_date.strftime('%Y-%m-%d')}\n"
        details += f"Last Maintenance: {book._last_maintenance.strftime('%Y-%m-%d')}\n"

        if isinstance(book, GeneralBook):
            details += f"Type: General Book\n"
            if hasattr(book, 'genre') and book.genre:
                details += f"Genre: {book.genre}\n"
            if hasattr(book, 'publisher') and book.publisher:
                details += f"Publisher: {book.publisher}\n"

        elif isinstance(book, RareBook):
            details += f"Type: Rare Book\n"
            if hasattr(book, 'origin') and book.origin:
                details += f"Origin: {book.origin}\n"
            if hasattr(book, 'estimated_value'):
                details += f"Estimated Value: ${book.estimated_value:.2f}\n"

        elif isinstance(book, AncientScript):
            details += f"Type: Ancient Script\n"
            if hasattr(book, 'language') and book.language:
                details += f"Language: {book.language}\n"
            if hasattr(book, 'period') and book.period:
                details += f"Period: {book.period}\n"

        if book.status == BookStatus.BORROWED:
            details += "\nWARNING: This book is currently borrowed and cannot be removed."

        self.remove_details_text.insert(tk.END, details)

        self.remove_details_text.config(state=tk.DISABLED)

    def remove_book(self):


        book_selection = self.remove_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        if book.status == BookStatus.BORROWED:
            messagebox.showerror("Error", "Cannot remove a borrowed book")
            return

        if not messagebox.askyesno("Confirm Removal",
                                 f"Are you sure you want to remove '{book.title}'?\n\n"
                                 f"This action cannot be undone."):
            return

        self.controller.catalog.remove_book(book_id)

        messagebox.showinfo("Success", f"Book '{book.title}' removed successfully")

        self.remove_book_var.set("")

        self.remove_details_text.config(state=tk.NORMAL)
        self.remove_details_text.delete(1.0, tk.END)
        self.remove_details_text.config(state=tk.DISABLED)

        self.update_book_combo()

    def load_book_for_condition(self):


        book_selection = self.condition_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        self.current_condition_var.set(book.condition.name)

        self.new_condition_var.set(book.condition.name)

    def update_book_condition(self):


        book_selection = self.condition_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        new_condition_name = self.new_condition_var.get()
        if not new_condition_name:
            messagebox.showerror("Error", "Please select a new condition")
            return

        try:
            new_condition = BookCondition[new_condition_name]
        except KeyError:
            messagebox.showerror("Error", "Invalid condition")
            return

        if book.condition == new_condition:
            messagebox.showinfo("No Change", "The condition is the same")
            return

        notes = self.condition_notes_var.get()

        original_condition = book.condition
        book.condition = new_condition
        self.controller.catalog.update_book(book)

        if hasattr(self.controller, 'preservation_service'):
            from services.preservation import PreservationAction
            action = PreservationAction.CONDITION_ASSESSMENT

            self.controller.preservation_service.add_preservation_record(
                book_id,
                action,
                self.controller.current_user.user_id if self.controller.current_user else None,
                f"Condition changed from {original_condition.name} to {new_condition.name}. Notes: {notes}"
            )

        messagebox.showinfo("Success",
                          f"Book condition updated from {original_condition.name} to {new_condition.name}")

        self.current_condition_var.set(new_condition.name)

        self.condition_notes_var.set("")

    def update_frame(self):


        self.update_book_combo()