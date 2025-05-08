"""
Login frame for the Enchanted Library GUI.
This module provides the login interface.
"""
import tkinter as tk
from tkinter import ttk, messagebox


class LoginFrame(ttk.Frame):
    """Frame for user login."""
    
    def __init__(self, parent, controller):
        """
        Initialize the login frame.
        
        Args:
            parent: The parent widget
            controller: The main application controller
        """
        super().__init__(parent)
        self.controller = controller
        
        # Create a frame to center the login form
        center_frame = ttk.Frame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Create the login form
        self.create_login_form(center_frame)
    
    def create_login_form(self, parent):
        """
        Create the login form.
        
        Args:
            parent: The parent widget
        """
        # Title
        title_label = ttk.Label(parent, text="Enchanted Library", 
                               font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(parent, text="Please login to continue", 
                                  font=('Helvetica', 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Email label and entry
        email_label = ttk.Label(parent, text="Email:", font=('Helvetica', 12))
        email_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(parent, textvariable=self.email_var, width=30, font=('Helvetica', 12))
        email_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Password label and entry
        password_label = ttk.Label(parent, text="Password:", font=('Helvetica', 12))
        password_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(parent, textvariable=self.password_var, 
                                  show="*", width=30, font=('Helvetica', 12))
        password_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Login button
        login_button = ttk.Button(parent, text="Login", command=self.login)
        login_button.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Sample credentials label
        creds_label = ttk.Label(parent, text="Sample credentials:", font=('Helvetica', 10))
        creds_label.grid(row=5, column=0, columnspan=2, pady=(30, 5))
        
        # Sample credentials
        samples = [
            "Librarian: alice@library.com / password123",
            "Scholar: carol@university.edu / password123",
            "Guest: eve@example.com / password123"
        ]
        
        for i, sample in enumerate(samples):
            sample_label = ttk.Label(parent, text=sample, font=('Helvetica', 10))
            sample_label.grid(row=6+i, column=0, columnspan=2, sticky=tk.W)
    
    def login(self):
        """Handle the login button click."""
        email = self.email_var.get()
        password = self.password_var.get()
        
        if not email or not password:
            messagebox.showerror("Login Error", "Please enter both email and password")
            return
        
        # Attempt to authenticate
        user = self.controller.library.authenticate_user(email, password)
        
        if user:
            self.controller.login(user)
        else:
            messagebox.showerror("Login Error", "Invalid email or password")
