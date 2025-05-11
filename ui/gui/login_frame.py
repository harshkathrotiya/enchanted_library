
import tkinter as tk
from tkinter import ttk, messagebox

class LoginFrame(ttk.Frame):

    def __init__(self, parent, controller):

        super().__init__(parent)
        self.controller = controller

        bg_frame = ttk.Frame(self)
        bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        header_frame = ttk.Frame(bg_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        banner_frame = ttk.Frame(header_frame, style='TFrame', height=120)
        banner_frame.pack(fill=tk.X)

        banner_label = ttk.Label(banner_frame, text="📚", font=('Helvetica', 48))
        banner_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        card_frame = ttk.Frame(bg_frame, style='TFrame')
        card_frame.pack(padx=50, pady=20)

        inner_frame = ttk.Frame(card_frame)
        inner_frame.pack(padx=30, pady=30)

        self.create_login_form(inner_frame)

    def create_login_form(self, parent):

        title_label = ttk.Label(parent, text="Enchanted Library",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

        subtitle_label = ttk.Label(parent, text="Please login to continue",
                                  style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))

        form_frame = ttk.Frame(parent)
        form_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)

        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill=tk.X, pady=5)

        email_icon = ttk.Label(email_frame, text="✉️", font=('Helvetica', 14))
        email_icon.pack(side=tk.LEFT, padx=(0, 10))

        email_label = ttk.Label(email_frame, text="Email:", font=('Helvetica', 12))
        email_label.pack(side=tk.LEFT, padx=(0, 5))

        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.email_var, width=30, font=('Helvetica', 12))
        email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=tk.X, pady=5)

        password_icon = ttk.Label(password_frame, text="🔒", font=('Helvetica', 14))
        password_icon.pack(side=tk.LEFT, padx=(0, 10))

        password_label = ttk.Label(password_frame, text="Password:", font=('Helvetica', 12))
        password_label.pack(side=tk.LEFT, padx=(0, 5))

        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var,
                                  show="•", width=30, font=('Helvetica', 12))
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        login_button = ttk.Button(button_frame, text="Login", command=self.login,
                                 style='Primary.TButton', width=20)
        login_button.pack()

        separator = ttk.Separator(parent, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=20)

        creds_frame = ttk.LabelFrame(parent, text="Sample Credentials")
        creds_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)

        samples = [
            ("Librarian", "aarav@library.com", "password123"),
            ("Scholar", "vikram@university.edu", "password123"),
            ("Guest", "arjun@example.com", "password123")
        ]

        for i, (role, email, password) in enumerate(samples):
            role_label = ttk.Label(creds_frame, text=role, font=('Helvetica', 10, 'bold'))
            role_label.grid(row=i, column=0, padx=5, pady=3, sticky=tk.W)

            email_label = ttk.Label(creds_frame, text=email, font=('Helvetica', 10))
            email_label.grid(row=i, column=1, padx=5, pady=3, sticky=tk.W)

            password_label = ttk.Label(creds_frame, text=password, font=('Helvetica', 10))
            password_label.grid(row=i, column=2, padx=5, pady=3, sticky=tk.W)

        parent.bind('<Return>', lambda event: self.login())

    def login(self):

        email = self.email_var.get()
        password = self.password_var.get()

        if not email or not password:
            messagebox.showerror("Login Error", "Please enter both email and password")
            return

        user = self.controller.library.authenticate_user(email, password)

        if user:
            self.controller.login(user)
        else:
            messagebox.showerror("Login Error", "Invalid email or password")
