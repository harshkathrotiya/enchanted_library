
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class DashboardFrame(ttk.Frame):

    def __init__(self, parent, controller):

        super().__init__(parent)
        self.controller = controller

        self.create_dashboard()

    def create_dashboard(self):

        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame, text="Dashboard", style='Title.TLabel')
        title_label.pack(side=tk.LEFT, padx=10)

        from datetime import datetime
        current_time = datetime.now().strftime("%A, %d %B %Y")
        time_label = ttk.Label(header_frame, text=current_time, font=('Helvetica', 12))
        time_label.pack(side=tk.RIGHT, padx=10)

        welcome_frame = ttk.Frame(self)
        welcome_frame.pack(fill=tk.X, pady=(0, 20), padx=10)

        welcome_text = f"Welcome back, {self.controller.current_user.name}!"
        welcome_label = ttk.Label(welcome_frame, text=welcome_text,
                                 font=('Helvetica', 14, 'bold'))
        welcome_label.pack(side=tk.LEFT)

        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.create_user_info_widget(left_column)
        self.create_borrowed_books_widget(left_column)

        self.create_library_stats_widget(right_column)
        self.create_recent_activity_widget(right_column)

        footer_frame = ttk.Frame(self)
        footer_frame.pack(fill=tk.X, pady=20, padx=10)

        actions = [
            ("🔍 Search Books", lambda: self.controller.show_frame('search')),
            ("📚 Borrow Book", lambda: self.controller.show_frame('book_management')),
            ("📋 My Loans", lambda: self.controller.show_frame('lending'))
        ]

        for text, command in actions:
            btn = ttk.Button(footer_frame, text=text, command=command, style='Primary.TButton')
            btn.pack(side=tk.LEFT, padx=10)

    def create_user_info_widget(self, parent):

        frame = ttk.LabelFrame(parent, text="User Profile")
        frame.pack(fill=tk.X, pady=10)

        user = self.controller.current_user

        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=15, pady=15)

        profile_frame = ttk.Frame(info_frame)
        profile_frame.grid(row=0, column=0, rowspan=4, padx=(0, 15))

        profile_icon = ttk.Label(profile_frame, text="👤", font=('Helvetica', 36))
        profile_icon.pack(padx=10, pady=10)

        role_badge = ttk.Label(profile_frame, text=user.get_role().name,
                              font=('Helvetica', 9, 'bold'),
                              background="#6c5ce7", foreground="white")
        role_badge.pack(pady=5)

        details = [
            ("👤", "Name:", user.name),
            ("✉️", "Email:", user.email),
            ("🕒", "Registered:", user.registration_date.strftime('%Y-%m-%d')),
            ("🔑", "Last Login:", user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "Never")
        ]

        for i, (icon, label, value) in enumerate(details):
            row_frame = ttk.Frame(info_frame)
            row_frame.grid(row=i, column=1, sticky=tk.W, pady=3)

            icon_label = ttk.Label(row_frame, text=icon, font=('Helvetica', 12))
            icon_label.pack(side=tk.LEFT, padx=(0, 5))

            label_widget = ttk.Label(row_frame, text=label, font=('Helvetica', 10, 'bold'))
            label_widget.pack(side=tk.LEFT, padx=(0, 5))

            value_widget = ttk.Label(row_frame, text=value, font=('Helvetica', 10))
            value_widget.pack(side=tk.LEFT)

        if user.get_role().name == 'LIBRARIAN':
            librarian_frame = ttk.Frame(info_frame)
            librarian_frame.grid(row=4, column=1, sticky=tk.W, pady=(10, 0))

            department_icon = ttk.Label(librarian_frame, text="🏢", font=('Helvetica', 12))
            department_icon.pack(side=tk.LEFT, padx=(0, 5))

            department_label = ttk.Label(librarian_frame, text="Department:", font=('Helvetica', 10, 'bold'))
            department_label.pack(side=tk.LEFT, padx=(0, 5))

            department_value = ttk.Label(librarian_frame, text=user.department or "N/A", font=('Helvetica', 10))
            department_value.pack(side=tk.LEFT)

            staff_frame = ttk.Frame(info_frame)
            staff_frame.grid(row=5, column=1, sticky=tk.W, pady=(3, 0))

            staff_icon = ttk.Label(staff_frame, text="🔖", font=('Helvetica', 12))
            staff_icon.pack(side=tk.LEFT, padx=(0, 5))

            staff_label = ttk.Label(staff_frame, text="Staff ID:", font=('Helvetica', 10, 'bold'))
            staff_label.pack(side=tk.LEFT, padx=(0, 5))

            staff_value = ttk.Label(staff_frame, text=user.staff_id or "N/A", font=('Helvetica', 10))
            staff_value.pack(side=tk.LEFT)

        elif user.get_role().name == 'SCHOLAR':
            scholar_frame = ttk.Frame(info_frame)
            scholar_frame.grid(row=4, column=1, sticky=tk.W, pady=(10, 0))

            institution_icon = ttk.Label(scholar_frame, text="🏫", font=('Helvetica', 12))
            institution_icon.pack(side=tk.LEFT, padx=(0, 5))

            institution_label = ttk.Label(scholar_frame, text="Institution:", font=('Helvetica', 10, 'bold'))
            institution_label.pack(side=tk.LEFT, padx=(0, 5))

            institution_value = ttk.Label(scholar_frame, text=user.institution or "N/A", font=('Helvetica', 10))
            institution_value.pack(side=tk.LEFT)

            field_frame = ttk.Frame(info_frame)
            field_frame.grid(row=5, column=1, sticky=tk.W, pady=(3, 0))

            field_icon = ttk.Label(field_frame, text="📚", font=('Helvetica', 12))
            field_icon.pack(side=tk.LEFT, padx=(0, 5))

            field_label = ttk.Label(field_frame, text="Field:", font=('Helvetica', 10, 'bold'))
            field_label.pack(side=tk.LEFT, padx=(0, 5))

            field_value = ttk.Label(field_frame, text=user.field_of_study or "N/A", font=('Helvetica', 10))
            field_value.pack(side=tk.LEFT)

        elif user.get_role().name == 'GUEST':
            guest_frame = ttk.Frame(info_frame)
            guest_frame.grid(row=4, column=1, sticky=tk.W, pady=(10, 0))

            membership_icon = ttk.Label(guest_frame, text="🎫", font=('Helvetica', 12))
            membership_icon.pack(side=tk.LEFT, padx=(0, 5))

            membership_label = ttk.Label(guest_frame, text="Membership:", font=('Helvetica', 10, 'bold'))
            membership_label.pack(side=tk.LEFT, padx=(0, 5))

            membership_value = ttk.Label(guest_frame, text=user.membership_type, font=('Helvetica', 10))
            membership_value.pack(side=tk.LEFT)

            expiry_frame = ttk.Frame(info_frame)
            expiry_frame.grid(row=5, column=1, sticky=tk.W, pady=(3, 0))

            expiry_icon = ttk.Label(expiry_frame, text="📅", font=('Helvetica', 12))
            expiry_icon.pack(side=tk.LEFT, padx=(0, 5))

            expiry_label = ttk.Label(expiry_frame, text="Expires:", font=('Helvetica', 10, 'bold'))
            expiry_label.pack(side=tk.LEFT, padx=(0, 5))

            expiry_date = user.membership_expiry.strftime('%Y-%m-%d') if user.membership_expiry else "N/A"
            expiry_value = ttk.Label(expiry_frame, text=expiry_date, font=('Helvetica', 10))
            expiry_value.pack(side=tk.LEFT)

            valid_frame = ttk.Frame(info_frame)
            valid_frame.grid(row=6, column=1, sticky=tk.W, pady=(3, 0))

            is_valid = user.is_membership_valid()
            valid_icon = ttk.Label(valid_frame, text="✅" if is_valid else "❌", font=('Helvetica', 12))
            valid_icon.pack(side=tk.LEFT, padx=(0, 5))

            valid_label = ttk.Label(valid_frame, text="Valid:", font=('Helvetica', 10, 'bold'))
            valid_label.pack(side=tk.LEFT, padx=(0, 5))

            valid_value = ttk.Label(valid_frame, text="Yes" if is_valid else "No",
                                   font=('Helvetica', 10),
                                   foreground="#00b894" if is_valid else "#e17055")
            valid_value.pack(side=tk.LEFT)

    def create_borrowed_books_widget(self, parent):

        frame = ttk.LabelFrame(parent, text="📚 Your Borrowed Books")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)

        borrowed_books = self.controller.library.get_user_borrowed_books(
            self.controller.current_user.user_id)

        if not borrowed_books:
            empty_frame = ttk.Frame(frame)
            empty_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            empty_icon = ttk.Label(empty_frame, text="📖", font=('Helvetica', 24))
            empty_icon.pack(pady=(20, 10))

            empty_label = ttk.Label(empty_frame, text="You have no borrowed books",
                                  font=('Helvetica', 11, 'italic'))
            empty_label.pack(pady=5)

            suggestion_label = ttk.Label(empty_frame,
                                       text="Visit the Books section to borrow some books",
                                       font=('Helvetica', 10))
            suggestion_label.pack(pady=5)

            browse_button = ttk.Button(empty_frame, text="Browse Books",
                                     command=lambda: self.controller.show_frame('book_management'),
                                     style='Primary.TButton')
            browse_button.pack(pady=10)
            return

        container_frame = ttk.Frame(frame)
        container_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header_frame = ttk.Frame(container_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        count_label = ttk.Label(header_frame,
                              text=f"You have {len(borrowed_books)} book{'s' if len(borrowed_books) > 1 else ''} borrowed",
                              font=('Helvetica', 10, 'bold'))
        count_label.pack(side=tk.LEFT)

        view_all_button = ttk.Button(header_frame, text="Manage Loans",
                                   command=lambda: self.controller.show_frame('lending'),
                                   style='Primary.TButton')
        view_all_button.pack(side=tk.RIGHT)

        columns = ('title', 'author', 'due_date', 'status')
        tree = ttk.Treeview(container_frame, columns=columns, show='headings', style='Treeview')

        tree.heading('title', text='Title')
        tree.heading('author', text='Author')
        tree.heading('due_date', text='Due Date')
        tree.heading('status', text='Status')

        tree.column('title', width=200)
        tree.column('author', width=150)
        tree.column('due_date', width=100)
        tree.column('status', width=80)

        y_scrollbar = ttk.Scrollbar(container_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(container_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True)

        for item in borrowed_books:
            book = item['book']
            due_date = item['due_date']
            is_overdue = due_date < datetime.now()
            status = "Overdue" if is_overdue else "On Time"

            days_diff = (due_date - datetime.now()).days
            days_text = f"({abs(days_diff)} days {'overdue' if days_diff < 0 else 'remaining'})"

            tag = 'overdue' if is_overdue else 'ontime'
            tree.insert('', tk.END, values=(
                book.title,
                book.author,
                f"{due_date.strftime('%Y-%m-%d')} {days_text}",
                status
            ), tags=(tag,))

        tree.tag_configure('overdue', foreground='#e17055')
        tree.tag_configure('ontime', foreground='#00b894')

        tree.bind("<Double-1>", lambda event: self.view_book_details(tree))

    def view_book_details(self, tree):
        
        selection = tree.selection()
        if not selection:
            return

        book_title = tree.item(selection[0], 'values')[0]

        for book_id, book in self.controller.catalog._books.items():
            if book.title == book_title:
                messagebox.showinfo("Book Details",
                                  f"Title: {book.title}\n"
                                  f"Author: {book.author}\n"
                                  f"Year: {book.year_published}\n"
                                  f"Status: {book.status.name}\n"
                                  f"Condition: {book.condition.name}")
                break

    def create_library_stats_widget(self, parent):

        frame = ttk.LabelFrame(parent, text="📊 Library Statistics")
        frame.pack(fill=tk.X, pady=10)

        container_frame = ttk.Frame(frame)
        container_frame.pack(fill=tk.X, padx=15, pady=15)

        total_books = len(self.controller.catalog._books)
        available_books = sum(1 for book in self.controller.catalog._books.values()
                             if book.status.name == 'AVAILABLE')
        borrowed_books = total_books - available_books
        total_users = len(self.controller.catalog._users)

        available_percent = (available_books / total_books * 100) if total_books > 0 else 0
        borrowed_percent = (borrowed_books / total_books * 100) if total_books > 0 else 0

        stats_grid = ttk.Frame(container_frame)
        stats_grid.pack(fill=tk.X, pady=10)

        stats = [
            ("📚", "Total Books", str(total_books)),
            ("✅", "Available", f"{available_books} ({available_percent:.1f}%)"),
            ("🔄", "Borrowed", f"{borrowed_books} ({borrowed_percent:.1f}%)"),
            ("👥", "Total Users", str(total_users))
        ]

        for i, (icon, label, value) in enumerate(stats):
            stat_frame = ttk.Frame(stats_grid, relief="solid", borderwidth=1)
            stat_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky=tk.NSEW)

            icon_label = ttk.Label(stat_frame, text=icon, font=('Helvetica', 24))
            icon_label.pack(pady=(10, 5))

            label_widget = ttk.Label(stat_frame, text=label, font=('Helvetica', 10, 'bold'))
            label_widget.pack()

            value_widget = ttk.Label(stat_frame, text=value, font=('Helvetica', 14))
            value_widget.pack(pady=(5, 10))

        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)

        visual_frame = ttk.Frame(container_frame)
        visual_frame.pack(fill=tk.X, pady=10)

        visual_title = ttk.Label(visual_frame, text="Book Availability", font=('Helvetica', 10, 'bold'))
        visual_title.pack(anchor=tk.W, pady=(0, 5))

        progress_frame = ttk.Frame(visual_frame, height=20)
        progress_frame.pack(fill=tk.X)

        available_bar = tk.Frame(progress_frame, width=int(available_percent*2), height=20, bg="#00b894")
        available_bar.pack(side=tk.LEFT)

        borrowed_bar = tk.Frame(progress_frame, width=int(borrowed_percent*2), height=20, bg="#fdcb6e")
        borrowed_bar.pack(side=tk.LEFT)

        legend_frame = ttk.Frame(visual_frame)
        legend_frame.pack(fill=tk.X, pady=5)

        available_legend = tk.Frame(legend_frame, width=10, height=10, bg="#00b894")
        available_legend.pack(side=tk.LEFT, padx=(0, 5))

        available_text = ttk.Label(legend_frame, text="Available", font=('Helvetica', 8))
        available_text.pack(side=tk.LEFT, padx=(0, 15))

        borrowed_legend = tk.Frame(legend_frame, width=10, height=10, bg="#fdcb6e")
        borrowed_legend.pack(side=tk.LEFT, padx=(0, 5))

        borrowed_text = ttk.Label(legend_frame, text="Borrowed", font=('Helvetica', 8))
        borrowed_text.pack(side=tk.LEFT)

    def create_recent_activity_widget(self, parent):

        frame = ttk.LabelFrame(parent, text="🔔 Recent Activity")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)

        events = self.controller.event_manager.events[-10:] if self.controller.event_manager.events else []

        if not events:
            empty_frame = ttk.Frame(frame)
            empty_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            empty_icon = ttk.Label(empty_frame, text="🔕", font=('Helvetica', 24))
            empty_icon.pack(pady=(20, 10))

            empty_label = ttk.Label(empty_frame, text="No recent activity",
                                  font=('Helvetica', 11, 'italic'))
            empty_label.pack(pady=5)

            return

        container_frame = ttk.Frame(frame)
        container_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header_frame = ttk.Frame(container_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        count_label = ttk.Label(header_frame,
                              text=f"Showing {len(events)} recent events",
                              font=('Helvetica', 10, 'bold'))
        count_label.pack(side=tk.LEFT)

        activity_canvas = tk.Canvas(container_frame, highlightthickness=0)
        activity_frame = ttk.Frame(activity_canvas)

        scrollbar = ttk.Scrollbar(container_frame, orient=tk.VERTICAL, command=activity_canvas.yview)
        activity_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        activity_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_window = activity_canvas.create_window((0, 0), window=activity_frame, anchor=tk.NW)

        def configure_canvas(event):
            activity_canvas.itemconfig(canvas_window, width=event.width)
        activity_canvas.bind('<Configure>', configure_canvas)

        def configure_scroll_region(event):
            activity_canvas.configure(scrollregion=activity_canvas.bbox("all"))
        activity_frame.bind('<Configure>', configure_scroll_region)

        event_icons = {
            'book_borrowed': '📚',
            'book_returned': '🔙',
            'book_added': '➕',
            'book_needs_restoration': '🔧',
            'user_added': '👤',
            'default': '📝'
        }

        for i, event in enumerate(reversed(events)):
            event_frame = ttk.Frame(activity_frame)
            event_frame.pack(fill=tk.X, pady=5)

            if i > 0:
                separator = ttk.Separator(event_frame, orient='horizontal')
                separator.pack(fill=tk.X, pady=(0, 5))

            content_frame = ttk.Frame(event_frame)
            content_frame.pack(fill=tk.X, padx=5, pady=5)

            event_time = event.timestamp.strftime('%Y-%m-%d %H:%M')
            event_type = event.event_type.replace('_', ' ').title()

            icon = event_icons.get(event.event_type, event_icons['default'])

            icon_label = ttk.Label(content_frame, text=icon, font=('Helvetica', 16))
            icon_label.pack(side=tk.LEFT, padx=(0, 10))

            text_frame = ttk.Frame(content_frame)
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            if event.event_type == 'book_borrowed':
                title = event.data.get('title', 'Unknown')
                user = event.data.get('user_name', 'Unknown')

                type_label = ttk.Label(text_frame, text=event_type, font=('Helvetica', 10, 'bold'))
                type_label.pack(anchor=tk.W)

                details_label = ttk.Label(text_frame,
                                        text=f"'{title}' borrowed by {user}",
                                        font=('Helvetica', 9))
                details_label.pack(anchor=tk.W)

            elif event.event_type == 'book_returned':
                title = event.data.get('title', 'Unknown')
                user = event.data.get('user_name', 'Unknown')

                type_label = ttk.Label(text_frame, text=event_type, font=('Helvetica', 10, 'bold'))
                type_label.pack(anchor=tk.W)

                details_label = ttk.Label(text_frame,
                                        text=f"'{title}' returned by {user}",
                                        font=('Helvetica', 9))
                details_label.pack(anchor=tk.W)

            elif event.event_type == 'book_added':
                title = event.data.get('title', 'Unknown')
                author = event.data.get('author', 'Unknown')

                type_label = ttk.Label(text_frame, text=event_type, font=('Helvetica', 10, 'bold'))
                type_label.pack(anchor=tk.W)

                details_label = ttk.Label(text_frame,
                                        text=f"'{title}' by {author}",
                                        font=('Helvetica', 9))
                details_label.pack(anchor=tk.W)

            else:
                type_label = ttk.Label(text_frame, text=event_type, font=('Helvetica', 10, 'bold'))
                type_label.pack(anchor=tk.W)

            time_label = ttk.Label(content_frame, text=event_time, font=('Helvetica', 8))
            time_label.pack(side=tk.RIGHT)

    def update_frame(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.create_dashboard()
