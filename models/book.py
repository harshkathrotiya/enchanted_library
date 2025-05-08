"""
Book models for the Enchanted Library system.
This module contains the base Book class and its specialized subclasses.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto


class BookCondition(Enum):
    """Enum representing the physical condition of a book."""
    EXCELLENT = auto()
    GOOD = auto()
    FAIR = auto()
    POOR = auto()
    CRITICAL = auto()


class BookStatus(Enum):
    """Enum representing the current status of a book."""
    AVAILABLE = auto()
    BORROWED = auto()
    RESERVED = auto()
    RESTORATION = auto()
    LOST = auto()


class Book(ABC):
    """Base abstract class for all types of books in the library."""
    
    def __init__(self, book_id, title, author, year_published, isbn=None):
        """
        Initialize a new Book.
        
        Args:
            book_id (str): Unique identifier for the book
            title (str): Title of the book
            author (str): Author of the book
            year_published (int): Year the book was published
            isbn (str, optional): ISBN number if available
        """
        self._book_id = book_id
        self._title = title
        self._author = author
        self._year_published = year_published
        self._isbn = isbn
        self._condition = BookCondition.GOOD
        self._status = BookStatus.AVAILABLE
        self._location = None
        self._acquisition_date = datetime.now()
        self._last_maintenance = datetime.now()
        self._borrowing_history = []
    
    @property
    def book_id(self):
        return self._book_id
    
    @property
    def title(self):
        return self._title
    
    @property
    def author(self):
        return self._author
    
    @property
    def year_published(self):
        return self._year_published
    
    @property
    def isbn(self):
        return self._isbn
    
    @property
    def condition(self):
        return self._condition
    
    @condition.setter
    def condition(self, value):
        if not isinstance(value, BookCondition):
            raise ValueError("Condition must be a BookCondition enum value")
        self._condition = value
        
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if not isinstance(value, BookStatus):
            raise ValueError("Status must be a BookStatus enum value")
        self._status = value
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, value):
        self._location = value
    
    @abstractmethod
    def get_lending_period(self):
        """Return the maximum lending period in days for this book type."""
        pass
    
    @abstractmethod
    def get_late_fee(self, days_overdue):
        """Calculate the late fee based on days overdue."""
        pass
    
    @abstractmethod
    def needs_restoration(self):
        """Determine if the book needs restoration based on its condition and age."""
        pass
    
    def record_borrowing(self, user_id, borrow_date, due_date):
        """Record a borrowing event in the book's history."""
        self._borrowing_history.append({
            'user_id': user_id,
            'borrow_date': borrow_date,
            'due_date': due_date,
            'return_date': None
        })
    
    def record_return(self, return_date):
        """Record the return of the book."""
        if self._borrowing_history and self._borrowing_history[-1]['return_date'] is None:
            self._borrowing_history[-1]['return_date'] = return_date
    
    def __str__(self):
        return f"{self._title} by {self._author} ({self._year_published})"


class GeneralBook(Book):
    """Regular books available for general circulation."""
    
    def __init__(self, book_id, title, author, year_published, isbn=None, genre=None):
        super().__init__(book_id, title, author, year_published, isbn)
        self._genre = genre
        self._is_bestseller = False
    
    @property
    def genre(self):
        return self._genre
    
    @property
    def is_bestseller(self):
        return self._is_bestseller
    
    @is_bestseller.setter
    def is_bestseller(self, value):
        self._is_bestseller = bool(value)
    
    def get_lending_period(self):
        """General books can be borrowed for 21 days, bestsellers for 14 days."""
        return 14 if self._is_bestseller else 21
    
    def get_late_fee(self, days_overdue):
        """Late fee is $0.25 per day for general books."""
        return days_overdue * 0.25
    
    def needs_restoration(self):
        """General books need restoration if in poor condition."""
        return self._condition in [BookCondition.POOR, BookCondition.CRITICAL]


class RareBook(Book):
    """Rare and valuable books with restricted access."""
    
    def __init__(self, book_id, title, author, year_published, isbn=None, 
                 estimated_value=None, rarity_level=1):
        super().__init__(book_id, title, author, year_published, isbn)
        self._estimated_value = estimated_value
        self._rarity_level = rarity_level  # 1-10 scale, 10 being the rarest
        self._requires_gloves = rarity_level > 5
        self._special_handling_notes = ""
    
    @property
    def estimated_value(self):
        return self._estimated_value
    
    @property
    def rarity_level(self):
        return self._rarity_level
    
    @property
    def requires_gloves(self):
        return self._requires_gloves
    
    @property
    def special_handling_notes(self):
        return self._special_handling_notes
    
    @special_handling_notes.setter
    def special_handling_notes(self, value):
        self._special_handling_notes = value
    
    def get_lending_period(self):
        """Rare books can only be borrowed for 7 days."""
        return 7
    
    def get_late_fee(self, days_overdue):
        """Late fee is $1.00 per day for rare books."""
        return days_overdue * 1.0
    
    def needs_restoration(self):
        """Rare books need more frequent restoration."""
        return self._condition in [BookCondition.FAIR, BookCondition.POOR, BookCondition.CRITICAL]


class AncientScript(Book):
    """Ancient manuscripts and scrolls requiring special preservation."""
    
    def __init__(self, book_id, title, author, year_published, isbn=None, 
                 origin=None, language=None, translation_available=False):
        super().__init__(book_id, title, author, year_published, isbn)
        self._origin = origin
        self._language = language
        self._translation_available = translation_available
        self._preservation_requirements = []
        self._digital_copy_available = False
    
    @property
    def origin(self):
        return self._origin
    
    @property
    def language(self):
        return self._language
    
    @property
    def translation_available(self):
        return self._translation_available
    
    @translation_available.setter
    def translation_available(self, value):
        self._translation_available = bool(value)
    
    @property
    def preservation_requirements(self):
        return self._preservation_requirements
    
    def add_preservation_requirement(self, requirement):
        """Add a preservation requirement for this ancient script."""
        self._preservation_requirements.append(requirement)
    
    @property
    def digital_copy_available(self):
        return self._digital_copy_available
    
    @digital_copy_available.setter
    def digital_copy_available(self, value):
        self._digital_copy_available = bool(value)
    
    def get_lending_period(self):
        """Ancient scripts can only be viewed in the reading room, not borrowed."""
        return 0  # 0 indicates in-library use only
    
    def get_late_fee(self, days_overdue):
        """Not applicable as ancient scripts cannot be borrowed."""
        return 0
    
    def needs_restoration(self):
        """Ancient scripts need restoration if not in excellent condition."""
        return self._condition != BookCondition.EXCELLENT
