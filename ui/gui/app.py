"""
Main GUI application for the Enchanted Library system.
This module provides the main application window and navigation.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from ui.gui.login_frame import LoginFrame
from ui.gui.dashboard_frame import DashboardFrame
from ui.gui.book_management_frame import BookManagementFrame
from ui.gui.user_management_frame import UserManagementFrame
from ui.gui.lending_frame import LendingFrame
from ui.gui.search_frame import SearchFrame


class EnchantedLibraryApp:
    """Main application class for the Enchanted Library GUI."""
    
    def __init__(self, library, catalog, event_manager):
        """
        Initialize the main application.
        
        Args:
            library: The library facade
            catalog: The library catalog
            event_manager: The event manager
        """
        self.library = library
        self.catalog = catalog
        self.event_manager = event_manager
        self.current_user = None
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Enchanted Library")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Set the theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a modern theme
        
        # Configure styles
        self.configure_styles()
        
        # Create the main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create the navigation sidebar
        self.sidebar = ttk.Frame(self.main_container, style='Sidebar.TFrame', width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        # Create the content area
        self.content = ttk.Frame(self.main_container)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize frames
        self.frames = {}
        self.current_frame = None
        
        # Create the login frame first
        self.frames['login'] = LoginFrame(self.content, self)
        
        # Other frames will be created after login
        
        # Start with the login frame
        self.show_frame('login')
    
    def configure_styles(self):
        """Configure custom styles for the application."""
        # Configure colors
        bg_color = "#f0f0f0"
        sidebar_bg = "#2c3e50"
        sidebar_fg = "#ecf0f1"
        button_bg = "#3498db"
        button_fg = "#ffffff"
        
        # Configure frame styles
        self.style.configure('Sidebar.TFrame', background=sidebar_bg)
        self.style.configure('Content.TFrame', background=bg_color)
        
        # Configure button styles
        self.style.configure('Nav.TButton', 
                            background=sidebar_bg, 
                            foreground=sidebar_fg,
                            borderwidth=0,
                            font=('Helvetica', 12),
                            padding=10)
        
        self.style.map('Nav.TButton',
                      background=[('active', '#34495e')],
                      foreground=[('active', '#ffffff')])
        
        # Configure label styles
        self.style.configure('Title.TLabel', 
                            font=('Helvetica', 16, 'bold'),
                            padding=10)
        
        self.style.configure('Sidebar.TLabel', 
                            background=sidebar_bg,
                            foreground=sidebar_fg,
                            font=('Helvetica', 14, 'bold'),
                            padding=10)
    
    def create_sidebar(self):
        """Create the navigation sidebar."""
        # Clear existing widgets
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        
        # Add library logo/title
        logo_label = ttk.Label(self.sidebar, text="Enchanted\nLibrary", 
                              style='Sidebar.TLabel', anchor=tk.CENTER)
        logo_label.pack(fill=tk.X, pady=(20, 30))
        
        # Add navigation buttons
        nav_buttons = [
            ("Dashboard", lambda: self.show_frame('dashboard')),
            ("Search", lambda: self.show_frame('search')),
            ("Books", lambda: self.show_frame('book_management')),
            ("Lending", lambda: self.show_frame('lending'))
        ]
        
        # Add user management button for librarians
        if self.current_user and self.current_user.get_role().name == 'LIBRARIAN':
            nav_buttons.append(("Users", lambda: self.show_frame('user_management')))
        
        # Create the buttons
        for text, command in nav_buttons:
            btn = ttk.Button(self.sidebar, text=text, command=command, style='Nav.TButton')
            btn.pack(fill=tk.X, pady=2)
        
        # Add spacer
        ttk.Frame(self.sidebar, style='Sidebar.TFrame').pack(fill=tk.Y, expand=True)
        
        # Add user info and logout button
        if self.current_user:
            user_label = ttk.Label(self.sidebar, 
                                  text=f"{self.current_user.name}\n({self.current_user.get_role().name})", 
                                  style='Sidebar.TLabel',
                                  anchor=tk.CENTER)
            user_label.pack(fill=tk.X)
            
            logout_btn = ttk.Button(self.sidebar, text="Logout", 
                                   command=self.logout, style='Nav.TButton')
            logout_btn.pack(fill=tk.X, pady=(2, 20))
    
    def show_frame(self, frame_name):
        """
        Show the specified frame.
        
        Args:
            frame_name (str): Name of the frame to show
        """
        # Hide current frame
        if self.current_frame:
            self.current_frame.pack_forget()
        
        # Show the requested frame
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update the frame if it has an update method
        if hasattr(self.current_frame, 'update_frame'):
            self.current_frame.update_frame()
    
    def login(self, user):
        """
        Handle user login.
        
        Args:
            user: The authenticated user
        """
        self.current_user = user
        
        # Create the other frames now that we're logged in
        self.frames['dashboard'] = DashboardFrame(self.content, self)
        self.frames['book_management'] = BookManagementFrame(self.content, self)
        self.frames['user_management'] = UserManagementFrame(self.content, self)
        self.frames['lending'] = LendingFrame(self.content, self)
        self.frames['search'] = SearchFrame(self.content, self)
        
        # Create the sidebar
        self.create_sidebar()
        
        # Show the dashboard
        self.show_frame('dashboard')
    
    def logout(self):
        """Handle user logout."""
        self.current_user = None
        
        # Remove all frames except login
        for frame_name in list(self.frames.keys()):
            if frame_name != 'login':
                del self.frames[frame_name]
        
        # Clear the sidebar
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        
        # Show the login frame
        self.show_frame('login')
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def launch_gui(library, catalog, event_manager):
    """
    Launch the GUI application.
    
    Args:
        library: The library facade
        catalog: The library catalog
        event_manager: The event manager
    """
    app = EnchantedLibraryApp(library, catalog, event_manager)
    app.run()
