
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto

class BookCondition(Enum):
    EXCELLENT = auto()
    GOOD = auto()
    FAIR = auto()
    POOR = auto()
    CRITICAL = auto()

class BookStatus(Enum):
    AVAILABLE = auto()
    BORROWED = auto()
    RESERVED = auto()
    RESTORATION = auto()
    LOST = auto()

class Book(ABC):

    def __init__(self, book_id, title, author, year_published, isbn=None, quantity=1):
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
        self._quantity = max(1, quantity)
        self._available_quantity = self._quantity

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

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        diff = value - self._quantity
        self._quantity = value
        self._available_quantity = max(0, self._available_quantity + diff)
        if self._quantity == 0:
            self._status = BookStatus.LOST
        elif self._quantity > 0 and self._available_quantity > 0 and self._status == BookStatus.LOST:
            self._status = BookStatus.AVAILABLE

    @property
    def available_quantity(self):
        return self._available_quantity

    def decrease_available_quantity(self):
        if self._available_quantity <= 0:
            raise ValueError("No copies available to borrow")
        self._available_quantity -= 1
        if self._available_quantity == 0:
            self._status = BookStatus.BORROWED
        return True

    def increase_available_quantity(self):
        if self._available_quantity >= self._quantity:
            raise ValueError("Cannot return more copies than total quantity")
        self._available_quantity += 1
        if self._available_quantity > 0 and self._status == BookStatus.BORROWED:
            self._status = BookStatus.AVAILABLE
        return True

    @abstractmethod
    def get_lending_period(self):
        pass

    @abstractmethod
    def get_late_fee(self, days_overdue):
        pass

    @abstractmethod
    def needs_restoration(self):
        pass

    def record_borrowing(self, user_id, borrow_date, due_date):
        self._borrowing_history.append({
            'user_id': user_id,
            'borrow_date': borrow_date,
            'due_date': due_date,
            'return_date': None
        })

    def record_return(self, return_date):
        if self._borrowing_history and self._borrowing_history[-1]['return_date'] is None:
            self._borrowing_history[-1]['return_date'] = return_date

    def __str__(self):
        return f"{self._title} by {self._author} ({self._year_published})"

class GeneralBook(Book):

    def __init__(self, book_id, title, author, year_published, isbn=None, genre=None, quantity=1):
        super().__init__(book_id, title, author, year_published, isbn, quantity)
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
        
        return 14 if self._is_bestseller else 21

    def get_late_fee(self, days_overdue):
        
        return days_overdue * 0.25

    def needs_restoration(self):
        
        return self._condition in [BookCondition.POOR, BookCondition.CRITICAL]

class RareBook(Book):
    

    def __init__(self, book_id, title, author, year_published, isbn=None,
                 estimated_value=None, rarity_level=1, quantity=1):
        super().__init__(book_id, title, author, year_published, isbn, quantity)
        self._estimated_value = estimated_value
        self._rarity_level = rarity_level
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
        
        return 7

    def get_late_fee(self, days_overdue):
        
        return days_overdue * 1.0

    def needs_restoration(self):
        
        return self._condition in [BookCondition.FAIR, BookCondition.POOR, BookCondition.CRITICAL]

class AncientScript(Book):
    

    def __init__(self, book_id, title, author, year_published, isbn=None,
                 origin=None, language=None, translation_available=False, quantity=1):
        super().__init__(book_id, title, author, year_published, isbn, quantity)
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
        
        self._preservation_requirements.append(requirement)

    @property
    def digital_copy_available(self):
        return self._digital_copy_available

    @digital_copy_available.setter
    def digital_copy_available(self, value):
        self._digital_copy_available = bool(value)

    def get_lending_period(self):
        
        return 0

    def get_late_fee(self, days_overdue):
        
        return 0

    def needs_restoration(self):
        
        return self._condition != BookCondition.EXCELLENT
