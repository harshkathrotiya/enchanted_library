import tkinter as tk
from tkinter import ttk, messagebox
import random
from collections import Counter

class RecommendationFrame(ttk.Frame):
    

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.create_recommendation_ui()

    def create_recommendation_ui(self):
        

        title_label = ttk.Label(self, text="Book Recommendations", style='Title.TLabel')
        title_label.pack(fill=tk.X, pady=(0, 10))

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        personal_frame = ttk.Frame(notebook)
        similar_frame = ttk.Frame(notebook)
        topic_frame = ttk.Frame(notebook)
        preferences_frame = ttk.Frame(notebook)

        notebook.add(personal_frame, text="Personal Recommendations")
        notebook.add(similar_frame, text="Similar Books")
        notebook.add(topic_frame, text="By Topic")
        notebook.add(preferences_frame, text="Preferences")

        self.create_personal_tab(personal_frame)
        self.create_similar_tab(similar_frame)
        self.create_topic_tab(topic_frame)
        self.create_preferences_tab(preferences_frame)

    def create_personal_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if self.controller.current_user:
            welcome_label = ttk.Label(frame,
                                    text=f"Recommendations for {self.controller.current_user.name}",
                                    font=('Helvetica', 12, 'bold'))
            welcome_label.pack(anchor=tk.W, pady=(0, 10))
        else:
            welcome_label = ttk.Label(frame,
                                    text="Please log in to get personalized recommendations",
                                    font=('Helvetica', 12, 'italic'))
            welcome_label.pack(anchor=tk.W, pady=(0, 10))
            return

        types_frame = ttk.Frame(frame)
        types_frame.pack(fill=tk.X, pady=10)

        ttk.Label(types_frame, text="Recommendation Type:",
                 font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.rec_type_var = tk.StringVar(value="history")
        rec_types = [
            ("Based on Reading History", "history"),
            ("Based on User Profile", "profile"),
            ("Popular in Your Category", "popular")
        ]

        for i, (text, value) in enumerate(rec_types):
            ttk.Radiobutton(types_frame, text=text,
                          variable=self.rec_type_var, value=value).grid(
                row=0, column=i+1, padx=5, pady=5)

        get_rec_button = ttk.Button(frame, text="Get Recommendations",
                                  command=self.get_personal_recommendations,
                                  style='Primary.TButton')
        get_rec_button.pack(pady=10)

        results_frame = ttk.LabelFrame(frame, text="Recommended Books")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ('title', 'author', 'year', 'type', 'score')
        self.personal_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        self.personal_tree.heading('title', text='Title')
        self.personal_tree.heading('author', text='Author')
        self.personal_tree.heading('year', text='Year')
        self.personal_tree.heading('type', text='Type')
        self.personal_tree.heading('score', text='Match Score')

        self.personal_tree.column('title', width=200)
        self.personal_tree.column('author', width=150)
        self.personal_tree.column('year', width=50)
        self.personal_tree.column('type', width=100)
        self.personal_tree.column('score', width=100)

        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.personal_tree.yview)
        self.personal_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.personal_tree.xview)
        self.personal_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.personal_tree.pack(fill=tk.BOTH, expand=True)

        self.personal_tree.bind("<Double-1>", self.view_recommended_book)

    def create_similar_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select a Book:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.similar_book_var = tk.StringVar()
        self.book_combo = ttk.Combobox(frame, textvariable=self.similar_book_var, width=50)
        self.book_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        self.update_book_combo()

        ttk.Label(frame, text="Similarity Criteria:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        criteria_frame = ttk.Frame(frame)
        criteria_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        self.author_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(criteria_frame, text="Same Author",
                       variable=self.author_var).pack(side=tk.LEFT, padx=5)

        self.genre_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(criteria_frame, text="Similar Genre",
                       variable=self.genre_var).pack(side=tk.LEFT, padx=5)

        self.period_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(criteria_frame, text="Same Time Period",
                       variable=self.period_var).pack(side=tk.LEFT, padx=5)

        get_similar_button = ttk.Button(frame, text="Find Similar Books",
                                      command=self.get_similar_books,
                                      style='Primary.TButton')
        get_similar_button.grid(row=2, column=0, columnspan=2, pady=10)

        results_frame = ttk.LabelFrame(frame, text="Similar Books")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)

        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(1, weight=1)

        columns = ('title', 'author', 'year', 'type', 'similarity')
        self.similar_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        self.similar_tree.heading('title', text='Title')
        self.similar_tree.heading('author', text='Author')
        self.similar_tree.heading('year', text='Year')
        self.similar_tree.heading('type', text='Type')
        self.similar_tree.heading('similarity', text='Similarity')

        self.similar_tree.column('title', width=200)
        self.similar_tree.column('author', width=150)
        self.similar_tree.column('year', width=50)
        self.similar_tree.column('type', width=100)
        self.similar_tree.column('similarity', width=100)

        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.similar_tree.yview)
        self.similar_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.similar_tree.xview)
        self.similar_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.similar_tree.pack(fill=tk.BOTH, expand=True)

        self.similar_tree.bind("<Double-1>", self.view_recommended_book)

    def create_topic_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select a Topic:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.topic_var = tk.StringVar()
        topics = self.get_available_topics()
        topic_combo = ttk.Combobox(frame, textvariable=self.topic_var,
                                 values=topics, width=30)
        topic_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Or Enter Custom Topic:", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)

        self.custom_topic_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.custom_topic_var, width=30).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

        get_topic_button = ttk.Button(frame, text="Find Books by Topic",
                                    command=self.get_topic_recommendations,
                                    style='Primary.TButton')
        get_topic_button.grid(row=2, column=0, columnspan=2, pady=10)

        results_frame = ttk.LabelFrame(frame, text="Books by Topic")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)

        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(1, weight=1)

        columns = ('title', 'author', 'year', 'type', 'relevance')
        self.topic_tree = ttk.Treeview(results_frame, columns=columns, show='headings')

        self.topic_tree.heading('title', text='Title')
        self.topic_tree.heading('author', text='Author')
        self.topic_tree.heading('year', text='Year')
        self.topic_tree.heading('type', text='Type')
        self.topic_tree.heading('relevance', text='Relevance')

        self.topic_tree.column('title', width=200)
        self.topic_tree.column('author', width=150)
        self.topic_tree.column('year', width=50)
        self.topic_tree.column('type', width=100)
        self.topic_tree.column('relevance', width=100)

        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.topic_tree.yview)
        self.topic_tree.configure(yscroll=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.topic_tree.xview)
        self.topic_tree.configure(xscroll=x_scrollbar.set)

        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.topic_tree.pack(fill=tk.BOTH, expand=True)

        self.topic_tree.bind("<Double-1>", self.view_recommended_book)

    def create_preferences_tab(self, parent):
        

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if not self.controller.current_user:
            ttk.Label(frame, text="Please log in to manage your preferences",
                     font=('Helvetica', 12, 'italic')).pack(pady=50)
            return

        genres_frame = ttk.LabelFrame(frame, text="Favorite Genres")
        genres_frame.pack(fill=tk.X, padx=5, pady=10)

        genres = ["Fiction", "Non-Fiction", "Mystery", "Science Fiction",
                 "Fantasy", "Romance", "History", "Biography", "Science",
                 "Philosophy", "Poetry", "Drama", "Adventure"]

        self.genre_vars = {}
        genre_grid = ttk.Frame(genres_frame)
        genre_grid.pack(fill=tk.X, padx=10, pady=10)

        for i, genre in enumerate(genres):
            row, col = divmod(i, 3)
            self.genre_vars[genre] = tk.BooleanVar(value=self.is_preferred_genre(genre))
            ttk.Checkbutton(genre_grid, text=genre,
                          variable=self.genre_vars[genre]).grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2)

        authors_frame = ttk.LabelFrame(frame, text="Preferred Authors")
        authors_frame.pack(fill=tk.X, padx=5, pady=10)

        authors_entry_frame = ttk.Frame(authors_frame)
        authors_entry_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(authors_entry_frame, text="Add Author:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.new_author_var = tk.StringVar()
        ttk.Entry(authors_entry_frame, textvariable=self.new_author_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)

        add_author_button = ttk.Button(authors_entry_frame, text="Add",
                                     command=self.add_preferred_author)
        add_author_button.grid(row=0, column=2, padx=5, pady=5)

        self.authors_listbox = tk.Listbox(authors_frame, height=5, width=40)
        self.authors_listbox.pack(fill=tk.X, padx=10, pady=5)

        self.update_authors_listbox()

        remove_author_button = ttk.Button(authors_frame, text="Remove Selected",
                                        command=self.remove_preferred_author)
        remove_author_button.pack(anchor=tk.E, padx=10, pady=5)

        save_button = ttk.Button(frame, text="Save Preferences",
                               command=self.save_preferences,
                               style='Primary.TButton')
        save_button.pack(pady=20)

    def update_book_combo(self):
        

        books = list(self.controller.catalog._books.values())

        self.book_combo['values'] = [f"{book.title} by {book.author} ({book.book_id})" for book in books]

    def get_personal_recommendations(self):
        

        for item in self.personal_tree.get_children():
            self.personal_tree.delete(item)

        if not self.controller.current_user:
            messagebox.showerror("Error", "Please log in to get personalized recommendations")
            return

        rec_type = self.rec_type_var.get()

        recommendations = []

        if rec_type == "history":
            recommendations = self.get_history_based_recommendations()
        elif rec_type == "profile":
            recommendations = self.get_profile_based_recommendations()
        elif rec_type == "popular":
            recommendations = self.get_popularity_based_recommendations()

        if not recommendations:
            messagebox.showinfo("No Recommendations",
                              "No recommendations found. Try a different recommendation type.")
            return

        for book, score in recommendations:
            book_type = self.get_book_type(book)

            self.personal_tree.insert('', tk.END, values=(
                book.title,
                book.author,
                book.year_published,
                book_type,
                f"{score:.2f}"
            ))

    def get_history_based_recommendations(self):
        

        user_id = self.controller.current_user.user_id
        borrowed_books = self.controller.library.get_user_borrowed_books(user_id)

        if not borrowed_books:
            return []

        read_books = [item['book'] for item in borrowed_books]
        read_book_ids = [book.book_id for book in read_books]

        all_books = list(self.controller.catalog._books.values())

        unread_books = [book for book in all_books if book.book_id not in read_book_ids]

        if not unread_books:
            return []

        recommendations = []

        for unread_book in unread_books:
            score = 0

            for read_book in read_books:
                if unread_book.author == read_book.author:
                    score += 0.5

                if hasattr(unread_book, 'genre') and hasattr(read_book, 'genre'):
                    if unread_book.genre == read_book.genre:
                        score += 0.3

                if abs(unread_book.year_published - read_book.year_published) < 20:
                    score += 0.2

            score = min(score, 1.0)

            if score > 0:
                recommendations.append((unread_book, score))

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:10]

    def get_profile_based_recommendations(self):
        

        all_books = list(self.controller.catalog._books.values())

        preferred_genres = self.get_user_preferred_genres()

        preferred_authors = self.get_user_preferred_authors()

        recommendations = []

        for book in all_books:
            score = 0

            if book.author in preferred_authors:
                score += 0.6

            if hasattr(book, 'genre') and book.genre in preferred_genres:
                score += 0.4

            score += random.uniform(0, 0.2)

            score = min(score, 1.0)

            if score > 0.2:
                recommendations.append((book, score))

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:10]

    def get_popularity_based_recommendations(self):
        

        lending_records = self.controller.catalog._lending_records.values()

        book_counts = Counter()
        for record in lending_records:
            book_counts[record.book_id] += 1

        all_books = list(self.controller.catalog._books.values())

        user_role = self.controller.current_user.get_role().name

        if user_role == 'SCHOLAR':
            category_books = [book for book in all_books if
                             hasattr(book, 'genre') and
                             book.genre in ['Science', 'History', 'Philosophy', 'Academic']]
        elif user_role == 'GUEST':
            category_books = [book for book in all_books if
                             hasattr(book, 'genre') and
                             book.genre in ['Fiction', 'Mystery', 'Romance', 'Adventure']]
        else:
            category_books = all_books

        recommendations = []

        max_count = max(book_counts.values()) if book_counts else 1

        for book in category_books:
            score = book_counts.get(book.book_id, 0) / max_count

            score += random.uniform(0, 0.3)

            score = min(score, 1.0)

            recommendations.append((book, score))

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:10]

    def get_similar_books(self):
        

        for item in self.similar_tree.get_children():
            self.similar_tree.delete(item)

        book_selection = self.similar_book_var.get()
        if not book_selection:
            messagebox.showerror("Error", "Please select a book")
            return

        book_id = book_selection.split('(')[-1].split(')')[0]

        book = self.controller.catalog.get_book(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        check_author = self.author_var.get()
        check_genre = self.genre_var.get()
        check_period = self.period_var.get()

        all_books = list(self.controller.catalog._books.values())

        other_books = [b for b in all_books if b.book_id != book_id]

        similar_books = []

        for other_book in other_books:
            similarity = 0
            reasons = []

            if check_author and other_book.author == book.author:
                similarity += 0.4
                reasons.append("Same author")

            if check_genre and hasattr(book, 'genre') and hasattr(other_book, 'genre'):
                if other_book.genre == book.genre:
                    similarity += 0.3
                    reasons.append("Same genre")

            if check_period and abs(other_book.year_published - book.year_published) < 20:
                similarity += 0.2
                reasons.append("Same time period")

            similarity += random.uniform(0, 0.1)

            similarity = min(similarity, 1.0)

            if similarity > 0.1:
                similar_books.append((other_book, similarity, ", ".join(reasons)))

        similar_books.sort(key=lambda x: x[1], reverse=True)

        if not similar_books:
            messagebox.showinfo("No Similar Books",
                              "No similar books found. Try different similarity criteria.")
            return

        for book, similarity, reasons in similar_books[:10]:
            book_type = self.get_book_type(book)

            self.similar_tree.insert('', tk.END, values=(
                book.title,
                book.author,
                book.year_published,
                book_type,
                f"{similarity:.2f} ({reasons})"
            ))

    def get_topic_recommendations(self):
        

        for item in self.topic_tree.get_children():
            self.topic_tree.delete(item)

        topic = self.topic_var.get()
        custom_topic = self.custom_topic_var.get()

        if custom_topic:
            topic = custom_topic

        if not topic:
            messagebox.showerror("Error", "Please select or enter a topic")
            return

        all_books = list(self.controller.catalog._books.values())

        topic_books = []

        for book in all_books:
            relevance = 0

            if topic.lower() in book.title.lower():
                relevance += 0.6

            if hasattr(book, 'genre') and topic.lower() in book.genre.lower():
                relevance += 0.4

            if hasattr(book, 'description') and book.description:
                if topic.lower() in book.description.lower():
                    relevance += 0.3

            relevance += random.uniform(0, 0.1)

            relevance = min(relevance, 1.0)

            if relevance > 0.1:
                topic_books.append((book, relevance))

        topic_books.sort(key=lambda x: x[1], reverse=True)

        if not topic_books:
            messagebox.showinfo("No Books Found",
                              f"No books found for topic '{topic}'. Try a different topic.")
            return

        for book, relevance in topic_books[:10]:
            book_type = self.get_book_type(book)

            self.topic_tree.insert('', tk.END, values=(
                book.title,
                book.author,
                book.year_published,
                book_type,
                f"{relevance:.2f}"
            ))

    def view_recommended_book(self, event):
        

        tree = event.widget

        selection = tree.selection()
        if not selection:
            return

        values = tree.item(selection[0], 'values')
        title = values[0]
        author = values[1]

        book = None
        for b in self.controller.catalog._books.values():
            if b.title == title and b.author == author:
                book = b
                break

        if not book:
            messagebox.showerror("Error", "Book not found")
            return

        self.controller.show_book_details(book.book_id)

    def get_book_type(self, book):
        

        from models.book import GeneralBook, RareBook, AncientScript

        if isinstance(book, GeneralBook):
            return "General"
        elif isinstance(book, RareBook):
            return "Rare"
        elif isinstance(book, AncientScript):
            return "Ancient"
        else:
            return "Unknown"

    def get_available_topics(self):
        

        all_books = list(self.controller.catalog._books.values())

        genres = set()
        for book in all_books:
            if hasattr(book, 'genre') and book.genre:
                genres.add(book.genre)

        topics = list(genres)
        topics.extend(["Adventure", "Mystery", "Romance", "Science", "History",
                      "Philosophy", "Art", "Music", "Travel", "Cooking"])

        topics = sorted(set(topics))

        return topics

    def is_preferred_genre(self, genre):
        

        if not self.controller.current_user:
            return False

        preferred_genres = self.get_user_preferred_genres()

        return genre in preferred_genres

    def get_user_preferred_genres(self):
        

        if not self.controller.current_user:
            return []

        user = self.controller.current_user
        if not hasattr(user, 'preferences'):
            user.preferences = {}

        if 'genres' not in user.preferences:
            user.preferences['genres'] = []

        return user.preferences['genres']

    def get_user_preferred_authors(self):
        

        if not self.controller.current_user:
            return []

        user = self.controller.current_user
        if not hasattr(user, 'preferences'):
            user.preferences = {}

        if 'authors' not in user.preferences:
            user.preferences['authors'] = []

        return user.preferences['authors']

    def update_authors_listbox(self):
        

        self.authors_listbox.delete(0, tk.END)

        preferred_authors = self.get_user_preferred_authors()

        for author in preferred_authors:
            self.authors_listbox.insert(tk.END, author)

    def add_preferred_author(self):
        

        if not self.controller.current_user:
            return

        author = self.new_author_var.get()
        if not author:
            return

        user = self.controller.current_user
        if not hasattr(user, 'preferences'):
            user.preferences = {}

        if 'authors' not in user.preferences:
            user.preferences['authors'] = []

        if author not in user.preferences['authors']:
            user.preferences['authors'].append(author)

        self.update_authors_listbox()

        self.new_author_var.set("")

    def remove_preferred_author(self):
        

        if not self.controller.current_user:
            return

        selection = self.authors_listbox.curselection()
        if not selection:
            return

        author = self.authors_listbox.get(selection[0])

        user = self.controller.current_user
        if hasattr(user, 'preferences') and 'authors' in user.preferences:
            if author in user.preferences['authors']:
                user.preferences['authors'].remove(author)

        self.update_authors_listbox()

    def save_preferences(self):
        

        if not self.controller.current_user:
            return

        user = self.controller.current_user

        if not hasattr(user, 'preferences'):
            user.preferences = {}

        preferred_genres = []
        for genre, var in self.genre_vars.items():
            if var.get():
                preferred_genres.append(genre)

        user.preferences['genres'] = preferred_genres

        self.controller.catalog.update_user(user)

        messagebox.showinfo("Success", "Preferences saved successfully")

    def update_frame(self):
        

        self.update_book_combo()

        if hasattr(self, 'authors_listbox'):
            self.update_authors_listbox()
