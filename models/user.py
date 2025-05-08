"""
User models for the Enchanted Library system.
This module contains the base User class and its specialized subclasses.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto


class UserRole(Enum):
    """Enum representing the different roles a user can have."""
    LIBRARIAN = auto()
    SCHOLAR = auto()
    GUEST = auto()


class User(ABC):
    """Base abstract class for all types of users in the library."""
    
    def __init__(self, user_id, name, email, password):
        """
        Initialize a new User.
        
        Args:
            user_id (str): Unique identifier for the user
            name (str): Full name of the user
            email (str): Email address of the user
            password (str): Hashed password for authentication
        """
        self._user_id = user_id
        self._name = name
        self._email = email
        self._password = password  # In a real system, this would be hashed
        self._registration_date = datetime.now()
        self._last_login = None
        self._active = True
        self._borrowed_books = []
        self._reading_history = []
    
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def name(self):
        return self._name
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        # Simple validation - in a real system, use a proper email validator
        if '@' not in value:
            raise ValueError("Invalid email format")
        self._email = value
    
    @property
    def registration_date(self):
        return self._registration_date
    
    @property
    def last_login(self):
        return self._last_login
    
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, value):
        self._active = bool(value)
    
    @property
    def borrowed_books(self):
        return self._borrowed_books
    
    @property
    def reading_history(self):
        return self._reading_history
    
    def record_login(self):
        """Record the current time as the last login time."""
        self._last_login = datetime.now()
    
    def borrow_book(self, book_id, due_date):
        """Record a book borrowing."""
        self._borrowed_books.append({
            'book_id': book_id,
            'borrow_date': datetime.now(),
            'due_date': due_date,
            'returned': False
        })
    
    def return_book(self, book_id):
        """Record a book return."""
        for book in self._borrowed_books:
            if book['book_id'] == book_id and not book['returned']:
                book['returned'] = True
                book['return_date'] = datetime.now()
                self._reading_history.append(book)
                return True
        return False
    
    def has_overdue_books(self):
        """Check if the user has any overdue books."""
        now = datetime.now()
        return any(not book['returned'] and book['due_date'] < now 
                  for book in self._borrowed_books)
    
    @abstractmethod
    def get_role(self):
        """Return the role of this user."""
        pass
    
    @abstractmethod
    def can_access_section(self, section_name):
        """Check if the user can access a specific library section."""
        pass
    
    @abstractmethod
    def get_max_books(self):
        """Return the maximum number of books this user can borrow at once."""
        pass
    
    def __str__(self):
        return f"{self._name} ({self._email})"


class Librarian(User):
    """Librarian with administrative privileges."""
    
    def __init__(self, user_id, name, email, password, department=None, staff_id=None):
        super().__init__(user_id, name, email, password)
        self._department = department
        self._staff_id = staff_id
        self._admin_level = 1  # 1-3, with 3 being highest
    
    @property
    def department(self):
        return self._department
    
    @property
    def staff_id(self):
        return self._staff_id
    
    @property
    def admin_level(self):
        return self._admin_level
    
    @admin_level.setter
    def admin_level(self, value):
        if value not in [1, 2, 3]:
            raise ValueError("Admin level must be 1, 2, or 3")
        self._admin_level = value
    
    def get_role(self):
        return UserRole.LIBRARIAN
    
    def can_access_section(self, section_name):
        """Librarians can access all sections."""
        return True
    
    def get_max_books(self):
        """Librarians can borrow up to 10 books."""
        return 10
    
    def can_modify_catalog(self):
        """Check if the librarian can modify the catalog."""
        return self._admin_level >= 2
    
    def can_manage_users(self):
        """Check if the librarian can manage user accounts."""
        return self._admin_level >= 2
    
    def can_access_restricted_records(self):
        """Check if the librarian can access restricted records."""
        return self._admin_level == 3


class Scholar(User):
    """Academic user with research privileges."""
    
    def __init__(self, user_id, name, email, password, institution=None, field_of_study=None):
        super().__init__(user_id, name, email, password)
        self._institution = institution
        self._field_of_study = field_of_study
        self._research_topics = []
        self._academic_level = "General"  # General, Graduate, Professor, Distinguished
    
    @property
    def institution(self):
        return self._institution
    
    @property
    def field_of_study(self):
        return self._field_of_study
    
    @property
    def research_topics(self):
        return self._research_topics
    
    def add_research_topic(self, topic):
        """Add a research topic for this scholar."""
        self._research_topics.append(topic)
    
    @property
    def academic_level(self):
        return self._academic_level
    
    @academic_level.setter
    def academic_level(self, value):
        valid_levels = ["General", "Graduate", "Professor", "Distinguished"]
        if value not in valid_levels:
            raise ValueError(f"Academic level must be one of: {', '.join(valid_levels)}")
        self._academic_level = value
    
    def get_role(self):
        return UserRole.SCHOLAR
    
    def can_access_section(self, section_name):
        """Scholars can access most sections, including some restricted ones."""
        restricted_sections = ["Rare Books", "Ancient Manuscripts"]
        if section_name in restricted_sections:
            return self._academic_level in ["Professor", "Distinguished"]
        return True
    
    def get_max_books(self):
        """Scholars can borrow more books based on their academic level."""
        max_books = {
            "General": 5,
            "Graduate": 8,
            "Professor": 12,
            "Distinguished": 15
        }
        return max_books.get(self._academic_level, 5)


class Guest(User):
    """Regular library visitor with basic privileges."""
    
    def __init__(self, user_id, name, email, password, address=None, phone=None):
        super().__init__(user_id, name, email, password)
        self._address = address
        self._phone = phone
        self._membership_type = "Standard"  # Standard, Premium
        self._membership_expiry = None
    
    @property
    def address(self):
        return self._address
    
    @address.setter
    def address(self, value):
        self._address = value
    
    @property
    def phone(self):
        return self._phone
    
    @phone.setter
    def phone(self, value):
        self._phone = value
    
    @property
    def membership_type(self):
        return self._membership_type
    
    @membership_type.setter
    def membership_type(self, value):
        if value not in ["Standard", "Premium"]:
            raise ValueError("Membership type must be Standard or Premium")
        self._membership_type = value
    
    @property
    def membership_expiry(self):
        return self._membership_expiry
    
    @membership_expiry.setter
    def membership_expiry(self, value):
        self._membership_expiry = value
    
    def get_role(self):
        return UserRole.GUEST
    
    def can_access_section(self, section_name):
        """Guests can only access general sections."""
        general_sections = ["Fiction", "Non-Fiction", "Children", "Reference"]
        return section_name in general_sections
    
    def get_max_books(self):
        """Guests can borrow fewer books based on their membership type."""
        return 5 if self._membership_type == "Premium" else 3
    
    def is_membership_valid(self):
        """Check if the guest's membership is still valid."""
        if self._membership_expiry is None:
            return False
        return datetime.now() <= self._membership_expiry
