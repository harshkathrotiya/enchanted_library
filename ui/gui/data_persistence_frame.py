import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import pickle
from datetime import datetime

class DataPersistenceFrame(ttk.Frame):
    

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.create_data_persistence_ui()

    def create_data_persistence_ui(self):
        

        title_label = ttk.Label(self, text="Data Persistence", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        if not self.controller.current_user or self.controller.current_user.get_role().name != 'LIBRARIAN':
            ttk.Label(self, text="Only librarians can access data persistence features",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        save_load_frame = ttk.Frame(notebook)
        import_export_frame = ttk.Frame(notebook)
        backup_frame = ttk.Frame(notebook)

        notebook.add(save_load_frame, text="Save/Load")
        notebook.add(import_export_frame, text="Import/Export")
        notebook.add(backup_frame, text="Backup")

        self.create_save_load_tab(save_load_frame)
        self.create_import_export_tab(import_export_frame)
        self.create_backup_tab(backup_frame)

    def create_save_load_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        save_frame = ttk.LabelFrame(frame, text="Save Library Data")
        save_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(save_frame, text="Save the current state of the library to a file.",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, padx=10, pady=5)

        save_button_frame = ttk.Frame(save_frame)
        save_button_frame.pack(fill=tk.X, padx=10, pady=10)

        save_button = ttk.Button(save_button_frame, text="Save Library Data",
                               command=self.save_library_data,
                               style='Primary.TButton')
        save_button.pack(side=tk.LEFT, padx=5)

        self.save_format_var = tk.StringVar(value="pickle")
        pickle_radio = ttk.Radiobutton(save_button_frame, text="Pickle Format",
                                     variable=self.save_format_var, value="pickle")
        pickle_radio.pack(side=tk.LEFT, padx=5)

        json_radio = ttk.Radiobutton(save_button_frame, text="JSON Format",
                                   variable=self.save_format_var, value="json")
        json_radio.pack(side=tk.LEFT, padx=5)

        load_frame = ttk.LabelFrame(frame, text="Load Library Data")
        load_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(load_frame, text="Load library data from a file. This will replace the current library data.",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, padx=10, pady=5)

        load_button_frame = ttk.Frame(load_frame)
        load_button_frame.pack(fill=tk.X, padx=10, pady=10)

        load_button = ttk.Button(load_button_frame, text="Load Library Data",
                               command=self.load_library_data,
                               style='Primary.TButton')
        load_button.pack(side=tk.LEFT, padx=5)

        self.load_format_var = tk.StringVar(value="pickle")
        pickle_radio = ttk.Radiobutton(load_button_frame, text="Pickle Format",
                                     variable=self.load_format_var, value="pickle")
        pickle_radio.pack(side=tk.LEFT, padx=5)

        json_radio = ttk.Radiobutton(load_button_frame, text="JSON Format",
                                   variable=self.load_format_var, value="json")
        json_radio.pack(side=tk.LEFT, padx=5)

        recent_frame = ttk.LabelFrame(frame, text="Recent Files")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        self.recent_files_text = tk.Text(recent_frame, wrap=tk.WORD, height=10, width=60)
        self.recent_files_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_recent_files()

    def create_import_export_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        export_frame = ttk.LabelFrame(frame, text="Export Data")
        export_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(export_frame, text="Export specific data to CSV or JSON files.",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, padx=10, pady=5)

        export_options_frame = ttk.Frame(export_frame)
        export_options_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(export_options_frame, text="Export Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.export_type_var = tk.StringVar(value="books")
        export_types = [
            ("Books", "books"),
            ("Users", "users"),
            ("Lending Records", "lending"),
            ("Sections", "sections"),
            ("Preservation Records", "preservation")
        ]

        for i, (text, value) in enumerate(export_types):
            ttk.Radiobutton(export_options_frame, text=text,
                          variable=self.export_type_var, value=value).grid(
                row=0, column=i+1, padx=5, pady=5)

        ttk.Label(export_options_frame, text="Format:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.export_format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(export_options_frame, text="CSV",
                      variable=self.export_format_var, value="csv").grid(
            row=1, column=1, padx=5, pady=5)

        ttk.Radiobutton(export_options_frame, text="JSON",
                      variable=self.export_format_var, value="json").grid(
            row=1, column=2, padx=5, pady=5)

        export_button = ttk.Button(export_frame, text="Export Data",
                                 command=self.export_data,
                                 style='Primary.TButton')
        export_button.pack(padx=10, pady=10)

        import_frame = ttk.LabelFrame(frame, text="Import Data")
        import_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(import_frame, text="Import data from CSV or JSON files.",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, padx=10, pady=5)

        import_options_frame = ttk.Frame(import_frame)
        import_options_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(import_options_frame, text="Import Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.import_type_var = tk.StringVar(value="books")
        import_types = [
            ("Books", "books"),
            ("Users", "users"),
            ("Lending Records", "lending"),
            ("Sections", "sections"),
            ("Preservation Records", "preservation")
        ]

        for i, (text, value) in enumerate(import_types):
            ttk.Radiobutton(import_options_frame, text=text,
                          variable=self.import_type_var, value=value).grid(
                row=0, column=i+1, padx=5, pady=5)

        ttk.Label(import_options_frame, text="Format:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.import_format_var = tk.StringVar(value="csv")
        ttk.Radiobutton(import_options_frame, text="CSV",
                      variable=self.import_format_var, value="csv").grid(
            row=1, column=1, padx=5, pady=5)

        ttk.Radiobutton(import_options_frame, text="JSON",
                      variable=self.import_format_var, value="json").grid(
            row=1, column=2, padx=5, pady=5)

        self.merge_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(import_options_frame, text="Merge with existing data",
                       variable=self.merge_var).grid(
            row=1, column=3, padx=5, pady=5)

        import_button = ttk.Button(import_frame, text="Import Data",
                                 command=self.import_data,
                                 style='Primary.TButton')
        import_button.pack(padx=10, pady=10)

    def create_backup_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        auto_backup_frame = ttk.LabelFrame(frame, text="Auto Backup")
        auto_backup_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(auto_backup_frame, text="Configure automatic backups of library data.",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, padx=10, pady=5)

        options_frame = ttk.Frame(auto_backup_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(options_frame, text="Backup Frequency:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.backup_frequency_var = tk.StringVar(value="daily")
        frequencies = [("Daily", "daily"), ("Weekly", "weekly"), ("Monthly", "monthly"), ("Never", "never")]

        for i, (text, value) in enumerate(frequencies):
            ttk.Radiobutton(options_frame, text=text,
                          variable=self.backup_frequency_var, value=value).grid(
                row=0, column=i+1, padx=5, pady=5)

        ttk.Label(options_frame, text="Backup Location:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.backup_location_var = tk.StringVar(value="./backups")
        location_entry = ttk.Entry(options_frame, textvariable=self.backup_location_var, width=30)
        location_entry.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)

        browse_button = ttk.Button(options_frame, text="Browse",
                                 command=self.browse_backup_location)
        browse_button.grid(row=1, column=4, padx=5, pady=5)

        ttk.Label(options_frame, text="Keep Backups:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

        self.keep_backups_var = tk.StringVar(value="5")
        ttk.Spinbox(options_frame, from_=1, to=30, textvariable=self.keep_backups_var, width=5).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5)

        save_settings_button = ttk.Button(auto_backup_frame, text="Save Backup Settings",
                                        command=self.save_backup_settings,
                                        style='Primary.TButton')
        save_settings_button.pack(padx=10, pady=10)

        manual_backup_frame = ttk.LabelFrame(frame, text="Manual Backup")
        manual_backup_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(manual_backup_frame, text="Create a backup of the current library data.",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, padx=10, pady=5)

        backup_button = ttk.Button(manual_backup_frame, text="Create Backup Now",
                                 command=self.create_backup,
                                 style='Primary.TButton')
        backup_button.pack(padx=10, pady=10)

        restore_frame = ttk.LabelFrame(frame, text="Restore Backup")
        restore_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(restore_frame, text="Restore library data from a backup file.",
                 font=('Helvetica', 10, 'italic')).pack(anchor=tk.W, padx=10, pady=5)

        restore_button = ttk.Button(restore_frame, text="Restore from Backup",
                                  command=self.restore_backup,
                                  style='Primary.TButton')
        restore_button.pack(padx=10, pady=10)

    def save_library_data(self):
        

        file_format = self.save_format_var.get()

        extension = ".pkl" if file_format == "pickle" else ".json"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"library_data_{timestamp}{extension}"

        file_path = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=[("Pickle files" if file_format == "pickle" else "JSON files",
                      f"*{extension}")],
            initialfile=default_filename
        )

        if not file_path:
            return

        try:
            data = {
                'books': self.controller.catalog._books,
                'users': self.controller.catalog._users,
                'lending_records': self.controller.catalog._lending_records,
                'sections': self.controller.catalog._sections,
                'timestamp': datetime.now().isoformat()
            }

            if hasattr(self.controller, 'preservation_service'):
                data['preservation_records'] = self.controller.preservation_service._preservation_records
                data['preservation_schedules'] = self.controller.preservation_service._preservation_schedules

            if file_format == "pickle":
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
            else:
                json_data = self.prepare_data_for_json(data)

                with open(file_path, 'w') as f:
                    json.dump(json_data, f, indent=2)

            self.add_recent_file(file_path)

            messagebox.showinfo("Success", f"Library data saved to {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save library data: {str(e)}")

    def load_library_data(self):
        

        file_format = self.load_format_var.get()

        extension = ".pkl" if file_format == "pickle" else ".json"

        file_path = filedialog.askopenfilename(
            defaultextension=extension,
            filetypes=[("Pickle files" if file_format == "pickle" else "JSON files",
                      f"*{extension}")]
        )

        if not file_path:
            return

        if not messagebox.askyesno("Confirm Load",
                                 "Loading will replace all current library data. Continue?"):
            return

        try:
            if file_format == "pickle":
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            else:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)

                data = self.convert_json_to_objects(json_data)

            self.controller.catalog._books = data.get('books', {})
            self.controller.catalog._users = data.get('users', {})
            self.controller.catalog._lending_records = data.get('lending_records', {})
            self.controller.catalog._sections = data.get('sections', {})

            if hasattr(self.controller, 'preservation_service') and 'preservation_records' in data:
                self.controller.preservation_service._preservation_records = data['preservation_records']
                self.controller.preservation_service._preservation_schedules = data.get('preservation_schedules', [])

            self.add_recent_file(file_path)

            messagebox.showinfo("Success", f"Library data loaded from {file_path}")

            self.controller.refresh_all_frames()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load library data: {str(e)}")

    def export_data(self):
        

        export_type = self.export_type_var.get()
        export_format = self.export_format_var.get()

        extension = f".{export_format}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{export_type}_{timestamp}{extension}"

        file_path = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=[(f"{export_format.upper()} files", f"*{extension}")],
            initialfile=default_filename
        )

        if not file_path:
            return

        try:
            if export_type == "books":
                data = self.controller.catalog._books
            elif export_type == "users":
                data = self.controller.catalog._users
            elif export_type == "lending":
                data = self.controller.catalog._lending_records
            elif export_type == "sections":
                data = self.controller.catalog._sections
            elif export_type == "preservation":
                if hasattr(self.controller, 'preservation_service'):
                    data = {
                        'records': self.controller.preservation_service._preservation_records,
                        'schedules': self.controller.preservation_service._preservation_schedules
                    }
                else:
                    messagebox.showerror("Error", "Preservation service not available")
                    return

            if export_format == "json":
                json_data = self.prepare_data_for_json(data)

                with open(file_path, 'w') as f:
                    json.dump(json_data, f, indent=2)
            else:
                self.export_to_csv(data, export_type, file_path)

            messagebox.showinfo("Success", f"{export_type.capitalize()} exported to {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def import_data(self):
        

        import_type = self.import_type_var.get()
        import_format = self.import_format_var.get()
        merge = self.merge_var.get()

        extension = f".{import_format}"

        file_path = filedialog.askopenfilename(
            defaultextension=extension,
            filetypes=[(f"{import_format.upper()} files", f"*{extension}")]
        )

        if not file_path:
            return

        if not messagebox.askyesno("Confirm Import",
                                 f"Import {import_type} from {file_path}?"):
            return

        try:
            if import_format == "json":
                with open(file_path, 'r') as f:
                    json_data = json.load(f)

                data = self.convert_json_to_objects(json_data)
            else:
                data = self.import_from_csv(file_path, import_type)

            if import_type == "books":
                if merge:
                    self.controller.catalog._books.update(data)
                else:
                    self.controller.catalog._books = data
            elif import_type == "users":
                if merge:
                    self.controller.catalog._users.update(data)
                else:
                    self.controller.catalog._users = data
            elif import_type == "lending":
                if merge:
                    self.controller.catalog._lending_records.update(data)
                else:
                    self.controller.catalog._lending_records = data
            elif import_type == "sections":
                if merge:
                    self.controller.catalog._sections.update(data)
                else:
                    self.controller.catalog._sections = data
            elif import_type == "preservation":
                if hasattr(self.controller, 'preservation_service'):
                    if merge:
                        self.controller.preservation_service._preservation_records.extend(data.get('records', []))
                        self.controller.preservation_service._preservation_schedules.extend(data.get('schedules', []))
                    else:
                        self.controller.preservation_service._preservation_records = data.get('records', [])
                        self.controller.preservation_service._preservation_schedules = data.get('schedules', [])
                else:
                    messagebox.showerror("Error", "Preservation service not available")
                    return

            messagebox.showinfo("Success", f"{import_type.capitalize()} imported from {file_path}")

            self.controller.refresh_all_frames()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data: {str(e)}")

    def browse_backup_location(self):
        

        directory = filedialog.askdirectory()
        if directory:
            self.backup_location_var.set(directory)

    def save_backup_settings(self):
        

        frequency = self.backup_frequency_var.get()
        location = self.backup_location_var.get()
        keep_backups = self.keep_backups_var.get()

        try:
            keep_backups = int(keep_backups)
            if keep_backups < 1:
                raise ValueError("Keep backups must be at least 1")
        except ValueError:
            messagebox.showerror("Error", "Keep backups must be a positive number")
            return

        if not os.path.exists(location):
            try:
                os.makedirs(location)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create backup directory: {str(e)}")
                return

        settings = {
            'frequency': frequency,
            'location': location,
            'keep_backups': keep_backups
        }

        try:
            with open('backup_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)

            messagebox.showinfo("Success", "Backup settings saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save backup settings: {str(e)}")

    def create_backup(self):
        

        location = self.backup_location_var.get()

        if not os.path.exists(location):
            try:
                os.makedirs(location)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create backup directory: {str(e)}")
                return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(location, f"library_backup_{timestamp}.pkl")

        try:
            data = {
                'books': self.controller.catalog._books,
                'users': self.controller.catalog._users,
                'lending_records': self.controller.catalog._lending_records,
                'sections': self.controller.catalog._sections,
                'timestamp': datetime.now().isoformat()
            }

            if hasattr(self.controller, 'preservation_service'):
                data['preservation_records'] = self.controller.preservation_service._preservation_records
                data['preservation_schedules'] = self.controller.preservation_service._preservation_schedules

            with open(backup_file, 'wb') as f:
                pickle.dump(data, f)

            messagebox.showinfo("Success", f"Backup created at {backup_file}")

            self.cleanup_old_backups()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")

    def restore_backup(self):
        

        backup_file = filedialog.askopenfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl")]
        )

        if not backup_file:
            return

        if not messagebox.askyesno("Confirm Restore",
                                 "Restoring will replace all current library data. Continue?"):
            return

        try:
            with open(backup_file, 'rb') as f:
                data = pickle.load(f)

            self.controller.catalog._books = data.get('books', {})
            self.controller.catalog._users = data.get('users', {})
            self.controller.catalog._lending_records = data.get('lending_records', {})
            self.controller.catalog._sections = data.get('sections', {})

            if hasattr(self.controller, 'preservation_service') and 'preservation_records' in data:
                self.controller.preservation_service._preservation_records = data['preservation_records']
                self.controller.preservation_service._preservation_schedules = data.get('preservation_schedules', [])

            messagebox.showinfo("Success", f"Library data restored from {backup_file}")

            self.controller.refresh_all_frames()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")

    def cleanup_old_backups(self):
        

        location = self.backup_location_var.get()
        try:
            keep_backups = int(self.keep_backups_var.get())
        except ValueError:
            keep_backups = 5

        backup_files = []
        for file in os.listdir(location):
            if file.startswith("library_backup_") and file.endswith(".pkl"):
                backup_files.append(os.path.join(location, file))

        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        if len(backup_files) > keep_backups:
            for file in backup_files[keep_backups:]:
                try:
                    os.remove(file)
                except Exception:
                    pass

    def add_recent_file(self, file_path):
        

        recent_files = []
        try:
            if os.path.exists('recent_files.json'):
                with open('recent_files.json', 'r') as f:
                    recent_files = json.load(f)
        except Exception:
            recent_files = []

        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)

        recent_files = recent_files[:10]

        try:
            with open('recent_files.json', 'w') as f:
                json.dump(recent_files, f)
        except Exception:
            pass

        self.update_recent_files()

    def update_recent_files(self):
        

        self.recent_files_text.delete(1.0, tk.END)

        recent_files = []
        try:
            if os.path.exists('recent_files.json'):
                with open('recent_files.json', 'r') as f:
                    recent_files = json.load(f)
        except Exception:
            recent_files = []

        if not recent_files:
            self.recent_files_text.insert(tk.END, "No recent files")
            return

        for i, file in enumerate(recent_files):
            try:
                mtime = os.path.getmtime(file)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                file_size = os.path.getsize(file)
                file_size_str = self.format_file_size(file_size)

                self.recent_files_text.insert(tk.END, f"{i+1}. {os.path.basename(file)}\n")
                self.recent_files_text.insert(tk.END, f"   Path: {file}\n")
                self.recent_files_text.insert(tk.END, f"   Modified: {mtime_str}, Size: {file_size_str}\n\n")
            except Exception:
                self.recent_files_text.insert(tk.END, f"{i+1}. {file} (not found)\n\n")

    def format_file_size(self, size):
        

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def prepare_data_for_json(self, data):
        

        return {"message": "JSON export not fully implemented"}

    def convert_json_to_objects(self, json_data):
        

        return {}

    def export_to_csv(self, data, export_type, file_path):
        

        with open(file_path, 'w') as f:
            f.write(f"# {export_type.capitalize()} Export\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write("# This is a placeholder CSV export\n")

    def import_from_csv(self, file_path, import_type):
        

        return {}

    def update_frame(self):
        

        self.update_recent_files()
