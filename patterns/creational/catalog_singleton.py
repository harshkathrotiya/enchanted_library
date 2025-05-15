import uuid
from datetime import datetime
from sqlalchemy import and_, or_

from database.db_session import db_session
from database.models import Book as DBBook
from database.models import GeneralBook as DBGeneralBook
from database.models import RareBook as DBRareBook
from database.models import AncientScript as DBAncientScript
from database.models import User as DBUser
from database.models import Section as DBSection
from database.models import LendingRecord as DBLendingRecord
from patterns.structural.data_persistence import DataPersistence

class Catalog:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Catalog, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Initialize in-memory cache
        self._books = {}
        self._users = {}
        self._lending_records = {}
        self._sections = {}
        self._last_updated = datetime.now()
        self._search_history = []

        # Initialize database
        DataPersistence.initialize_database()

        # Load data from database if available
        try:
            DataPersistence.load_catalog_from_database(self)
            DataPersistence.load_users_from_database(self)
        except Exception as e:
            print(f"Warning: Could not load data from database: {e}")
            print("Using in-memory storage only.")

    @property
    def last_updated(self):
        return self._last_updated

    def add_book(self, book):
        # Add to in-memory cache
        self._books[book.book_id] = book
        self._last_updated = datetime.now()

        # Save to database
        try:
            DataPersistence.save_catalog_to_database(self)
        except Exception as e:
            print(f"Warning: Could not save book to database: {e}")

        return book.book_id

    def get_book(self, book_id):

        return self._books.get(book_id)

    def update_book(self, book):
        if book.book_id in self._books:
            # Update in-memory cache
            self._books[book.book_id] = book
            self._last_updated = datetime.now()

            # Update in database
            try:
                DataPersistence.save_catalog_to_database(self)
            except Exception as e:
                print(f"Warning: Could not update book in database: {e}")

            return True
        return False

    def remove_book(self, book_id):
        if book_id in self._books:
            # Remove from in-memory cache
            del self._books[book_id]
            self._last_updated = datetime.now()

            # Remove from database
            try:
                # Find the book in the database
                db_book = db_session.query(DBBook).filter_by(book_id=book_id).first()
                if db_book:
                    db_session.delete(db_book)
                    db_session.commit()
            except Exception as e:
                print(f"Warning: Could not remove book from database: {e}")

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
        # Add to in-memory cache
        self._users[user.user_id] = user
        self._last_updated = datetime.now()

        # Save to database
        try:
            DataPersistence.save_users_to_database(self)
        except Exception as e:
            print(f"Warning: Could not save user to database: {e}")

        return user.user_id

    def get_user(self, user_id):

        return self._users.get(user_id)

    def update_user(self, user):
        if user.user_id in self._users:
            # Update in-memory cache
            self._users[user.user_id] = user
            self._last_updated = datetime.now()

            # Update in database
            try:
                DataPersistence.save_users_to_database(self)
            except Exception as e:
                print(f"Warning: Could not update user in database: {e}")

            return True
        return False

    def remove_user(self, user_id):
        if user_id in self._users:
            # Remove from in-memory cache
            del self._users[user_id]
            self._last_updated = datetime.now()

            # Remove from database
            try:
                # Find the user in the database
                db_user = db_session.query(DBUser).filter_by(user_id=user_id).first()
                if db_user:
                    db_session.delete(db_user)
                    db_session.commit()
            except Exception as e:
                print(f"Warning: Could not remove user from database: {e}")

            return True
        return False

    def add_lending_record(self, lending_record):
        # Add to in-memory cache
        self._lending_records[lending_record.record_id] = lending_record
        self._last_updated = datetime.now()

        # Save to database
        try:
            DataPersistence.save_users_to_database(self)  # Lending records are saved with users
        except Exception as e:
            print(f"Warning: Could not save lending record to database: {e}")

        return lending_record.record_id

    def get_lending_record(self, record_id):

        return self._lending_records.get(record_id)

    def update_lending_record(self, lending_record):
        if lending_record.record_id in self._lending_records:
            # Update in-memory cache
            self._lending_records[lending_record.record_id] = lending_record
            self._last_updated = datetime.now()

            # Update in database
            try:
                DataPersistence.save_users_to_database(self)  # Lending records are saved with users
            except Exception as e:
                print(f"Warning: Could not update lending record in database: {e}")

            return True
        return False

    def get_user_lending_records(self, user_id):

        return [record for record in self._lending_records.values() if record.user_id == user_id]

    def get_book_lending_records(self, book_id):

        return [record for record in self._lending_records.values() if record.book_id == book_id]

    def get_overdue_records(self):

        return [record for record in self._lending_records.values() if record.is_overdue()]

    def add_section(self, name, description, access_level=0):
        # Create section ID
        section_id = str(uuid.uuid4())

        # Add to in-memory cache
        self._sections[section_id] = {
            'id': section_id,
            'name': name,
            'description': description,
            'access_level': access_level,
            'books': []
        }
        self._last_updated = datetime.now()

        # Save to database
        try:
            # Create new section in database
            db_section = DBSection(
                id=section_id,
                name=name,
                description=description,
                access_level=access_level
            )
            db_session.add(db_section)
            db_session.commit()
        except Exception as e:
            print(f"Warning: Could not save section to database: {e}")

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
            # Update in-memory cache
            if book_id not in self._sections[section_id]['books']:
                self._sections[section_id]['books'].append(book_id)
                self._last_updated = datetime.now()

            # Update in database
            try:
                db_book = db_session.query(DBBook).filter_by(book_id=book_id).first()
                db_section = db_session.query(DBSection).filter_by(id=section_id).first()

                if db_book and db_section and db_book not in db_section.books:
                    db_section.books.append(db_book)
                    db_session.commit()
            except Exception as e:
                print(f"Warning: Could not add book to section in database: {e}")

            return True
        return False
