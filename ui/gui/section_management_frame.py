import tkinter as tk
from tkinter import ttk, messagebox
import uuid

from security.access_control import AccessLevel

class SectionManagementFrame(ttk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.create_section_management()

    def create_section_management(self):

        title_label = ttk.Label(self, text="Section Management", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        if not self.controller.current_user or self.controller.current_user.get_role().name != 'LIBRARIAN':
            ttk.Label(self, text="Only librarians can access section management",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        section_list_frame = ttk.Frame(notebook)
        add_section_frame = ttk.Frame(notebook)
        assign_books_frame = ttk.Frame(notebook)

        notebook.add(section_list_frame, text="Section List")
        notebook.add(add_section_frame, text="Add/Edit Section")
        notebook.add(assign_books_frame, text="Assign Books")

        self.create_section_list(section_list_frame)
        self.create_add_section_form(add_section_frame)
        self.create_assign_books(assign_books_frame)

    def create_section_list(self, parent):

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        columns = ('id', 'name', 'description', 'access_level', 'book_count')
        self.section_tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.section_tree.heading('id', text='ID')
        self.section_tree.heading('name', text='Name')
        self.section_tree.heading('description', text='Description')
        self.section_tree.heading('access_level', text='Access Level')
        self.section_tree.heading('book_count', text='Books')

        self.section_tree.column('id', width=250)
        self.section_tree.column('name', width=150)
        self.section_tree.column('description', width=250)
        self.section_tree.column('access_level', width=100)
        self.section_tree.column('book_count', width=50)

        y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.section_tree.yview)
        self.section_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.section_tree.xview)
        self.section_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.section_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        refresh_button = ttk.Button(button_frame, text="Refresh",
                                  command=self.populate_section_list,
                                  style='Primary.TButton')
        refresh_button.pack(side=tk.LEFT, padx=5)

        edit_button = ttk.Button(button_frame, text="Edit Section",
                               command=self.edit_section)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text="Delete Section",
                                 command=self.delete_section,
                                 style='Error.TButton')
        delete_button.pack(side=tk.LEFT, padx=5)

        self.section_tree.bind("<Double-1>", lambda event: self.edit_section())

        self.populate_section_list()

    def populate_section_list(self):

        for item in self.section_tree.get_children():
            self.section_tree.delete(item)

        for section_id, section in self.controller.catalog._sections.items():
            book_count = len(section['books'])

            access_level_name = "Public"
            if section['access_level'] == 1:
                access_level_name = "Restricted"
            elif section['access_level'] == 2:
                access_level_name = "Highly Restricted"

            self.section_tree.insert('', tk.END, values=(
                section_id,
                section['name'],
                section['description'],
                access_level_name,
                book_count
            ))

    def create_add_section_form(self, parent):

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.section_id_var = tk.StringVar()

        ttk.Label(frame, text="Section Name:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.section_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.section_name_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Description:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.section_desc_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.section_desc_var, width=50).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Access Level:", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.access_level_var = tk.IntVar(value=0)
        access_levels = [
            (0, "Public", "Available to all users"),
            (1, "Restricted", "Available to librarians and qualified scholars"),
            (2, "Highly Restricted", "Available only to senior librarians")
        ]

        access_frame = ttk.Frame(frame)
        access_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        for i, (level, text, desc) in enumerate(access_levels):
            level_frame = ttk.Frame(access_frame)
            level_frame.pack(fill=tk.X, pady=2)

            ttk.Radiobutton(level_frame, text=text, variable=self.access_level_var,
                          value=level).pack(side=tk.LEFT)

            ttk.Label(level_frame, text=f" - {desc}",
                     font=('Helvetica', 9, 'italic')).pack(side=tk.LEFT)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        self.save_button = ttk.Button(button_frame, text="Add Section",
                                    command=self.save_section,
                                    style='Primary.TButton')
        self.save_button.pack(side=tk.LEFT, padx=5)

        clear_button = ttk.Button(button_frame, text="Clear Form",
                                command=self.clear_section_form)
        clear_button.pack(side=tk.LEFT, padx=5)

    def create_assign_books(self, parent):

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select Section:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.assign_section_var = tk.StringVar()
        self.section_combo = ttk.Combobox(frame, textvariable=self.assign_section_var, width=30)
        self.section_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        books_frame = ttk.Frame(frame)
        books_frame.grid(row=4, column=0, columnspan=4, sticky=tk.NSEW, padx=5, pady=5)

        columns = ('id', 'title', 'author', 'type', 'status')
        self.section_books_tree = ttk.Treeview(books_frame, columns=columns, show='headings')

        refresh_button = ttk.Button(frame, text="↻", width=3,
                                  command=self.update_section_combo)
        refresh_button.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Select Book:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.assign_book_var = tk.StringVar()
        self.book_combo = ttk.Combobox(frame, textvariable=self.assign_book_var, width=50)
        self.book_combo.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)

        refresh_button = ttk.Button(frame, text="↻", width=3,
                                  command=self.update_book_combo)
        refresh_button.grid(row=1, column=3, padx=5, pady=5)

        assign_button = ttk.Button(frame, text="Assign Book to Section",
                                 command=self.assign_book_to_section,
                                 style='Primary.TButton')
        assign_button.grid(row=2, column=0, columnspan=4, pady=20)

        ttk.Label(frame, text="Books in Selected Section:",
                 font=('Helvetica', 12, 'bold')).grid(
            row=3, column=0, columnspan=4, sticky=tk.W, padx=5, pady=(20, 5))

        frame.rowconfigure(4, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

        self.section_books_tree.heading('id', text='ID')
        self.section_books_tree.heading('title', text='Title')
        self.section_books_tree.heading('author', text='Author')
        self.section_books_tree.heading('type', text='Type')
        self.section_books_tree.heading('status', text='Status')

        self.section_books_tree.column('id', width=250)
        self.section_books_tree.column('title', width=200)
        self.section_books_tree.column('author', width=150)
        self.section_books_tree.column('type', width=100)
        self.section_books_tree.column('status', width=100)

        y_scrollbar = ttk.Scrollbar(books_frame, orient=tk.VERTICAL, command=self.section_books_tree.yview)
        self.section_books_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(books_frame, orient=tk.HORIZONTAL, command=self.section_books_tree.xview)
        self.section_books_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.section_books_tree.pack(fill=tk.BOTH, expand=True)

        remove_button = ttk.Button(frame, text="Remove Book from Section",
                                 command=self.remove_book_from_section,
                                 style='Error.TButton')
        remove_button.grid(row=5, column=0, columnspan=4, pady=10)

        self.section_combo.bind("<<ComboboxSelected>>", lambda _: self.update_section_books())

        self.update_book_combo()
        self.update_section_combo()

    def edit_section(self):

        selection = self.section_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a section to edit")
            return

        section_id = self.section_tree.item(selection[0], 'values')[0]
        section = self.controller.catalog.get_section(section_id)

        if not section:
            messagebox.showerror("Error", "Section not found")
            return

        self.section_id_var.set(section_id)
        self.section_name_var.set(section['name'])
        self.section_desc_var.set(section['description'])
        self.access_level_var.set(section['access_level'])

        self.save_button.configure(text="Save Changes")

        parent_widget = self.nametowidget(self.winfo_parent())
        if hasattr(parent_widget, 'select'):
            parent_widget.select(1)

    def delete_section(self):

        selection = self.section_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a section to delete")
            return

        section_id = self.section_tree.item(selection[0], 'values')[0]
        section = self.controller.catalog.get_section(section_id)

        if not section:
            messagebox.showerror("Error", "Section not found")
            return

        if section['books']:
            if not messagebox.askyesno("Warning",
                                     f"Section '{section['name']}' contains {len(section['books'])} books. "
                                     f"Deleting this section will remove these books from the section, "
                                     f"but not from the catalog. Continue?"):
                return

        if section_id in self.controller.catalog._sections:
            del self.controller.catalog._sections[section_id]
            messagebox.showinfo("Success", f"Section '{section['name']}' deleted successfully")

            self.populate_section_list()
            self.update_section_combo()
        else:
            messagebox.showerror("Error", "Failed to delete section")

    def save_section(self):

        section_id = self.section_id_var.get()
        name = self.section_name_var.get()
        description = self.section_desc_var.get()
        access_level = self.access_level_var.get()

        if not name:
            messagebox.showerror("Error", "Section name is required")
            return

        if section_id:
            section = self.controller.catalog.get_section(section_id)
            if not section:
                messagebox.showerror("Error", "Section not found")
                return

            section['name'] = name
            section['description'] = description
            section['access_level'] = access_level

            messagebox.showinfo("Success", f"Section '{name}' updated successfully")
        else: 
            for section in self.controller.catalog._sections.values():
                if section['name'].lower() == name.lower():
                    messagebox.showerror("Error", f"Section name '{name}' already exists")
                    return

            section_id = self.controller.catalog.add_section(name, description, access_level)

            if section_id:
                messagebox.showinfo("Success", f"Section '{name}' added successfully")
            else:
                messagebox.showerror("Error", "Failed to add section")

        self.clear_section_form()

        self.populate_section_list()
        self.update_section_combo()

    def clear_section_form(self):

        self.section_id_var.set("")
        self.section_name_var.set("")
        self.section_desc_var.set("")
        self.access_level_var.set(0)

        self.save_button.configure(text="Add Section")

    def update_section_combo(self):

        sections = list(self.controller.catalog._sections.values())

        self.section_combo['values'] = [f"{section['name']} ({section['id']})" for section in sections]

        self.assign_section_var.set("")

        if hasattr(self, 'section_books_tree') and self.section_books_tree.winfo_exists():
            for item in self.section_books_tree.get_children():
                self.section_books_tree.delete(item)

    def update_book_combo(self):

        books = list(self.controller.catalog._books.values())

        self.book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

        self.assign_book_var.set("")

    def update_section_books(self):

        for item in self.section_books_tree.get_children():
            self.section_books_tree.delete(item)

        section_selection = self.assign_section_var.get()
        if not section_selection:
            return

        section_id = section_selection.split('(')[-1].split(')')[0]
        section = self.controller.catalog.get_section(section_id)

        if not section:
            return

        for book_id in section['books']:
            book = self.controller.catalog.get_book(book_id)
            if not book:
                continue

            from models.book import GeneralBook, RareBook, AncientScript
            if isinstance(book, GeneralBook):
                book_type = "General"
            elif isinstance(book, RareBook):
                book_type = "Rare"
            elif isinstance(book, AncientScript):
                book_type = "Ancient"
            else:
                book_type = "Unknown"

            self.section_books_tree.insert('', tk.END, values=(
                book.book_id,
                book.title,
                book.author,
                book_type,
                book.status.name
            ))

    def assign_book_to_section(self):

        section_selection = self.assign_section_var.get()
        if not section_selection:
            messagebox.showerror("Error", "Please select a section")
            return

        section_id = section_selection.split('(')[-1].split(')')[0]

        book_selection = self.assign_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        result = self.controller.catalog.add_book_to_section(book_id, section_id)

        if result:
            messagebox.showinfo("Success", "Book assigned to section successfully")

            self.update_section_books()

            self.populate_section_list()
        else:
            messagebox.showerror("Error", "Failed to assign book to section")

    def remove_book_from_section(self):

        section_selection = self.assign_section_var.get()
        if not section_selection:
            messagebox.showerror("Error", "Please select a section")
            return

        section_id = section_selection.split('(')[-1].split(')')[0]
        section = self.controller.catalog.get_section(section_id)

        if not section:
            messagebox.showerror("Error", "Section not found")
            return

        selection = self.section_books_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a book to remove")
            return

        book_id = self.section_books_tree.item(selection[0], 'values')[0]

        if book_id in section['books']:
            section['books'].remove(book_id)
            messagebox.showinfo("Success", "Book removed from section successfully")

            self.update_section_books()

            self.populate_section_list()
        else:
            messagebox.showerror("Error", "Book not found in section")

    def update_frame(self):

        if hasattr(self, 'section_tree'):
            self.populate_section_list()

        if hasattr(self, 'section_combo'):
            self.update_section_combo()

        if hasattr(self, 'book_combo'):
            self.update_book_combo()
