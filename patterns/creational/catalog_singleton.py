import uuid
from datetime import datetime

class Catalog:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Catalog, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        
        self._books = {}  
        self._users = {}  
        self._lending_records = {} 
        self._sections = {}
        self._last_updated = datetime.now()
        self._search_history = []
    
    @property
    def last_updated(self):
        return self._last_updated
    
    def add_book(self, book):
        
        self._books[book.book_id] = book
        self._last_updated = datetime.now()
        return book.book_id
    
    def get_book(self, book_id):
        
        return self._books.get(book_id)
    
    def update_book(self, book):
        
        if book.book_id in self._books:
            self._books[book.book_id] = book
            self._last_updated = datetime.now()
            return True
        return False
    
    def remove_book(self, book_id):
        
        if book_id in self._books:
            del self._books[book_id]
            self._last_updated = datetime.now()
            return True
        return False
    
    def search_books(self, **kwargs):
        
        results = list(self._books.values())
        
        if 'title' in kwargs:
            title = kwargs['title'].lower()
            results = [book for book in results if title in book.title.lower()]
        
        if 'author' in kwargs:
            author = kwargs['author'].lower()
            results = [book for book in results if author in book.author.lower()]
        
        if 'year' in kwargs:
            year = kwargs['year']
            results = [book for book in results if book.year_published == year]
        
        if 'status' in kwargs:
            status = kwargs['status']
            results = [book for book in results if book.status == status]
        
        self._search_history.append({
            'timestamp': datetime.now(),
            'criteria': kwargs,
            'results_count': len(results)
        })
        
        return results
    
    def add_user(self, user):
        
        self._users[user.user_id] = user
        self._last_updated = datetime.now()
        return user.user_id
    
    def get_user(self, user_id):
        
        return self._users.get(user_id)
    
    def update_user(self, user):
        
        if user.user_id in self._users:
            self._users[user.user_id] = user
            self._last_updated = datetime.now()
            return True
        return False
    
    def remove_user(self, user_id):
        
        if user_id in self._users:
            del self._users[user_id]
            self._last_updated = datetime.now()
            return True
        return False
    
    def add_lending_record(self, lending_record):
        
        self._lending_records[lending_record.record_id] = lending_record
        self._last_updated = datetime.now()
        return lending_record.record_id
    
    def get_lending_record(self, record_id):
        
        return self._lending_records.get(record_id)
    
    def update_lending_record(self, lending_record):
        
        if lending_record.record_id in self._lending_records:
            self._lending_records[lending_record.record_id] = lending_record
            self._last_updated = datetime.now()
            return True
        return False
    
    def get_user_lending_records(self, user_id):
        
        return [record for record in self._lending_records.values() if record.user_id == user_id]
    
    def get_book_lending_records(self, book_id):
        
        return [record for record in self._lending_records.values() if record.book_id == book_id]
    
    def get_overdue_records(self):
        
        return [record for record in self._lending_records.values() if record.is_overdue()]
    
    def add_section(self, name, description, access_level=0):
        
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
        
        return self._sections.get(section_id)
    
    def get_section_by_name(self, name):
        
        for section in self._sections.values():
            if section['name'].lower() == name.lower():
                return section
        return None
    def add_book_to_section(self, book_id, section_id):
        
        if book_id in self._books and section_id in self._sections:
            if book_id not in self._sections[section_id]['books']:
                self._sections[section_id]['books'].append(book_id)
                self._last_updated = datetime.now()
            return True
        return False
