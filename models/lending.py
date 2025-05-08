"""
Lending models for the Enchanted Library system.
This module contains classes for managing book lending records and policies.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, auto


class LendingStatus(Enum):
    """Enum representing the status of a lending record."""
    ACTIVE = auto()
    RETURNED = auto()
    OVERDUE = auto()
    LOST = auto()
    DAMAGED = auto()


class LendingRecord:
    """Class representing a record of a book being lent to a user."""
    
    def __init__(self, record_id, book_id, user_id, checkout_date=None):
        """
        Initialize a new lending record.
        
        Args:
            record_id (str): Unique identifier for this lending record
            book_id (str): ID of the book being lent
            user_id (str): ID of the user borrowing the book
            checkout_date (datetime, optional): Date when the book was checked out
        """
        self._record_id = record_id
        self._book_id = book_id
        self._user_id = user_id
        self._checkout_date = checkout_date or datetime.now()
        self._due_date = None
        self._return_date = None
        self._status = LendingStatus.ACTIVE
        self._renewal_count = 0
        self._late_fee = 0.0
        self._notes = ""
    
    @property
    def record_id(self):
        return self._record_id
    
    @property
    def book_id(self):
        return self._book_id
    
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def checkout_date(self):
        return self._checkout_date
    
    @property
    def due_date(self):
        return self._due_date
    
    @due_date.setter
    def due_date(self, value):
        self._due_date = value
    
    @property
    def return_date(self):
        return self._return_date
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if not isinstance(value, LendingStatus):
            raise ValueError("Status must be a LendingStatus enum value")
        self._status = value
    
    @property
    def renewal_count(self):
        return self._renewal_count
    
    @property
    def late_fee(self):
        return self._late_fee
    
    @late_fee.setter
    def late_fee(self, value):
        self._late_fee = float(value)
    
    @property
    def notes(self):
        return self._notes
    
    @notes.setter
    def notes(self, value):
        self._notes = value
    
    def is_overdue(self):
        """Check if the book is overdue."""
        if self._status == LendingStatus.RETURNED:
            return False
        if self._due_date is None:
            return False
        return datetime.now() > self._due_date
    
    def days_overdue(self):
        """Calculate the number of days the book is overdue."""
        if not self.is_overdue():
            return 0
        delta = datetime.now() - self._due_date
        return delta.days
    
    def renew(self, days):
        """
        Renew the lending period.
        
        Args:
            days (int): Number of days to extend the lending period
            
        Returns:
            bool: True if renewal was successful, False otherwise
        """
        if self._status != LendingStatus.ACTIVE:
            return False
        
        if self.is_overdue():
            return False
        
        self._due_date += timedelta(days=days)
        self._renewal_count += 1
        return True
    
    def return_book(self, return_date=None, condition_changed=False):
        """
        Record the return of the book.
        
        Args:
            return_date (datetime, optional): Date when the book was returned
            condition_changed (bool): Whether the book's condition has changed
            
        Returns:
            float: Late fee if applicable, 0 otherwise
        """
        self._return_date = return_date or datetime.now()
        
        if condition_changed:
            self._status = LendingStatus.DAMAGED
        elif self.is_overdue():
            self._status = LendingStatus.OVERDUE
        else:
            self._status = LendingStatus.RETURNED
            
        return self._late_fee
    
    def mark_as_lost(self):
        """Mark the book as lost."""
        self._status = LendingStatus.LOST
    
    def __str__(self):
        status_str = self._status.name.capitalize()
        if self._return_date:
            return f"Lending {self._record_id}: Book {self._book_id} to User {self._user_id} - {status_str} (Returned on {self._return_date.strftime('%Y-%m-%d')})"
        else:
            return f"Lending {self._record_id}: Book {self._book_id} to User {self._user_id} - {status_str} (Due on {self._due_date.strftime('%Y-%m-%d') if self._due_date else 'N/A'})"


class LendingPolicy(ABC):
    """Abstract base class for different lending policies."""
    
    @abstractmethod
    def calculate_due_date(self, book, user, checkout_date):
        """
        Calculate the due date for a book checkout.
        
        Args:
            book: The book being checked out
            user: The user checking out the book
            checkout_date: The date of checkout
            
        Returns:
            datetime: The calculated due date
        """
        pass
    
    @abstractmethod
    def can_renew(self, lending_record, book, user):
        """
        Check if a lending can be renewed.
        
        Args:
            lending_record: The current lending record
            book: The book being renewed
            user: The user renewing the book
            
        Returns:
            bool: True if the book can be renewed, False otherwise
        """
        pass
    
    @abstractmethod
    def get_max_renewals(self, book, user):
        """
        Get the maximum number of renewals allowed.
        
        Args:
            book: The book being renewed
            user: The user renewing the book
            
        Returns:
            int: Maximum number of renewals allowed
        """
        pass


class StandardLendingPolicy(LendingPolicy):
    """Standard lending policy for general books."""
    
    def calculate_due_date(self, book, user, checkout_date):
        """Calculate due date based on book type and user role."""
        lending_period = book.get_lending_period()
        return checkout_date + timedelta(days=lending_period)
    
    def can_renew(self, lending_record, book, user):
        """Check if the book can be renewed under standard policy."""
        if lending_record.is_overdue():
            return False
        
        if lending_record.renewal_count >= self.get_max_renewals(book, user):
            return False
        
        return True
    
    def get_max_renewals(self, book, user):
        """Get maximum renewals based on user role."""
        from models.user import UserRole
        
        role = user.get_role()
        if role == UserRole.LIBRARIAN:
            return 3
        elif role == UserRole.SCHOLAR:
            return 2
        else:  # Guest
            return 1


class RestrictedLendingPolicy(LendingPolicy):
    """Restricted lending policy for rare books and ancient scripts."""
    
    def calculate_due_date(self, book, user, checkout_date):
        """Calculate due date for restricted items."""
        from models.user import UserRole
        
        # Ancient scripts cannot be borrowed
        if book.get_lending_period() == 0:
            return None
        
        # Rare books have shorter lending periods
        role = user.get_role()
        if role == UserRole.LIBRARIAN:
            return checkout_date + timedelta(days=book.get_lending_period())
        elif role == UserRole.SCHOLAR:
            # Scholars get the standard lending period for rare books
            return checkout_date + timedelta(days=book.get_lending_period())
        else:
            # Guests get a shorter period for rare books if they can borrow them at all
            return checkout_date + timedelta(days=3)
    
    def can_renew(self, lending_record, book, user):
        """Check if the restricted item can be renewed."""
        from models.user import UserRole
        
        # Ancient scripts cannot be renewed
        if book.get_lending_period() == 0:
            return False
        
        if lending_record.is_overdue():
            return False
        
        role = user.get_role()
        if role == UserRole.GUEST:
            # Guests cannot renew restricted items
            return False
        
        if lending_record.renewal_count >= self.get_max_renewals(book, user):
            return False
        
        return True
    
    def get_max_renewals(self, book, user):
        """Get maximum renewals for restricted items."""
        from models.user import UserRole
        
        # Ancient scripts cannot be renewed
        if book.get_lending_period() == 0:
            return 0
        
        role = user.get_role()
        if role == UserRole.LIBRARIAN:
            return 2
        elif role == UserRole.SCHOLAR:
            return 1
        else:  # Guest
            return 0
