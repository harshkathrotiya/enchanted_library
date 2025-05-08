"""
Lending frame for the Enchanted Library GUI.
This module provides the interface for managing book lending.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from models.user import UserRole
from patterns.behavioral.action_command import CheckoutBookCommand, ReturnBookCommand, CommandInvoker


class LendingFrame(ttk.Frame):
    """Frame for managing book lending."""
    
    def __init__(self, parent, controller):
        """
        Initialize the lending frame.
        
        Args:
            parent: The parent widget
            controller: The main application controller
        """
        super().__init__(parent)
        self.controller = controller
        self.command_invoker = CommandInvoker()
        
        # Create the lending management layout
        self.create_lending_management()
    
    def create_lending_management(self):
        """Create the lending management layout."""
        # Title
        title_label = ttk.Label(self, text="Lending Management", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create a notebook for different lending operations
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        borrowed_books_frame = ttk.Frame(notebook)
        overdue_books_frame = ttk.Frame(notebook)
        checkout_frame = ttk.Frame(notebook)
        return_frame = ttk.Frame(notebook)
        
        notebook.add(borrowed_books_frame, text="My Borrowed Books")
        notebook.add(overdue_books_frame, text="Overdue Books")
        notebook.add(checkout_frame, text="Checkout Book")
        notebook.add(return_frame, text="Return Book")
        
        # Create the content for each tab
        self.create_borrowed_books_tab(borrowed_books_frame)
        self.create_overdue_books_tab(overdue_books_frame)
        self.create_checkout_tab(checkout_frame)
        self.create_return_tab(return_frame)
    
    def create_borrowed_books_tab(self, parent):
        """
        Create the borrowed books tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the borrowed books
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get the user's borrowed books
        if not self.controller.current_user:
            ttk.Label(frame, text="Please log in to view your borrowed books", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        borrowed_books = self.controller.library.get_user_borrowed_books(
            self.controller.current_user.user_id)
        
        if not borrowed_books:
            ttk.Label(frame, text="You have no borrowed books", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Create a treeview to display the books
        columns = ('id', 'title', 'author', 'borrow_date', 'due_date', 'status')
        self.borrowed_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define the columns
        self.borrowed_tree.heading('id', text='ID')
        self.borrowed_tree.heading('title', text='Title')
        self.borrowed_tree.heading('author', text='Author')
        self.borrowed_tree.heading('borrow_date', text='Borrowed On')
        self.borrowed_tree.heading('due_date', text='Due Date')
        self.borrowed_tree.heading('status', text='Status')
        
        # Set column widths
        self.borrowed_tree.column('id', width=250)
        self.borrowed_tree.column('title', width=200)
        self.borrowed_tree.column('author', width=150)
        self.borrowed_tree.column('borrow_date', width=100)
        self.borrowed_tree.column('due_date', width=100)
        self.borrowed_tree.column('status', width=80)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.borrowed_tree.yview)
        self.borrowed_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.borrowed_tree.xview)
        self.borrowed_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.borrowed_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add the books to the treeview
        for item in borrowed_books:
            book = item['book']
            borrow_date = item['borrow_date']
            due_date = item['due_date']
            status = "Overdue" if due_date < datetime.now() else "On Time"
            
            self.borrowed_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                borrow_date.strftime('%Y-%m-%d'),
                due_date.strftime('%Y-%m-%d'),
                status
            ))
        
        # Add a return button
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        return_button = ttk.Button(button_frame, text="Return Selected Book", 
                                  command=self.return_selected_book)
        return_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(button_frame, text="Refresh", 
                                   command=lambda: self.update_frame())
        refresh_button.pack(side=tk.LEFT, padx=5)
    
    def return_selected_book(self):
        """Return the selected book."""
        # Get the selected item
        selection = self.borrowed_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a book to return")
            return
        
        # Get the book ID
        book_id = self.borrowed_tree.item(selection[0], 'values')[0]
        
        # Ask if the book's condition has changed
        condition_changed = messagebox.askyesno("Book Condition", "Has the book's condition changed?")
        
        # Create and execute the return command
        command = ReturnBookCommand(self.controller.catalog, book_id, 
                                   self.controller.current_user.user_id, condition_changed)
        result = self.command_invoker.execute_command(command)
        
        if result['success']:
            messagebox.showinfo("Success", result['message'])
            
            # Notify the event manager
            book = self.controller.catalog.get_book(book_id)
            self.controller.event_manager.book_returned(book, self.controller.current_user)
            
            # Update the frame
            self.update_frame()
        else:
            messagebox.showerror("Error", result['message'])
    
    def create_overdue_books_tab(self, parent):
        """
        Create the overdue books tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the overdue books
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Check if user has permission to view all overdue books
        if not self.controller.current_user or self.controller.current_user.get_role() != UserRole.LIBRARIAN:
            ttk.Label(frame, text="Only librarians can view all overdue books", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Get all overdue books
        overdue_books = self.controller.library.get_overdue_books()
        
        if not overdue_books:
            ttk.Label(frame, text="No overdue books", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Create a treeview to display the books
        columns = ('id', 'title', 'user', 'due_date', 'days_overdue', 'late_fee')
        self.overdue_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define the columns
        self.overdue_tree.heading('id', text='ID')
        self.overdue_tree.heading('title', text='Title')
        self.overdue_tree.heading('user', text='Borrowed By')
        self.overdue_tree.heading('due_date', text='Due Date')
        self.overdue_tree.heading('days_overdue', text='Days Overdue')
        self.overdue_tree.heading('late_fee', text='Late Fee')
        
        # Set column widths
        self.overdue_tree.column('id', width=250)
        self.overdue_tree.column('title', width=200)
        self.overdue_tree.column('user', width=150)
        self.overdue_tree.column('due_date', width=100)
        self.overdue_tree.column('days_overdue', width=100)
        self.overdue_tree.column('late_fee', width=80)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.overdue_tree.yview)
        self.overdue_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.overdue_tree.xview)
        self.overdue_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.overdue_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add the books to the treeview
        for item in overdue_books:
            book = item['book']
            user = item['user']
            record = item['record']
            days_overdue = item['days_overdue']
            late_fee = item['late_fee']
            
            self.overdue_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                user.name,
                record.due_date.strftime('%Y-%m-%d'),
                days_overdue,
                f"${late_fee:.2f}"
            ))
        
        # Add a refresh button
        refresh_button = ttk.Button(frame, text="Refresh", 
                                   command=lambda: self.update_frame())
        refresh_button.pack(pady=10)
    
    def create_checkout_tab(self, parent):
        """
        Create the checkout tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the checkout form
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Check if user is logged in
        if not self.controller.current_user:
            ttk.Label(frame, text="Please log in to check out books", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Book search
        ttk.Label(frame, text="Search for a book to check out:", 
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search Term:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_button = ttk.Button(search_frame, text="Search", 
                                  command=self.search_books_for_checkout)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Create a treeview to display the search results
        columns = ('id', 'title', 'author', 'year', 'type', 'status')
        self.search_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define the columns
        self.search_tree.heading('id', text='ID')
        self.search_tree.heading('title', text='Title')
        self.search_tree.heading('author', text='Author')
        self.search_tree.heading('year', text='Year')
        self.search_tree.heading('type', text='Type')
        self.search_tree.heading('status', text='Status')
        
        # Set column widths
        self.search_tree.column('id', width=250)
        self.search_tree.column('title', width=200)
        self.search_tree.column('author', width=150)
        self.search_tree.column('year', width=50)
        self.search_tree.column('type', width=100)
        self.search_tree.column('status', width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.search_tree.xview)
        self.search_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.search_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add a checkout button
        checkout_button = ttk.Button(frame, text="Checkout Selected Book", 
                                    command=self.checkout_selected_book)
        checkout_button.pack(pady=10)
    
    def search_books_for_checkout(self):
        """Search for books to check out."""
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
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
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
            
            self.search_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book.year_published,
                book_type,
                book.status.name
            ))
    
    def checkout_selected_book(self):
        """Check out the selected book."""
        # Get the selected item
        selection = self.search_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a book to check out")
            return
        
        # Get the book ID
        book_id = self.search_tree.item(selection[0], 'values')[0]
        
        # Create and execute the checkout command
        command = CheckoutBookCommand(self.controller.catalog, book_id, 
                                     self.controller.current_user.user_id)
        result = self.command_invoker.execute_command(command)
        
        if result['success']:
            messagebox.showinfo("Success", 
                              f"{result['message']}\nDue date: {result['due_date'].strftime('%Y-%m-%d')}")
            
            # Notify the event manager
            book = self.controller.catalog.get_book(book_id)
            self.controller.event_manager.book_borrowed(book, self.controller.current_user)
            
            # Update the frame
            self.update_frame()
        else:
            messagebox.showerror("Error", result['message'])
    
    def create_return_tab(self, parent):
        """
        Create the return tab.
        
        Args:
            parent: The parent widget
        """
        # Create a frame for the return form
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Check if user is logged in
        if not self.controller.current_user:
            ttk.Label(frame, text="Please log in to return books", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Get the user's borrowed books
        borrowed_books = self.controller.library.get_user_borrowed_books(
            self.controller.current_user.user_id)
        
        if not borrowed_books:
            ttk.Label(frame, text="You have no borrowed books to return", 
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return
        
        # Create a treeview to display the borrowed books
        columns = ('id', 'title', 'author', 'due_date', 'status')
        self.return_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define the columns
        self.return_tree.heading('id', text='ID')
        self.return_tree.heading('title', text='Title')
        self.return_tree.heading('author', text='Author')
        self.return_tree.heading('due_date', text='Due Date')
        self.return_tree.heading('status', text='Status')
        
        # Set column widths
        self.return_tree.column('id', width=250)
        self.return_tree.column('title', width=200)
        self.return_tree.column('author', width=150)
        self.return_tree.column('due_date', width=100)
        self.return_tree.column('status', width=80)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.return_tree.yview)
        self.return_tree.configure(yscroll=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.return_tree.xview)
        self.return_tree.configure(xscroll=x_scrollbar.set)
        
        # Pack the scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.return_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add the books to the treeview
        for item in borrowed_books:
            book = item['book']
            due_date = item['due_date']
            status = "Overdue" if due_date < datetime.now() else "On Time"
            
            self.return_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                due_date.strftime('%Y-%m-%d'),
                status
            ))
        
        # Add a condition frame
        condition_frame = ttk.Frame(frame)
        condition_frame.pack(fill=tk.X, pady=10)
        
        self.condition_changed_var = tk.BooleanVar(value=False)
        condition_check = ttk.Checkbutton(condition_frame, text="Book condition has changed", 
                                         variable=self.condition_changed_var)
        condition_check.pack(side=tk.LEFT, padx=5)
        
        # Add a return button
        return_button = ttk.Button(frame, text="Return Selected Book", 
                                  command=self.return_book_from_tab)
        return_button.pack(pady=10)
    
    def return_book_from_tab(self):
        """Return the selected book from the return tab."""
        # Get the selected item
        selection = self.return_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a book to return")
            return
        
        # Get the book ID
        book_id = self.return_tree.item(selection[0], 'values')[0]
        
        # Get the condition changed value
        condition_changed = self.condition_changed_var.get()
        
        # Create and execute the return command
        command = ReturnBookCommand(self.controller.catalog, book_id, 
                                   self.controller.current_user.user_id, condition_changed)
        result = self.command_invoker.execute_command(command)
        
        if result['success']:
            messagebox.showinfo("Success", result['message'])
            
            # Notify the event manager
            book = self.controller.catalog.get_book(book_id)
            self.controller.event_manager.book_returned(book, self.controller.current_user)
            
            # Update the frame
            self.update_frame()
        else:
            messagebox.showerror("Error", result['message'])
    
    def update_frame(self):
        """Update the frame with current data."""
        # Destroy all widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate the lending management layout
        self.create_lending_management()
