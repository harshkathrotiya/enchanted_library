
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from models.user import UserRole
from models.book import BookCondition

class LendingStrategy(ABC):

    @abstractmethod
    def calculate_due_date(self, book, user, checkout_date):

        pass

    @abstractmethod
    def can_borrow(self, book, user):

        pass

    @abstractmethod
    def can_renew(self, lending_record, book, user):

        pass

    @abstractmethod
    def calculate_late_fee(self, book, days_overdue):

        pass

class AcademicLendingStrategy(LendingStrategy):

    def calculate_due_date(self, book, user, checkout_date):

        base_period = book.get_lending_period()

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

        if base_period == 0:
            return None

        return checkout_date + timedelta(days=base_period + adjustment)

    def can_borrow(self, book, user):

        if user.get_role() != UserRole.SCHOLAR:
            return False

        if book.get_lending_period() == 0:
            return False

        return True

    def can_renew(self, lending_record, book, user):

        if user.get_role() != UserRole.SCHOLAR:
            return False

        if book.get_lending_period() == 0:
            return False

        if lending_record.is_overdue():
            return False

        if lending_record.renewal_count >= 3:
            return False

        return True

    def calculate_late_fee(self, book, days_overdue):

        adjusted_days = max(0, days_overdue - 3)

        return book.get_late_fee(adjusted_days)

class PublicLendingStrategy(LendingStrategy):

    def calculate_due_date(self, book, user, checkout_date):

        base_period = book.get_lending_period()

        if hasattr(user, 'membership_type') and user.membership_type == "Premium":
            adjustment = 7
        else:
            adjustment = 0

        if base_period == 0:
            return None

        return checkout_date + timedelta(days=base_period + adjustment)

    def can_borrow(self, book, user):

        if user.get_role() != UserRole.GUEST:
            return False

        if hasattr(user, 'is_membership_valid') and not user.is_membership_valid():
            return False

        if book.get_lending_period() == 0:
            return False

        from models.book import RareBook, AncientScript
        if isinstance(book, RareBook) or isinstance(book, AncientScript):
            return False

        return True

    def can_renew(self, lending_record, book, user):

        if user.get_role() != UserRole.GUEST:
            return False

        if hasattr(user, 'is_membership_valid') and not user.is_membership_valid():
            return False

        if lending_record.is_overdue():
            return False

        max_renewals = 2 if hasattr(user, 'membership_type') and user.membership_type == "Premium" else 1
        if lending_record.renewal_count >= max_renewals:
            return False

        return True

    def calculate_late_fee(self, book, days_overdue):

        return book.get_late_fee(days_overdue)

class RestrictedReadingRoomStrategy(LendingStrategy):

    def calculate_due_date(self, book, user, checkout_date):

        return checkout_date + timedelta(hours=8)

    def can_borrow(self, book, user):

       
        if book.get_lending_period() == 0:
          
            from models.book import AncientScript
            if isinstance(book, AncientScript):
               
                if user.get_role() == UserRole.LIBRARIAN:
                    return True
                elif user.get_role() == UserRole.SCHOLAR:
                    if hasattr(user, 'academic_level'):
                        return user.academic_level in ["Professor", "Distinguished"]
                return False

        from models.book import RareBook
        if isinstance(book, RareBook):
            if user.get_role() == UserRole.LIBRARIAN:
                return True
            elif user.get_role() == UserRole.SCHOLAR:
                return True
            return False

        return False

    def can_renew(self, lending_record, book, user):

        return False

    def calculate_late_fee(self, book, days_overdue):

        base_fee = book.get_late_fee(days_overdue)
        return base_fee * 3

class SeasonalLendingStrategy(LendingStrategy):
   

    def __init__(self, season_name="Summer Reading", extension_days=7, discount_factor=0.5):
        
        self._season_name = season_name
        self._extension_days = extension_days
        self._discount_factor = discount_factor

    @property
    def season_name(self):
        return self._season_name

    def calculate_due_date(self, book, user, checkout_date):
        
        base_period = book.get_lending_period()

        if base_period == 0:
            return None

        return checkout_date + timedelta(days=base_period + self._extension_days)

    def can_borrow(self, book, user):
       
        if book.get_lending_period() == 0:
            return False

        from models.book import RareBook, AncientScript

        if isinstance(book, AncientScript):
            return False

        if isinstance(book, RareBook):
            if user.get_role() == UserRole.GUEST:
                return book.rarity_level <= 3
            else:
                return True

        return True

    def can_renew(self, lending_record, book, user):
        
        if lending_record.is_overdue():
            return False

        max_renewals = 2

        if user.get_role() == UserRole.LIBRARIAN:
            max_renewals = 4
        elif user.get_role() == UserRole.SCHOLAR:
            max_renewals = 3

        if lending_record.renewal_count >= max_renewals:
            return False

        return True

    def calculate_late_fee(self, book, days_overdue):
        
        base_fee = book.get_late_fee(days_overdue)

        return base_fee * self._discount_factor

class ResearchProjectStrategy(LendingStrategy):
    

    def __init__(self, project_name, project_end_date, max_books=10):
        
        self._project_name = project_name
        self._project_end_date = project_end_date
        self._max_books = max_books
        self._project_books = []

    @property
    def project_name(self):
        return self._project_name

    @property
    def project_end_date(self):
        return self._project_end_date

    @property
    def max_books(self):
        return self._max_books

    @property
    def project_books(self):
        return self._project_books

    def add_project_book(self, book_id):
        
        if book_id not in self._project_books:
            self._project_books.append(book_id)

    def calculate_due_date(self, book, user, checkout_date):
        
        max_days = 90

        days_until_end = (self._project_end_date - checkout_date).days

        lending_days = min(days_until_end, max_days)

        if lending_days <= 0:
            return None

        return checkout_date + timedelta(days=lending_days)

    def can_borrow(self, book, user):
        
        if datetime.now() > self._project_end_date:
            return False

        if len(self._project_books) >= self._max_books:
            return book.book_id in self._project_books

        if book.get_lending_period() == 0:
            return False

        from models.book import RareBook, AncientScript

        if isinstance(book, AncientScript):
            self.add_project_book(book.book_id)
            return False

        self.add_project_book(book.book_id)
        return True

    def can_renew(self, lending_record, book, user):
        
        if datetime.now() > self._project_end_date:
            return False

        if lending_record.is_overdue():
            return False

        if book.book_id in self._project_books:
            potential_due_date = lending_record.due_date + timedelta(days=14)
            return potential_due_date <= self._project_end_date

        return lending_record.renewal_count < 2

    def calculate_late_fee(self, book, days_overdue):
        
        base_fee = book.get_late_fee(days_overdue)

        if book.book_id in self._project_books:
            return base_fee * 1.5

        return base_fee

class LendingStrategyContext:
    

    def __init__(self, strategy=None):
        
        self._strategy = strategy
        self._seasonal_strategies = {}
        self._research_projects = {}

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy

    def add_seasonal_strategy(self, season_name, start_date, end_date, extension_days=7, discount_factor=0.5):
        
        self._seasonal_strategies[season_name] = {
            'strategy': SeasonalLendingStrategy(season_name, extension_days, discount_factor),
            'start_date': start_date,
            'end_date': end_date
        }

    def add_research_project(self, project_name, project_end_date, max_books=10):
        
        self._research_projects[project_name] = ResearchProjectStrategy(
            project_name, project_end_date, max_books
        )

    def get_research_project(self, project_name):
        
        return self._research_projects.get(project_name)

    def calculate_due_date(self, book, user, checkout_date=None):
        
        if not self._strategy:
            raise ValueError("No lending strategy set")

        if checkout_date is None:
            checkout_date = datetime.now()

        return self._strategy.calculate_due_date(book, user, checkout_date)

    def can_borrow(self, book, user):
        
        if not self._strategy:
            raise ValueError("No lending strategy set")

        return self._strategy.can_borrow(book, user)

    def can_renew(self, lending_record, book, user):
        
        if not self._strategy:
            raise ValueError("No lending strategy set")

        return self._strategy.can_renew(lending_record, book, user)

    def calculate_late_fee(self, book, days_overdue):
        
        if not self._strategy:
            raise ValueError("No lending strategy set")

        return self._strategy.calculate_late_fee(book, days_overdue)

    def select_strategy_for_book_and_user(self, book, user):
        
        from models.book import AncientScript, RareBook

        now = datetime.now()
        for season_info in self._seasonal_strategies.values():
            if season_info['start_date'] <= now <= season_info['end_date']:
                self._strategy = season_info['strategy']
                return self._strategy

        if isinstance(book, AncientScript) or (isinstance(book, RareBook) and book.rarity_level >= 8):
            self._strategy = RestrictedReadingRoomStrategy()
        elif user.get_role() == UserRole.SCHOLAR:
            self._strategy = AcademicLendingStrategy()
        else:
            self._strategy = PublicLendingStrategy()

        return self._strategy

    def select_research_project_strategy(self, project_name):
        
        if project_name in self._research_projects:
            self._strategy = self._research_projects[project_name]
            return True
        return False
