"""
Dashboard frame for the Enchanted Library GUI.
This module provides the main dashboard interface.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class DashboardFrame(ttk.Frame):
    """Frame for the main dashboard."""
    
    def __init__(self, parent, controller):
        """
        Initialize the dashboard frame.
        
        Args:
            parent: The parent widget
            controller: The main application controller
        """
        super().__init__(parent)
        self.controller = controller
        
        # Create the dashboard layout
        self.create_dashboard()
    
    def create_dashboard(self):
        """Create the dashboard layout."""
        # Title
        title_label = ttk.Label(self, text="Dashboard", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create a frame for the dashboard content
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split the dashboard into two columns
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Add widgets to the left column
        self.create_user_info_widget(left_column)
        self.create_borrowed_books_widget(left_column)
        
        # Add widgets to the right column
        self.create_library_stats_widget(right_column)
        self.create_recent_activity_widget(right_column)
    
    def create_user_info_widget(self, parent):
        """
        Create the user information widget.
        
        Args:
            parent: The parent widget
        """
        # Create a frame with a border
        frame = ttk.LabelFrame(parent, text="User Information")
        frame.pack(fill=tk.X, pady=10)
        
        # User information
        user = self.controller.current_user
        
        # Create a grid for the user info
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add user details
        labels = [
            ("Name:", user.name),
            ("Email:", user.email),
            ("Role:", user.get_role().name),
            ("Last Login:", user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else "Never")
        ]
        
        # Add role-specific information
        if user.get_role().name == 'LIBRARIAN':
            labels.extend([
                ("Department:", user.department or "N/A"),
                ("Staff ID:", user.staff_id or "N/A"),
                ("Admin Level:", str(user.admin_level))
            ])
        elif user.get_role().name == 'SCHOLAR':
            labels.extend([
                ("Institution:", user.institution or "N/A"),
                ("Field of Study:", user.field_of_study or "N/A"),
                ("Academic Level:", user.academic_level)
            ])
        elif user.get_role().name == 'GUEST':
            labels.extend([
                ("Membership Type:", user.membership_type),
                ("Membership Expiry:", user.membership_expiry.strftime('%Y-%m-%d') if user.membership_expiry else "N/A"),
                ("Membership Valid:", "Yes" if user.is_membership_valid() else "No")
            ])
        
        # Display the labels
        for i, (label, value) in enumerate(labels):
            ttk.Label(info_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=value, font=('Helvetica', 10)).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2)
    
    def create_borrowed_books_widget(self, parent):
        """
        Create the borrowed books widget.
        
        Args:
            parent: The parent widget
        """
        # Create a frame with a border
        frame = ttk.LabelFrame(parent, text="Your Borrowed Books")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Get the user's borrowed books
        borrowed_books = self.controller.library.get_user_borrowed_books(
            self.controller.current_user.user_id)
        
        if not borrowed_books:
            ttk.Label(frame, text="You have no borrowed books", 
                     font=('Helvetica', 10, 'italic')).pack(padx=10, pady=10)
            return
        
        # Create a treeview to display the books
        columns = ('title', 'author', 'due_date', 'status')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Define the columns
        tree.heading('title', text='Title')
        tree.heading('author', text='Author')
        tree.heading('due_date', text='Due Date')
        tree.heading('status', text='Status')
        
        # Set column widths
        tree.column('title', width=200)
        tree.column('author', width=150)
        tree.column('due_date', width=100)
        tree.column('status', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add the books to the treeview
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
    
    def create_library_stats_widget(self, parent):
        """
        Create the library statistics widget.
        
        Args:
            parent: The parent widget
        """
        # Create a frame with a border
        frame = ttk.LabelFrame(parent, text="Library Statistics")
        frame.pack(fill=tk.X, pady=10)
        
        # Create a frame for the stats
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Calculate some basic statistics
        total_books = len(self.controller.catalog._books)
        available_books = sum(1 for book in self.controller.catalog._books.values() 
                             if book.status.name == 'AVAILABLE')
        borrowed_books = total_books - available_books
        total_users = len(self.controller.catalog._users)
        
        # Display the statistics
        stats = [
            ("Total Books:", str(total_books)),
            ("Available Books:", str(available_books)),
            ("Borrowed Books:", str(borrowed_books)),
            ("Total Users:", str(total_users))
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(stats_frame, text=label, font=('Helvetica', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(stats_frame, text=value, font=('Helvetica', 10)).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2)
    
    def create_recent_activity_widget(self, parent):
        """
        Create the recent activity widget.
        
        Args:
            parent: The parent widget
        """
        # Create a frame with a border
        frame = ttk.LabelFrame(parent, text="Recent Activity")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Get recent events from the event manager
        events = self.controller.event_manager.events[-10:] if self.controller.event_manager.events else []
        
        if not events:
            ttk.Label(frame, text="No recent activity", 
                     font=('Helvetica', 10, 'italic')).pack(padx=10, pady=10)
            return
        
        # Create a listbox to display the events
        listbox = tk.Listbox(frame, font=('Helvetica', 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add the events to the listbox (most recent first)
        for event in reversed(events):
            event_time = event.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            event_type = event.event_type.replace('_', ' ').title()
            
            # Format the event description based on type
            if event.event_type == 'book_borrowed':
                description = f"{event_time} - {event_type}: '{event.data.get('title', 'Unknown')}' by {event.data.get('user_name', 'Unknown')}"
            elif event.event_type == 'book_returned':
                description = f"{event_time} - {event_type}: '{event.data.get('title', 'Unknown')}' by {event.data.get('user_name', 'Unknown')}"
            elif event.event_type == 'book_added':
                description = f"{event_time} - {event_type}: '{event.data.get('title', 'Unknown')}' by {event.data.get('author', 'Unknown')}"
            else:
                description = f"{event_time} - {event_type}"
            
            listbox.insert(tk.END, description)
    
    def update_frame(self):
        """Update the dashboard with current data."""
        # Destroy all widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate the dashboard
        self.create_dashboard()
