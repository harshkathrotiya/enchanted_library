"""
Catalog Singleton implementation for the Enchanted Library system.
This module implements the Singleton Pattern for the library catalog.
"""
import uuid
from datetime import datetime


class Catalog:
    """
    Singleton class for the library catalog.
    Ensures only one catalog instance exists throughout the system.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Catalog, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the catalog with empty collections."""
        self._books = {}  # Dictionary of book_id -> book
        self._users = {}  # Dictionary of user_id -> user
        self._lending_records = {}  # Dictionary of record_id -> lending_record
        self._sections = {}  # Dictionary of section_id -> section
        self._last_updated = datetime.now()
        self._search_history = []
    
    @property
    def last_updated(self):
        return self._last_updated
    
    def add_book(self, book):
        """
        Add a book to the catalog.
        
        Args:
            book: The book to add
            
        Returns:
            str: The ID of the added book
        """
        self._books[book.book_id] = book
        self._last_updated = datetime.now()
        return book.book_id
    
    def get_book(self, book_id):
        """
        Get a book from the catalog by ID.
        
        Args:
            book_id (str): ID of the book to retrieve
            
        Returns:
            Book: The requested book, or None if not found
        """
        return self._books.get(book_id)
    
    def update_book(self, book):
        """
        Update a book in the catalog.
        
        Args:
            book: The book to update
            
        Returns:
            bool: True if the book was updated, False if not found
        """
        if book.book_id in self._books:
            self._books[book.book_id] = book
            self._last_updated = datetime.now()
            return True
        return False
    
    def remove_book(self, book_id):
        """
        Remove a book from the catalog.
        
        Args:
            book_id (str): ID of the book to remove
            
        Returns:
            bool: True if the book was removed, False if not found
        """
        if book_id in self._books:
            del self._books[book_id]
            self._last_updated = datetime.now()
            return True
        return False
    
    def search_books(self, **kwargs):
        """
        Search for books matching the given criteria.
        
        Args:
            **kwargs: Search criteria (title, author, year, etc.)
            
        Returns:
            list: List of books matching the criteria
        """
        results = list(self._books.values())
        
        # Filter by title
        if 'title' in kwargs:
            title = kwargs['title'].lower()
            results = [book for book in results if title in book.title.lower()]
        
        # Filter by author
        if 'author' in kwargs:
            author = kwargs['author'].lower()
            results = [book for book in results if author in book.author.lower()]
        
        # Filter by year
        if 'year' in kwargs:
            year = kwargs['year']
            results = [book for book in results if book.year_published == year]
        
        # Filter by status
        if 'status' in kwargs:
            status = kwargs['status']
            results = [book for book in results if book.status == status]
        
        # Record the search
        self._search_history.append({
            'timestamp': datetime.now(),
            'criteria': kwargs,
            'results_count': len(results)
        })
        
        return results
    
    def add_user(self, user):
        """
        Add a user to the catalog.
        
        Args:
            user: The user to add
            
        Returns:
            str: The ID of the added user
        """
        self._users[user.user_id] = user
        self._last_updated = datetime.now()
        return user.user_id
    
    def get_user(self, user_id):
        """
        Get a user from the catalog by ID.
        
        Args:
            user_id (str): ID of the user to retrieve
            
        Returns:
            User: The requested user, or None if not found
        """
        return self._users.get(user_id)
    
    def update_user(self, user):
        """
        Update a user in the catalog.
        
        Args:
            user: The user to update
            
        Returns:
            bool: True if the user was updated, False if not found
        """
        if user.user_id in self._users:
            self._users[user.user_id] = user
            self._last_updated = datetime.now()
            return True
        return False
    
    def remove_user(self, user_id):
        """
        Remove a user from the catalog.
        
        Args:
            user_id (str): ID of the user to remove
            
        Returns:
            bool: True if the user was removed, False if not found
        """
        if user_id in self._users:
            del self._users[user_id]
            self._last_updated = datetime.now()
            return True
        return False
    
    def add_lending_record(self, lending_record):
        """
        Add a lending record to the catalog.
        
        Args:
            lending_record: The lending record to add
            
        Returns:
            str: The ID of the added lending record
        """
        self._lending_records[lending_record.record_id] = lending_record
        self._last_updated = datetime.now()
        return lending_record.record_id
    
    def get_lending_record(self, record_id):
        """
        Get a lending record from the catalog by ID.
        
        Args:
            record_id (str): ID of the lending record to retrieve
            
        Returns:
            LendingRecord: The requested lending record, or None if not found
        """
        return self._lending_records.get(record_id)
    
    def update_lending_record(self, lending_record):
        """
        Update a lending record in the catalog.
        
        Args:
            lending_record: The lending record to update
            
        Returns:
            bool: True if the lending record was updated, False if not found
        """
        if lending_record.record_id in self._lending_records:
            self._lending_records[lending_record.record_id] = lending_record
            self._last_updated = datetime.now()
            return True
        return False
    
    def get_user_lending_records(self, user_id):
        """
        Get all lending records for a specific user.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            list: List of lending records for the user
        """
        return [record for record in self._lending_records.values() if record.user_id == user_id]
    
    def get_book_lending_records(self, book_id):
        """
        Get all lending records for a specific book.
        
        Args:
            book_id (str): ID of the book
            
        Returns:
            list: List of lending records for the book
        """
        return [record for record in self._lending_records.values() if record.book_id == book_id]
    
    def get_overdue_records(self):
        """
        Get all overdue lending records.
        
        Returns:
            list: List of overdue lending records
        """
        return [record for record in self._lending_records.values() if record.is_overdue()]
    
    def add_section(self, name, description, access_level=0):
        """
        Add a new section to the library.
        
        Args:
            name (str): Name of the section
            description (str): Description of the section
            access_level (int): Required access level (0=public, 1=restricted, 2=highly restricted)
            
        Returns:
            str: The ID of the added section
        """
        section_id = str(uuid.uuid4())
        self._sections[section_id] = {
            'id': section_id,
            'name': name,
            'description': description,
            'access_level': access_level,
            'books': []
        }
        self._last_updated = datetime.now()
        return section_id
    
    def get_section(self, section_id):
        """
        Get a section from the catalog by ID.
        
        Args:
            section_id (str): ID of the section to retrieve
            
        Returns:
            dict: The requested section, or None if not found
        """
        return self._sections.get(section_id)
    
    def get_section_by_name(self, name):
        """
        Get a section from the catalog by name.
        
        Args:
            name (str): Name of the section to retrieve
            
        Returns:
            dict: The requested section, or None if not found
        """
        for section in self._sections.values():
            if section['name'].lower() == name.lower():
                return section
        return None
    
    def add_book_to_section(self, book_id, section_id):
        """
        Add a book to a section.
        
        Args:
            book_id (str): ID of the book to add
            section_id (str): ID of the section to add the book to
            
        Returns:
            bool: True if the book was added, False if not found
        """
        if book_id in self._books and section_id in self._sections:
            if book_id not in self._sections[section_id]['books']:
                self._sections[section_id]['books'].append(book_id)
                self._last_updated = datetime.now()
            return True
        return False
