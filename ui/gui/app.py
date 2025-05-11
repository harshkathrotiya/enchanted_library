
import tkinter as tk
from tkinter import ttk, messagebox

from ui.gui.login_frame import LoginFrame
from ui.gui.dashboard_frame import DashboardFrame
from ui.gui.book_management_frame import BookManagementFrame
from ui.gui.user_management_frame import UserManagementFrame
from ui.gui.lending_frame import LendingFrame
from ui.gui.search_frame import SearchFrame
from ui.gui.preservation_frame import PreservationFrame
from ui.gui.section_management_frame import SectionManagementFrame
from ui.gui.financial_frame import FinancialFrame
from ui.gui.book_modification_frame import BookModificationFrame
from ui.gui.data_persistence_frame import DataPersistenceFrame
from ui.gui.recommendation_frame import RecommendationFrame

class EnchantedLibraryApp:

    def __init__(self, library, catalog, event_manager):

        self.library = library
        self.catalog = catalog
        self.event_manager = event_manager
        self.current_user = None

        from services.preservation import PreservationService
        from services.fee_calculator import FeeCalculator

        self.preservation_service = PreservationService(catalog, event_manager)
        self.fee_calculator = FeeCalculator()

        self.root = tk.Tk()
        self.root.title("Enchanted Library")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.configure_styles()

        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ttk.Frame(self.main_container, style='Sidebar.TFrame', width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)

        self.content = ttk.Frame(self.main_container)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.frames = {}
        self.current_frame = None

        self.frames['login'] = LoginFrame(self.content, self)

        self.show_frame('login')

    def configure_styles(self):

        bg_color = "#f8f9fa"
        content_bg = "#ffffff"
        sidebar_bg = "#343a40"
        sidebar_fg = "#f8f9fa"
        accent_color = "#6c5ce7"
        accent_light = "#a29bfe"
        button_bg = "#6c5ce7"
        button_fg = "#ffffff"
        success_color = "#00b894"
        warning_color = "#fdcb6e"
        error_color = "#e17055"

        self.style.configure('Sidebar.TFrame', background=sidebar_bg)
        self.style.configure('Content.TFrame', background=content_bg)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TNotebook', background=bg_color)
        self.style.configure('TNotebook.Tab', background=bg_color, padding=[10, 5], font=('Helvetica', 10))
        self.style.map('TNotebook.Tab',
                      background=[('selected', accent_color)],
                      foreground=[('selected', '#ffffff')])

        self.style.configure('Nav.TButton',
                            background=sidebar_bg,
                            foreground=sidebar_fg,
                            borderwidth=0,
                            font=('Helvetica', 12),
                            padding=10)

        self.style.map('Nav.TButton',
                      background=[('active', accent_color)],
                      foreground=[('active', '#ffffff')])

        self.style.configure('Primary.TButton',
                            background=button_bg,
                            foreground=button_fg,
                            font=('Helvetica', 11),
                            padding=8)

        self.style.map('Primary.TButton',
                      background=[('active', accent_light)],
                      foreground=[('active', '#ffffff')])

        self.style.configure('Success.TButton',
                            background=success_color,
                            foreground='#ffffff',
                            font=('Helvetica', 11),
                            padding=8)

        self.style.configure('Warning.TButton',
                            background=warning_color,
                            foreground='#333333',
                            font=('Helvetica', 11),
                            padding=8)

        self.style.configure('Error.TButton',
                            background=error_color,
                            foreground='#ffffff',
                            font=('Helvetica', 11),
                            padding=8)

        self.style.configure('Title.TLabel',
                            font=('Helvetica', 18, 'bold'),
                            foreground=accent_color,
                            padding=10)

        self.style.configure('Subtitle.TLabel',
                            font=('Helvetica', 14),
                            padding=5)

        self.style.configure('Sidebar.TLabel',
                            background=sidebar_bg,
                            foreground=sidebar_fg,
                            font=('Helvetica', 14, 'bold'),
                            padding=10)

        self.style.configure('Success.TLabel',
                            foreground=success_color,
                            font=('Helvetica', 11))

        self.style.configure('Warning.TLabel',
                            foreground=warning_color,
                            font=('Helvetica', 11))

        self.style.configure('Error.TLabel',
                            foreground=error_color,
                            font=('Helvetica', 11))

        self.style.configure('Treeview',
                            background=content_bg,
                            fieldbackground=content_bg,
                            font=('Helvetica', 10))

        self.style.configure('Treeview.Heading',
                            background=bg_color,
                            font=('Helvetica', 11, 'bold'))

    def create_sidebar(self):

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        logo_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        logo_frame.pack(fill=tk.X, pady=(20, 5))

        logo_label = ttk.Label(logo_frame, text="Enchanted",
                              style='Sidebar.TLabel', anchor=tk.CENTER)
        logo_label.pack(fill=tk.X)

        logo_label2 = ttk.Label(logo_frame, text="Library",
                               style='Sidebar.TLabel', anchor=tk.CENTER)
        logo_label2.pack(fill=tk.X, pady=(0, 10))

        separator = ttk.Separator(self.sidebar, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)

        nav_buttons = [
            ("🏠 Dashboard", lambda: self.show_frame('dashboard')),
            ("🔍 Search", lambda: self.show_frame('search')),
            ("📚 Books", lambda: self.show_frame('book_management')),
            ("📋 Lending", lambda: self.show_frame('lending')),
            ("📊 Recommendations", lambda: self.show_frame('recommendation'))
        ]

        if self.current_user and self.current_user.get_role().name == 'LIBRARIAN':
            nav_buttons.append(("👥 Users", lambda: self.show_frame('user_management')))
            nav_buttons.append(("🔧 Preservation", lambda: self.show_frame('preservation')))
            nav_buttons.append(("📂 Sections", lambda: self.show_frame('section_management')))
            nav_buttons.append(("💰 Finances", lambda: self.show_frame('financial')))
            nav_buttons.append(("💾 Data", lambda: self.show_frame('data_persistence')))

        buttons_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        for text, command in nav_buttons:
            btn = ttk.Button(buttons_frame, text=text, command=command, style='Nav.TButton')
            btn.pack(fill=tk.X, pady=3, padx=5)

            self.create_tooltip(btn, f"Go to {text.split(' ')[1]}")

        ttk.Frame(self.sidebar, style='Sidebar.TFrame').pack(fill=tk.Y, expand=True)

        if self.current_user:
            separator2 = ttk.Separator(self.sidebar, orient='horizontal')
            separator2.pack(fill=tk.X, padx=20, pady=10)

            user_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
            user_frame.pack(fill=tk.X, padx=10, pady=5)

            user_icon = ttk.Label(user_frame, text="👤",
                                 style='Sidebar.TLabel', font=('Helvetica', 16))
            user_icon.pack(pady=(5, 0))

            user_name = ttk.Label(user_frame,
                                 text=f"{self.current_user.name}",
                                 style='Sidebar.TLabel',
                                 anchor=tk.CENTER)
            user_name.pack(fill=tk.X)

            user_role = ttk.Label(user_frame,
                                 text=f"({self.current_user.get_role().name})",
                                 style='Sidebar.TLabel',
                                 font=('Helvetica', 10),
                                 anchor=tk.CENTER)
            user_role.pack(fill=tk.X, pady=(0, 10))

            logout_btn = ttk.Button(user_frame, text="🚪 Logout",
                                   command=self.logout, style='Nav.TButton')
            logout_btn.pack(fill=tk.X, pady=(5, 10))

    def create_tooltip(self, widget, text):

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25

            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = ttk.Label(self.tooltip, text=text,
                             background="#ffffe0", relief="solid", borderwidth=1,
                             font=("Helvetica", 10), padding=2)
            label.pack()

        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def show_frame(self, frame_name):

        if self.current_frame:
            self.current_frame.pack_forget()

        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.current_frame, 'update_frame'):
            self.current_frame.update_frame()

    def refresh_all_frames(self):

        for frame_name, frame in self.frames.items():
            if hasattr(frame, 'update_frame'):
                try:
                    frame.update_frame()
                except Exception as e:
                    print(f"Error updating frame {frame_name}: {str(e)}")

        if self.current_frame:
            self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_book_details(self, book_id):

        self.show_frame('book_management')

        book_management_frame = self.frames['book_management']

        notebook = book_management_frame.winfo_children()[0]

        if hasattr(notebook, 'select'):
            notebook.select(2)

        book_details_frame = notebook.winfo_children()[2]

        for child in book_details_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.Entry) and hasattr(grandchild, 'var'):
                        grandchild.var.set(book_id)
                        break

        for child in book_details_frame.winfo_children():
            if isinstance(child, ttk.Button) and child.cget('text') == "Load Book Details":
                child.invoke()
                break

    def login(self, user):

        self.current_user = user

        self.frames['dashboard'] = DashboardFrame(self.content, self)
        self.frames['book_management'] = BookManagementFrame(self.content, self)
        self.frames['user_management'] = UserManagementFrame(self.content, self)
        self.frames['lending'] = LendingFrame(self.content, self)
        self.frames['search'] = SearchFrame(self.content, self)
        self.frames['preservation'] = PreservationFrame(self.content, self)
        self.frames['section_management'] = SectionManagementFrame(self.content, self)
        self.frames['financial'] = FinancialFrame(self.content, self)
        self.frames['data_persistence'] = DataPersistenceFrame(self.content, self)
        self.frames['recommendation'] = RecommendationFrame(self.content, self)

        self.create_sidebar()

        self.show_frame('dashboard')

    def logout(self):

        self.current_user = None

        for frame_name in list(self.frames.keys()):
            if frame_name != 'login':
                del self.frames[frame_name]

        for widget in self.sidebar.winfo_children():
            widget.destroy()

        self.show_frame('login')

    def run(self):

        self.root.mainloop()

def launch_gui(library, catalog, event_manager):

    app = EnchantedLibraryApp(library, catalog, event_manager)
    app.run()
