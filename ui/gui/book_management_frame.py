"""
Book management frame for the Enchanted Library GUI.
This module provides the interface for managing books.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from datetime import datetime

from models.book import BookCondition, BookStatus
from patterns.creational.book_factory import BookFactory
from patterns.behavioral.action_command import AddBookCommand, CommandInvoker


class BookManagementFrame(ttk.Frame):
    """Frame for managing books."""
    
    def __init__(self, parent, controller):
        """
        Initialize the book management frame.
        
        Args:
            parent: The parent widget
            controller: The main application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.command_invoker = CommandInvoker()
        
        # Create the book management layout
        self.create_book_management()
    
    def create_book_management(self):
        """Create the book management layout."""
        # Title
        title_label = ttk.Label(self, text="Book Management", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create a notebook for different book operations
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        book_list_frame = ttk.Frame(notebook)
        add_book_frame = ttk.Frame(notebook)
        book_details_frame = ttk.Frame(notebook)
        
        notebook.add(book_list_frame, text="Book List")
        notebook.add(add_book_frame, text="Add Book")
        notebook.add(book_details_frame, text="Book Details")
        
        # Create the content for each tab
        self.create_book_list(book_list_frame)
        self.create_add_book_form(add_book_frame)
        self.create_book_details(book_details_frame)
    
    def create_book_list(self, parent):
        """
        Create the book list tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the book list
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a treeview to display the books
        columns = ('id', 'title', 'author', 'year', 'type', 'status')
        self.book_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define the columns
        self.book_tree.heading('id', text='ID')
        self.book_tree.heading('title', text='Title')
        self.book_tree.heading('author', text='Author')
        self.book_tree.heading('year', text='Year')
        self.book_tree.heading('type', text='Type')
        self.book_tree.heading('status', text='Status')
        
        # Set column widths
        self.book_tree.column('id', width=250)
        self.book_tree.column('title', width=200)
        self.book_tree.column('author', width=150)
        self.book_tree.column('year', width=50)
        self.book_tree.column('type', width=100)
        self.book_tree.column('status', width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.book_tree.xview)
        self.book_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.book_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event to view book details
        self.book_tree.bind("<Double-1>", self.on_book_selected)
        
        # Add books to the treeview
        self.populate_book_list()
        
        # Add a refresh button
        refresh_button = ttk.Button(frame, text="Refresh", command=self.populate_book_list)
        refresh_button.pack(pady=10)
    
    def populate_book_list(self):
        """Populate the book list with data from the catalog."""
        # Clear the treeview
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        
        # Add books to the treeview
        for book in self.controller.catalog._books.values():
            # Determine book type
            from models.book import GeneralBook, RareBook, AncientScript
            if isinstance(book, GeneralBook):
                book_type = "General"
            elif isinstance(book, RareBook):
                book_type = "Rare"
            elif isinstance(book, AncientScript):
                book_type = "Ancient"
            else:
                book_type = "Unknown"
            
            self.book_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name
            ))
    
    def on_book_selected(self, event):
        """
        Handle book selection event.
        
        Args:
            event: The event object
        """
        # Get the selected item
        selection = self.book_tree.selection()
        if not selection:
            return
        
        # Get the book ID
        book_id = self.book_tree.item(selection[0], 'values')[0]
        
        # Update the book details tab
        self.update_book_details(book_id)
        
        # Switch to the book details tab
        notebook = self.nametowidget(self.winfo_parent())
        notebook.select(2)  # Select the book details tab (index 2)
    
    def create_add_book_form(self, parent):
        """
        Create the add book form.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the form
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Check if user has permission to add books
        if not self.controller.current_user or self.controller.current_user.get_role().name != 'LIBRARIAN':
            ttk.Label(form_frame, text="Only librarians can add books", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Book type selection
        ttk.Label(form_frame, text="Book Type:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.book_type_var = tk.StringVar(value="general")
        book_types = [("General Book", "general"), ("Rare Book", "rare"), ("Ancient Script", "ancient")]
        
        for i, (text, value) in enumerate(book_types):
            ttk.Radiobutton(form_frame, text=text, variable=self.book_type_var, value=value).grid(
                row=0, column=i+1, padx=5, pady=5)
        
        # Common book information
        common_fields = [
            ("Title:", "title"),
            ("Author:", "author"),
            ("Year Published:", "year"),
            ("ISBN (optional):", "isbn")
        ]
        
        self.book_vars = {}
        
        for i, (label, var_name) in enumerate(common_fields):
            ttk.Label(form_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i+1, column=0, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars[var_name] = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.book_vars[var_name], width=30).grid(
                row=i+1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Type-specific fields
        self.type_specific_frame = ttk.LabelFrame(form_frame, text="Type-Specific Information")
        self.type_specific_frame.grid(row=5, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=10)
        
        # Create the type-specific fields
        self.create_type_specific_fields()
        
        # Add book button
        add_button = ttk.Button(form_frame, text="Add Book", command=self.add_book)
        add_button.grid(row=6, column=0, columnspan=4, pady=20)
        
        # Bind the book type change event
        self.book_type_var.trace_add("write", lambda *args: self.create_type_specific_fields())
    
    def create_type_specific_fields(self):
        """Create the type-specific fields based on the selected book type."""
        # Clear the frame
        for widget in self.type_specific_frame.winfo_children():
            widget.destroy()
        
        book_type = self.book_type_var.get()
        
        if book_type == "general":
            # Fields for general books
            ttk.Label(self.type_specific_frame, text="Genre:", font=('Helvetica', 10, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["genre"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.book_vars["genre"], width=30).grid(
                row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["is_bestseller"] = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.type_specific_frame, text="Is Bestseller", 
                           variable=self.book_vars["is_bestseller"]).grid(
                row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
            
        elif book_type == "rare":
            # Fields for rare books
            ttk.Label(self.type_specific_frame, text="Estimated Value ($):", font=('Helvetica', 10, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["estimated_value"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.book_vars["estimated_value"], width=15).grid(
                row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(self.type_specific_frame, text="Rarity Level (1-10):", font=('Helvetica', 10, 'bold')).grid(
                row=1, column=0, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["rarity_level"] = tk.StringVar(value="5")
            ttk.Spinbox(self.type_specific_frame, from_=1, to=10, textvariable=self.book_vars["rarity_level"], 
                       width=5).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(self.type_specific_frame, text="Special Handling Notes:", font=('Helvetica', 10, 'bold')).grid(
                row=2, column=0, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["special_handling_notes"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.book_vars["special_handling_notes"], width=30).grid(
                row=2, column=1, sticky=tk.W, padx=5, pady=5)
            
        elif book_type == "ancient":
            # Fields for ancient scripts
            ttk.Label(self.type_specific_frame, text="Origin:", font=('Helvetica', 10, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["origin"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.book_vars["origin"], width=30).grid(
                row=0, column=1, sticky=tk.W, padx=5, pady=5)
            
            ttk.Label(self.type_specific_frame, text="Language:", font=('Helvetica', 10, 'bold')).grid(
                row=1, column=0, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["language"] = tk.StringVar()
            ttk.Entry(self.type_specific_frame, textvariable=self.book_vars["language"], width=30).grid(
                row=1, column=1, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["translation_available"] = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.type_specific_frame, text="Translation Available", 
                           variable=self.book_vars["translation_available"]).grid(
                row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
            
            self.book_vars["digital_copy_available"] = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.type_specific_frame, text="Digital Copy Available", 
                           variable=self.book_vars["digital_copy_available"]).grid(
                row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
    
    def add_book(self):
        """Add a new book to the catalog."""
        # Validate required fields
        required_fields = ["title", "author", "year"]
        for field in required_fields:
            if not self.book_vars[field].get().strip():
                messagebox.showerror("Error", f"{field.capitalize()} is required")
                return
        
        # Validate year
        try:
            year = int(self.book_vars["year"].get())
        except ValueError:
            messagebox.showerror("Error", "Year must be a number")
            return
        
        # Get book type and common parameters
        book_type = self.book_type_var.get()
        kwargs = {
            "title": self.book_vars["title"].get(),
            "author": self.book_vars["author"].get(),
            "year_published": year,
            "isbn": self.book_vars["isbn"].get() or None
        }
        
        # Add type-specific parameters
        if book_type == "general":
            kwargs["genre"] = self.book_vars["genre"].get() or None
            kwargs["is_bestseller"] = self.book_vars["is_bestseller"].get()
        elif book_type == "rare":
            try:
                kwargs["estimated_value"] = float(self.book_vars["estimated_value"].get()) if self.book_vars["estimated_value"].get() else None
            except ValueError:
                messagebox.showerror("Error", "Estimated value must be a number")
                return
            
            try:
                kwargs["rarity_level"] = int(self.book_vars["rarity_level"].get())
            except ValueError:
                messagebox.showerror("Error", "Rarity level must be a number")
                return
            
            kwargs["special_handling_notes"] = self.book_vars["special_handling_notes"].get() or None
        elif book_type == "ancient":
            kwargs["origin"] = self.book_vars["origin"].get() or None
            kwargs["language"] = self.book_vars["language"].get() or None
            kwargs["translation_available"] = self.book_vars["translation_available"].get()
            kwargs["digital_copy_available"] = self.book_vars["digital_copy_available"].get()
        
        # Create the book using the factory
        try:
            book = BookFactory.create_book(book_type, **kwargs)
            
            # Create and execute the add book command
            command = AddBookCommand(self.controller.catalog, book)
            result = self.command_invoker.execute_command(command)
            
            if result['success']:
                # Notify the event manager
                self.controller.event_manager.book_added(book)
                
                # Show success message
                messagebox.showinfo("Success", f"Book '{book.title}' added successfully")
                
                # Clear the form
                for var_name in self.book_vars:
                    if isinstance(self.book_vars[var_name], tk.BooleanVar):
                        self.book_vars[var_name].set(False)
                    else:
                        self.book_vars[var_name].set("")
                
                # Refresh the book list
                self.populate_book_list()
            else:
                messagebox.showerror("Error", result['message'])
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def create_book_details(self, parent):
        """
        Create the book details tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the book details
        self.details_frame = ttk.Frame(parent)
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Initial message
        ttk.Label(self.details_frame, text="Select a book from the Book List tab to view details", 
                 font=('Helvetica', 12, 'italic')).pack(pady=50)
    
    def update_book_details(self, book_id):
        """
        Update the book details tab with information about the selected book.
        
        Args:
            book_id (str): ID of the book to display
        """
        # Clear the frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Get the book
        book = self.controller.catalog.get_book(book_id)
        
        if not book:
            ttk.Label(self.details_frame, text=f"Book not found: {book_id}", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Create a scrollable frame for the details
        canvas = tk.Canvas(self.details_frame)
        scrollbar = ttk.Scrollbar(self.details_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Book title
        ttk.Label(scrollable_frame, text=book.title, font=('Helvetica', 16, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 10))
        
        # Book details
        details = [
            ("Author:", book.author),
            ("Year Published:", str(book.year_published)),
            ("ISBN:", book.isbn or "N/A"),
            ("Condition:", book.condition.name),
            ("Status:", book.status.name),
            ("Location:", book.location or "N/A")
        ]
        
        # Display book type specific details
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
        
        # Display the details
        for i, (label, value) in enumerate(details):
            ttk.Label(scrollable_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i+1, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(scrollable_frame, text=value, font=('Helvetica', 10)).grid(
                row=i+1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Display availability information
        availability = self.controller.library.get_book_availability(book_id)
        ttk.Label(scrollable_frame, text="Availability:", font=('Helvetica', 10, 'bold')).grid(
            row=len(details)+1, column=0, sticky=tk.W, padx=5, pady=(10, 2))
        ttk.Label(scrollable_frame, text=availability['message'], font=('Helvetica', 10)).grid(
            row=len(details)+1, column=1, sticky=tk.W, padx=5, pady=(10, 2))
        
        # Display lending information
        if book.status == BookStatus.BORROWED:
            lending_records = self.controller.catalog.get_book_lending_records(book_id)
            active_records = [r for r in lending_records if r.status.name == 'ACTIVE']
            
            if active_records:
                record = active_records[0]
                user = self.controller.catalog.get_user(record.user_id)
                
                ttk.Label(scrollable_frame, text="Currently borrowed by:", font=('Helvetica', 10, 'bold')).grid(
                    row=len(details)+2, column=0, sticky=tk.W, padx=5, pady=2)
                ttk.Label(scrollable_frame, text=user.name if user else "Unknown", font=('Helvetica', 10)).grid(
                    row=len(details)+2, column=1, sticky=tk.W, padx=5, pady=2)
                
                ttk.Label(scrollable_frame, text="Due date:", font=('Helvetica', 10, 'bold')).grid(
                    row=len(details)+3, column=0, sticky=tk.W, padx=5, pady=2)
                ttk.Label(scrollable_frame, text=record.due_date.strftime('%Y-%m-%d'), font=('Helvetica', 10)).grid(
                    row=len(details)+3, column=1, sticky=tk.W, padx=5, pady=2)
                
                if record.is_overdue():
                    days_overdue = record.days_overdue()
                    
                    ttk.Label(scrollable_frame, text="Overdue by:", font=('Helvetica', 10, 'bold')).grid(
                        row=len(details)+4, column=0, sticky=tk.W, padx=5, pady=2)
                    ttk.Label(scrollable_frame, text=f"{days_overdue} days", font=('Helvetica', 10)).grid(
                        row=len(details)+4, column=1, sticky=tk.W, padx=5, pady=2)
                    
                    ttk.Label(scrollable_frame, text="Late fee:", font=('Helvetica', 10, 'bold')).grid(
                        row=len(details)+5, column=0, sticky=tk.W, padx=5, pady=2)
                    ttk.Label(scrollable_frame, text=f"${book.get_late_fee(days_overdue):.2f}", font=('Helvetica', 10)).grid(
                        row=len(details)+5, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Add action buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(details)+6, column=0, columnspan=2, pady=20)
        
        # Checkout button
        if book.status == BookStatus.AVAILABLE and self.controller.current_user:
            checkout_button = ttk.Button(button_frame, text="Checkout Book", 
                                       command=lambda: self.checkout_book(book_id))
            checkout_button.pack(side=tk.LEFT, padx=5)
        
        # Return button
        if (book.status == BookStatus.BORROWED and self.controller.current_user and
            any(r.user_id == self.controller.current_user.user_id and r.status.name == 'ACTIVE'
                for r in self.controller.catalog.get_book_lending_records(book_id))):
            return_button = ttk.Button(button_frame, text="Return Book", 
                                     command=lambda: self.return_book(book_id))
            return_button.pack(side=tk.LEFT, padx=5)
    
    def checkout_book(self, book_id):
        """
        Check out a book.
        
        Args:
            book_id (str): ID of the book to check out
        """
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please log in first")
            return
        
        # Create and execute the checkout command
        from patterns.behavioral.action_command import CheckoutBookCommand
        command = CheckoutBookCommand(self.controller.catalog, book_id, self.controller.current_user.user_id)
        result = self.command_invoker.execute_command(command)
        
        if result['success']:
            messagebox.showinfo("Success", f"{result['message']}\nDue date: {result['due_date'].strftime('%Y-%m-%d')}")
            
            # Notify the event manager
            book = self.controller.catalog.get_book(book_id)
            self.controller.event_manager.book_borrowed(book, self.controller.current_user)
            
            # Update the book details
            self.update_book_details(book_id)
            
            # Refresh the book list
            self.populate_book_list()
        else:
            messagebox.showerror("Error", result['message'])
    
    def return_book(self, book_id):
        """
        Return a book.
        
        Args:
            book_id (str): ID of the book to return
        """
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please log in first")
            return
        
        # Ask if the book's condition has changed
        condition_changed = messagebox.askyesno("Book Condition", "Has the book's condition changed?")
        
        # Create and execute the return command
        from patterns.behavioral.action_command import ReturnBookCommand
        command = ReturnBookCommand(self.controller.catalog, book_id, self.controller.current_user.user_id, condition_changed)
        result = self.command_invoker.execute_command(command)
        
        if result['success']:
            messagebox.showinfo("Success", result['message'])
            
            # Notify the event manager
            book = self.controller.catalog.get_book(book_id)
            self.controller.event_manager.book_returned(book, self.controller.current_user)
            
            # Update the book details
            self.update_book_details(book_id)
            
            # Refresh the book list
            self.populate_book_list()
        else:
            messagebox.showerror("Error", result['message'])
    
    def update_frame(self):
        """Update the frame with current data."""
        # Refresh the book list
        if hasattr(self, 'book_tree'):
            self.populate_book_list()
