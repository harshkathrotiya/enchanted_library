
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, auto

class LendingStatus(Enum):
    ACTIVE = auto()
    RETURNED = auto()
    OVERDUE = auto()
    LOST = auto()
    DAMAGED = auto()

class LendingRecord:
   
    def __init__(self, record_id, book_id, user_id, checkout_date=None):
       
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
       
        if self._status == LendingStatus.RETURNED:
            return False
        if self._due_date is None:
            return False
        return datetime.now() > self._due_date
    
    def days_overdue(self):
        
        if not self.is_overdue():
            return 0
        delta = datetime.now() - self._due_date
        return delta.days
    
    def renew(self, days):
       
        if self._status != LendingStatus.ACTIVE:
            return False
        
        if self.is_overdue():
            return False
        
        self._due_date += timedelta(days=days)
        self._renewal_count += 1
        return True
    
    def return_book(self, return_date=None, condition_changed=False):
        
        self._return_date = return_date or datetime.now()
        
        if condition_changed:
            self._status = LendingStatus.DAMAGED
        elif self.is_overdue():
            self._status = LendingStatus.OVERDUE
        else:
            self._status = LendingStatus.RETURNED
            
        return self._late_fee
    
    def mark_as_lost(self):
        
        self._status = LendingStatus.LOST
    
    def __str__(self):
        status_str = self._status.name.capitalize()
        if self._return_date:
            return f"Lending {self._record_id}: Book {self._book_id} to User {self._user_id} - {status_str} (Returned on {self._return_date.strftime('%Y-%m-%d')})"
        else:
            return f"Lending {self._record_id}: Book {self._book_id} to User {self._user_id} - {status_str} (Due on {self._due_date.strftime('%Y-%m-%d') if self._due_date else 'N/A'})"

class LendingPolicy(ABC):
    
    
    @abstractmethod
    def calculate_due_date(self, book, user, checkout_date):
        
        pass
    
    @abstractmethod
    def can_renew(self, lending_record, book, user):
        
        pass
    
    @abstractmethod
    def get_max_renewals(self, book, user):
        
        pass

class StandardLendingPolicy(LendingPolicy):
    
    
    def calculate_due_date(self, book, user, checkout_date):
        
        lending_period = book.get_lending_period()
        return checkout_date + timedelta(days=lending_period)
    
    def can_renew(self, lending_record, book, user):
        
        if lending_record.is_overdue():
            return False
        
        if lending_record.renewal_count >= self.get_max_renewals(book, user):
            return False
        
        return True
    
    def get_max_renewals(self, book, user):
        
        from models.user import UserRole
        
        role = user.get_role()
        if role == UserRole.LIBRARIAN:
            return 3
        elif role == UserRole.SCHOLAR:
            return 2
        else:
            return 1

class RestrictedLendingPolicy(LendingPolicy):
    
    
    def calculate_due_date(self, book, user, checkout_date):
        
        from models.user import UserRole
        
        if book.get_lending_period() == 0:
            return None
        
        role = user.get_role()
        if role == UserRole.LIBRARIAN:
            return checkout_date + timedelta(days=book.get_lending_period())
        elif role == UserRole.SCHOLAR:
            return checkout_date + timedelta(days=book.get_lending_period())
        else:
            return checkout_date + timedelta(days=3)
    
    def can_renew(self, lending_record, book, user):
        
        from models.user import UserRole
        
        if book.get_lending_period() == 0:
            return False
        
        if lending_record.is_overdue():
            return False
        
        role = user.get_role()
        if role == UserRole.GUEST:
            return False
        
        if lending_record.renewal_count >= self.get_max_renewals(book, user):
            return False
        
        return True
    
    def get_max_renewals(self, book, user):
        
        from models.user import UserRole
        
        if book.get_lending_period() == 0:
            return 0
        
        role = user.get_role()
        if role == UserRole.LIBRARIAN:
            return 2
        elif role == UserRole.SCHOLAR:
            return 1
        else:
            return 0
