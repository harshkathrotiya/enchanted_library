"""
Search frame for the Enchanted Library GUI.
This module provides the interface for searching books.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from models.book import BookStatus
from services.recommendation import RecommendationService


class SearchFrame(ttk.Frame):
    """Frame for searching books."""
    
    def __init__(self, parent, controller):
        """
        Initialize the search frame.
        
        Args:
            parent: The parent widget
            controller: The main application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.recommendation_service = RecommendationService(controller.catalog)
        
        # Create the search layout
        self.create_search_layout()
    
    def create_search_layout(self):
        """Create the search layout."""
        # Title
        title_label = ttk.Label(self, text="Search & Recommendations", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create a notebook for different search operations
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        basic_search_frame = ttk.Frame(notebook)
        advanced_search_frame = ttk.Frame(notebook)
        recommendations_frame = ttk.Frame(notebook)
        
        notebook.add(basic_search_frame, text="Basic Search")
        notebook.add(advanced_search_frame, text="Advanced Search")
        notebook.add(recommendations_frame, text="Recommendations")
        
        # Create the content for each tab
        self.create_basic_search(basic_search_frame)
        self.create_advanced_search(advanced_search_frame)
        self.create_recommendations(recommendations_frame)
    
    def create_basic_search(self, parent):
        """
        Create the basic search tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the search form
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Search term
        ttk.Label(form_frame, text="Search Term:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(form_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Search button
        search_button = ttk.Button(form_frame, text="Search", command=self.perform_basic_search)
        search_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Create a frame for the search results
        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create a treeview to display the search results
        columns = ('id', 'title', 'author', 'year', 'type', 'status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        # Define the columns
        self.results_tree.heading('id', text='ID')
        self.results_tree.heading('title', text='Title')
        self.results_tree.heading('author', text='Author')
        self.results_tree.heading('year', text='Year')
        self.results_tree.heading('type', text='Type')
        self.results_tree.heading('status', text='Status')
        
        # Set column widths
        self.results_tree.column('id', width=250)
        self.results_tree.column('title', width=200)
        self.results_tree.column('author', width=150)
        self.results_tree.column('year', width=50)
        self.results_tree.column('type', width=100)
        self.results_tree.column('status', width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event to view book details
        self.results_tree.bind("<Double-1>", self.view_book_details)
    
    def perform_basic_search(self):
        """Perform a basic search."""
        search_term = self.search_var.get()
        
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return
        
        # Search in title and author
        books = self.controller.catalog.search_books(title=search_term) + self.controller.catalog.search_books(author=search_term)
        
        # Remove duplicates
        unique_books = {}
        for book in books:
            unique_books[book.book_id] = book
        
        books = list(unique_books.values())
        
        # Clear the treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if not books:
            messagebox.showinfo("Search Results", f"No books found matching '{search_term}'")
            return
        
        # Add books to the treeview
        for book in books:
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
            
            self.results_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name
            ))
    
    def create_advanced_search(self, parent):
        """
        Create the advanced search tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the search form
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Search fields
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
        
        # Book type
        ttk.Label(form_frame, text="Book Type:", font=('Helvetica', 10, 'bold')).grid(
            row=len(fields), column=0, sticky=tk.W, padx=5, pady=5)
        
        self.advanced_search_vars["book_type"] = tk.StringVar(value="any")
        book_types = [("Any", "any"), ("General", "general"), ("Rare", "rare"), ("Ancient", "ancient")]
        
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=len(fields), column=1, sticky=tk.W, padx=5, pady=5)
        
        for i, (text, value) in enumerate(book_types):
            ttk.Radiobutton(type_frame, text=text, variable=self.advanced_search_vars["book_type"], 
                           value=value).grid(row=0, column=i, padx=5)
        
        # Book status
        ttk.Label(form_frame, text="Status:", font=('Helvetica', 10, 'bold')).grid(
            row=len(fields)+1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.advanced_search_vars["status"] = tk.StringVar(value="any")
        statuses = [("Any", "any"), ("Available", "AVAILABLE"), ("Borrowed", "BORROWED")]
        
        status_frame = ttk.Frame(form_frame)
        status_frame.grid(row=len(fields)+1, column=1, sticky=tk.W, padx=5, pady=5)
        
        for i, (text, value) in enumerate(statuses):
            ttk.Radiobutton(status_frame, text=text, variable=self.advanced_search_vars["status"], 
                           value=value).grid(row=0, column=i, padx=5)
        
        # Search button
        search_button = ttk.Button(form_frame, text="Search", command=self.perform_advanced_search)
        search_button.grid(row=len(fields)+2, column=0, columnspan=2, pady=10)
        
        # Create a frame for the search results
        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create a treeview to display the search results
        columns = ('id', 'title', 'author', 'year', 'type', 'status')
        self.advanced_results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        # Define the columns
        self.advanced_results_tree.heading('id', text='ID')
        self.advanced_results_tree.heading('title', text='Title')
        self.advanced_results_tree.heading('author', text='Author')
        self.advanced_results_tree.heading('year', text='Year')
        self.advanced_results_tree.heading('type', text='Type')
        self.advanced_results_tree.heading('status', text='Status')
        
        # Set column widths
        self.advanced_results_tree.column('id', width=250)
        self.advanced_results_tree.column('title', width=200)
        self.advanced_results_tree.column('author', width=150)
        self.advanced_results_tree.column('year', width=50)
        self.advanced_results_tree.column('type', width=100)
        self.advanced_results_tree.column('status', width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.advanced_results_tree.yview)
        self.advanced_results_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.advanced_results_tree.xview)
        self.advanced_results_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.advanced_results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event to view book details
        self.advanced_results_tree.bind("<Double-1>", self.view_book_details_advanced)
    
    def perform_advanced_search(self):
        """Perform an advanced search."""
        # Build search criteria
        criteria = {}
        
        for field in ["title", "author", "isbn"]:
            if self.advanced_search_vars[field].get():
                criteria[field] = self.advanced_search_vars[field].get()
        
        # Handle year separately (convert to int)
        if self.advanced_search_vars["year"].get():
            try:
                criteria["year"] = int(self.advanced_search_vars["year"].get())
            except ValueError:
                messagebox.showerror("Error", "Year must be a number")
                return
        
        # Get all books first
        books = list(self.controller.catalog._books.values())
        
        # Filter by criteria
        for key, value in criteria.items():
            if key == "title":
                books = [book for book in books if value.lower() in book.title.lower()]
            elif key == "author":
                books = [book for book in books if value.lower() in book.author.lower()]
            elif key == "year":
                books = [book for book in books if book.year_published == value]
            elif key == "isbn":
                books = [book for book in books if book.isbn and value.lower() in book.isbn.lower()]
        
        # Filter by book type
        book_type = self.advanced_search_vars["book_type"].get()
        if book_type != "any":
            from models.book import GeneralBook, RareBook, AncientScript
            if book_type == "general":
                books = [book for book in books if isinstance(book, GeneralBook)]
            elif book_type == "rare":
                books = [book for book in books if isinstance(book, RareBook)]
            elif book_type == "ancient":
                books = [book for book in books if isinstance(book, AncientScript)]
        
        # Filter by status
        status = self.advanced_search_vars["status"].get()
        if status != "any":
            books = [book for book in books if book.status.name == status]
        
        # Clear the treeview
        for item in self.advanced_results_tree.get_children():
            self.advanced_results_tree.delete(item)
        
        if not books:
            messagebox.showinfo("Search Results", "No books found matching your criteria")
            return
        
        # Add books to the treeview
        for book in books:
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
            
            self.advanced_results_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name
            ))
    
    def create_recommendations(self, parent):
        """
        Create the recommendations tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the recommendations
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Check if user is logged in
        if not self.controller.current_user:
            ttk.Label(frame, text="Please log in to view recommendations", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Title
        ttk.Label(frame, text="Recommended Books", font=('Helvetica', 12, 'bold')).pack(
            anchor=tk.W, pady=(0, 10))
        
        # Get recommendations
        recommendations = self.recommendation_service.get_recommendations_for_user(
            self.controller.current_user.user_id)
        
        if not recommendations:
            ttk.Label(frame, text="No recommendations available. Try borrowing some books first!", 
                     font=('Helvetica', 10, 'italic')).pack(pady=20)
            return
        
        # Create a treeview to display the recommendations
        columns = ('id', 'title', 'author', 'year', 'type', 'status', 'reason')
        self.recommendations_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define the columns
        self.recommendations_tree.heading('id', text='ID')
        self.recommendations_tree.heading('title', text='Title')
        self.recommendations_tree.heading('author', text='Author')
        self.recommendations_tree.heading('year', text='Year')
        self.recommendations_tree.heading('type', text='Type')
        self.recommendations_tree.heading('status', text='Status')
        self.recommendations_tree.heading('reason', text='Recommendation Reason')
        
        # Set column widths
        self.recommendations_tree.column('id', width=250)
        self.recommendations_tree.column('title', width=200)
        self.recommendations_tree.column('author', width=150)
        self.recommendations_tree.column('year', width=50)
        self.recommendations_tree.column('type', width=100)
        self.recommendations_tree.column('status', width=100)
        self.recommendations_tree.column('reason', width=200)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.recommendations_tree.yview)
        self.recommendations_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.recommendations_tree.xview)
        self.recommendations_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.recommendations_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add the recommendations to the treeview
        for recommendation in recommendations:
            book = recommendation['book']
            reason = recommendation['reason']
            
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
            
            self.recommendations_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name,
                reason
            ))
        
        # Bind double-click event to view book details
        self.recommendations_tree.bind("<Double-1>", self.view_book_details_recommendations)
        
        # Add a refresh button
        refresh_button = ttk.Button(frame, text="Refresh Recommendations", 
                                   command=lambda: self.update_frame())
        refresh_button.pack(pady=10)
    
    def view_book_details(self, event):
        """
        View details of a book from the basic search results.
        
        Args:
            event: The event object
        """
        # Get the selected item
        selection = self.results_tree.selection()
        if not selection:
            return
        
        # Get the book ID
        book_id = self.results_tree.item(selection[0], 'values')[0]
        
        # Show the book details
        self.show_book_details(book_id)
    
    def view_book_details_advanced(self, event):
        """
        View details of a book from the advanced search results.
        
        Args:
            event: The event object
        """
        # Get the selected item
        selection = self.advanced_results_tree.selection()
        if not selection:
            return
        
        # Get the book ID
        book_id = self.advanced_results_tree.item(selection[0], 'values')[0]
        
        # Show the book details
        self.show_book_details(book_id)
    
    def view_book_details_recommendations(self, event):
        """
        View details of a book from the recommendations.
        
        Args:
            event: The event object
        """
        # Get the selected item
        selection = self.recommendations_tree.selection()
        if not selection:
            return
        
        # Get the book ID
        book_id = self.recommendations_tree.item(selection[0], 'values')[0]
        
        # Show the book details
        self.show_book_details(book_id)
    
    def show_book_details(self, book_id):
        """
        Show details of a book in a popup window.
        
        Args:
            book_id (str): ID of the book to display
        """
        # Get the book
        book = self.controller.catalog.get_book(book_id)
        
        if not book:
            messagebox.showerror("Error", f"Book not found: {book_id}")
            return
        
        # Create a new toplevel window
        details_window = tk.Toplevel(self)
        details_window.title(f"Book Details: {book.title}")
        details_window.geometry("600x500")
        details_window.minsize(500, 400)
        
        # Create a scrollable frame for the details
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
        
        # Book title
        ttk.Label(scrollable_frame, text=book.title, font=('Helvetica', 16, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(10, 5))
        
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
                row=i+1, column=0, sticky=tk.W, padx=10, pady=2)
            ttk.Label(scrollable_frame, text=value, font=('Helvetica', 10)).grid(
                row=i+1, column=1, sticky=tk.W, padx=10, pady=2)
        
        # Display availability information
        availability = self.controller.library.get_book_availability(book_id)
        ttk.Label(scrollable_frame, text="Availability:", font=('Helvetica', 10, 'bold')).grid(
            row=len(details)+1, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        ttk.Label(scrollable_frame, text=availability['message'], font=('Helvetica', 10)).grid(
            row=len(details)+1, column=1, sticky=tk.W, padx=10, pady=(10, 2))
        
        # Display lending information
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
        
        # Add action buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(details)+4, column=0, columnspan=2, pady=20)
        
        # Checkout button
        if book.status == BookStatus.AVAILABLE and self.controller.current_user:
            checkout_button = ttk.Button(button_frame, text="Checkout Book", 
                                       command=lambda: self.checkout_book(book_id, details_window))
            checkout_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=details_window.destroy)
        close_button.pack(side=tk.LEFT, padx=5)
    
    def checkout_book(self, book_id, details_window):
        """
        Check out a book.
        
        Args:
            book_id (str): ID of the book to check out
            details_window: The details window to close after checkout
        """
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please log in first")
            return
        
        # Create and execute the checkout command
        from patterns.behavioral.action_command import CheckoutBookCommand, CommandInvoker
        command_invoker = CommandInvoker()
        command = CheckoutBookCommand(self.controller.catalog, book_id, self.controller.current_user.user_id)
        result = command_invoker.execute_command(command)
        
        if result['success']:
            messagebox.showinfo("Success", 
                              f"{result['message']}\nDue date: {result['due_date'].strftime('%Y-%m-%d')}")
            
            # Notify the event manager
            book = self.controller.catalog.get_book(book_id)
            self.controller.event_manager.book_borrowed(book, self.controller.current_user)
            
            # Close the details window
            details_window.destroy()
            
            # Update the frame
            self.update_frame()
        else:
            messagebox.showerror("Error", result['message'])
    
    def update_frame(self):
        """Update the frame with current data."""
        # Destroy all widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate the search layout
        self.create_search_layout()
