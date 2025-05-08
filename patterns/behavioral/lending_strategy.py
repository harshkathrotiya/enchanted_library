"""
Lending Strategy implementation for the Enchanted Library system.
This module implements the Strategy Pattern for different book lending rules.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from models.user import UserRole


class LendingStrategy(ABC):
    """Abstract base class for lending strategies."""
    
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
    def can_borrow(self, book, user):
        """
        Check if a user can borrow a book.
        
        Args:
            book: The book to be borrowed
            user: The user wanting to borrow the book
            
        Returns:
            bool: True if the user can borrow the book, False otherwise
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
    def calculate_late_fee(self, book, days_overdue):
        """
        Calculate the late fee for an overdue book.
        
        Args:
            book: The overdue book
            days_overdue: Number of days the book is overdue
            
        Returns:
            float: The calculated late fee
        """
        pass


class AcademicLendingStrategy(LendingStrategy):
    """Lending strategy for academic users (scholars)."""
    
    def calculate_due_date(self, book, user, checkout_date):
        """Calculate due date for academic users."""
        # Academic users get longer lending periods
        base_period = book.get_lending_period()
        
        # Adjust based on academic level
        if hasattr(user, 'academic_level'):
            level_adjustments = {
                "General": 0,
                "Graduate": 7,
                "Professor": 14,
                "Distinguished": 21
            }
            adjustment = level_adjustments.get(user.academic_level, 0)
        else:
            adjustment = 0
        
        # If the book can't be borrowed, return None
        if base_period == 0:
            return None
        
        return checkout_date + timedelta(days=base_period + adjustment)
    
    def can_borrow(self, book, user):
        """Check if an academic user can borrow a book."""
        # Check if the user is a scholar
        if user.get_role() != UserRole.SCHOLAR:
            return False
        
        # Check if the book can be borrowed at all
        if book.get_lending_period() == 0:
            return False
        
        # Check if the user has access to the book's section
        # This would require knowing the book's section, which we don't have here
        # In a real implementation, we would check this
        
        return True
    
    def can_renew(self, lending_record, book, user):
        """Check if an academic user can renew a book."""
        # Check if the user is a scholar
        if user.get_role() != UserRole.SCHOLAR:
            return False
        
        # Check if the book can be borrowed at all
        if book.get_lending_period() == 0:
            return False
        
        # Check if the lending is overdue
        if lending_record.is_overdue():
            return False
        
        # Scholars can renew up to 3 times
        if lending_record.renewal_count >= 3:
            return False
        
        return True
    
    def calculate_late_fee(self, book, days_overdue):
        """Calculate late fee for academic users."""
        # Academic users have a grace period of 3 days
        adjusted_days = max(0, days_overdue - 3)
        
        # Then use the book's standard late fee calculation
        return book.get_late_fee(adjusted_days)


class PublicLendingStrategy(LendingStrategy):
    """Lending strategy for public users (guests)."""
    
    def calculate_due_date(self, book, user, checkout_date):
        """Calculate due date for public users."""
        # Public users get the standard lending period
        base_period = book.get_lending_period()
        
        # Adjust based on membership type
        if hasattr(user, 'membership_type') and user.membership_type == "Premium":
            adjustment = 7  # Premium members get an extra week
        else:
            adjustment = 0
        
        # If the book can't be borrowed, return None
        if base_period == 0:
            return None
        
        return checkout_date + timedelta(days=base_period + adjustment)
    
    def can_borrow(self, book, user):
        """Check if a public user can borrow a book."""
        # Check if the user is a guest
        if user.get_role() != UserRole.GUEST:
            return False
        
        # Check if the user's membership is valid
        if hasattr(user, 'is_membership_valid') and not user.is_membership_valid():
            return False
        
        # Check if the book can be borrowed at all
        if book.get_lending_period() == 0:
            return False
        
        # Public users can't borrow rare books or ancient scripts
        from models.book import RareBook, AncientScript
        if isinstance(book, RareBook) or isinstance(book, AncientScript):
            return False
        
        return True
    
    def can_renew(self, lending_record, book, user):
        """Check if a public user can renew a book."""
        # Check if the user is a guest
        if user.get_role() != UserRole.GUEST:
            return False
        
        # Check if the user's membership is valid
        if hasattr(user, 'is_membership_valid') and not user.is_membership_valid():
            return False
        
        # Check if the lending is overdue
        if lending_record.is_overdue():
            return False
        
        # Standard members can renew once, premium members twice
        max_renewals = 2 if hasattr(user, 'membership_type') and user.membership_type == "Premium" else 1
        if lending_record.renewal_count >= max_renewals:
            return False
        
        return True
    
    def calculate_late_fee(self, book, days_overdue):
        """Calculate late fee for public users."""
        # Public users pay the standard late fee
        return book.get_late_fee(days_overdue)


class RestrictedReadingRoomStrategy(LendingStrategy):
    """Lending strategy for restricted reading room access."""
    
    def calculate_due_date(self, book, user, checkout_date):
        """Calculate due date for reading room access."""
        # Books in the reading room must be returned the same day
        return checkout_date + timedelta(hours=8)  # 8-hour access
    
    def can_borrow(self, book, user):
        """Check if a user can access a book in the reading room."""
        # Check if the book can be borrowed at all
        if book.get_lending_period() == 0:
            # Ancient scripts can only be viewed in the reading room
            from models.book import AncientScript
            if isinstance(book, AncientScript):
                # Check user's access level
                if user.get_role() == UserRole.LIBRARIAN:
                    return True
                elif user.get_role() == UserRole.SCHOLAR:
                    # Scholars need to be at least at the Professor level
                    if hasattr(user, 'academic_level'):
                        return user.academic_level in ["Professor", "Distinguished"]
                return False
        
        # For other books, check if they're rare
        from models.book import RareBook
        if isinstance(book, RareBook):
            # Check user's access level
            if user.get_role() == UserRole.LIBRARIAN:
                return True
            elif user.get_role() == UserRole.SCHOLAR:
                return True  # All scholars can access rare books in the reading room
            return False
        
        # General books don't need the reading room strategy
        return False
    
    def can_renew(self, lending_record, book, user):
        """Check if reading room access can be renewed."""
        # Reading room access cannot be renewed
        return False
    
    def calculate_late_fee(self, book, days_overdue):
        """Calculate late fee for reading room access."""
        # Higher late fees for reading room items
        base_fee = book.get_late_fee(days_overdue)
        return base_fee * 3  # Triple the standard late fee


class LendingStrategyContext:
    """Context class that uses a lending strategy."""
    
    def __init__(self, strategy=None):
        """
        Initialize the context with a strategy.
        
        Args:
            strategy (LendingStrategy, optional): The lending strategy to use
        """
        self._strategy = strategy
    
    @property
    def strategy(self):
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy
    
    def calculate_due_date(self, book, user, checkout_date=None):
        """
        Calculate the due date using the current strategy.
        
        Args:
            book: The book being checked out
            user: The user checking out the book
            checkout_date: The date of checkout (defaults to now)
            
        Returns:
            datetime: The calculated due date
        """
        if not self._strategy:
            raise ValueError("No lending strategy set")
        
        if checkout_date is None:
            checkout_date = datetime.now()
        
        return self._strategy.calculate_due_date(book, user, checkout_date)
    
    def can_borrow(self, book, user):
        """
        Check if a user can borrow a book using the current strategy.
        
        Args:
            book: The book to be borrowed
            user: The user wanting to borrow the book
            
        Returns:
            bool: True if the user can borrow the book, False otherwise
        """
        if not self._strategy:
            raise ValueError("No lending strategy set")
        
        return self._strategy.can_borrow(book, user)
    
    def can_renew(self, lending_record, book, user):
        """
        Check if a lending can be renewed using the current strategy.
        
        Args:
            lending_record: The current lending record
            book: The book being renewed
            user: The user renewing the book
            
        Returns:
            bool: True if the book can be renewed, False otherwise
        """
        if not self._strategy:
            raise ValueError("No lending strategy set")
        
        return self._strategy.can_renew(lending_record, book, user)
    
    def calculate_late_fee(self, book, days_overdue):
        """
        Calculate the late fee using the current strategy.
        
        Args:
            book: The overdue book
            days_overdue: Number of days the book is overdue
            
        Returns:
            float: The calculated late fee
        """
        if not self._strategy:
            raise ValueError("No lending strategy set")
        
        return self._strategy.calculate_late_fee(book, days_overdue)
    
    def select_strategy_for_book_and_user(self, book, user):
        """
        Automatically select the appropriate strategy based on the book and user.
        
        Args:
            book: The book to be borrowed
            user: The user wanting to borrow the book
            
        Returns:
            LendingStrategy: The selected strategy
        """
        from models.book import AncientScript, RareBook
        
        # Check if the book is an ancient script or rare book that needs reading room access
        if isinstance(book, AncientScript) or (isinstance(book, RareBook) and book.rarity_level >= 8):
            self._strategy = RestrictedReadingRoomStrategy()
        # Check if the user is a scholar
        elif user.get_role() == UserRole.SCHOLAR:
            self._strategy = AcademicLendingStrategy()
        # Otherwise, use the public lending strategy
        else:
            self._strategy = PublicLendingStrategy()
        
        return self._strategy
