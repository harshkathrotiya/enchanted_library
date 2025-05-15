import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from database.db_session import Base
from models.book import BookCondition, BookStatus
from models.user import UserRole
from models.lending import LendingStatus

# Association table for books and sections
book_section_association = Table(
    'book_section', Base.metadata,
    Column('book_id', String, ForeignKey('books.book_id')),
    Column('section_id', String, ForeignKey('sections.id'))
)

class Book(Base):
    __tablename__ = 'books'
    
    book_id = Column(String, primary_key=True)
    type = Column(String(50))
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    year_published = Column(Integer, nullable=False)
    isbn = Column(String(20))
    condition = Column(Enum(BookCondition), default=BookCondition.GOOD)
    status = Column(Enum(BookStatus), default=BookStatus.AVAILABLE)
    location = Column(String(255))
    acquisition_date = Column(DateTime, default=datetime.now)
    last_maintenance = Column(DateTime, default=datetime.now)
    quantity = Column(Integer, default=1)
    available_quantity = Column(Integer, default=1)
    
    __mapper_args__ = {
        'polymorphic_identity': 'book',
        'polymorphic_on': type
    }
    
    # Relationships
    sections = relationship("Section", secondary=book_section_association, back_populates="books")
    lending_records = relationship("LendingRecord", back_populates="book")
    
    def __init__(self, book_id, title, author, year_published, isbn=None, quantity=1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.year_published = year_published
        self.isbn = isbn
        self.quantity = max(1, quantity)
        self.available_quantity = self.quantity

class GeneralBook(Book):
    __tablename__ = 'general_books'
    
    book_id = Column(String, ForeignKey('books.book_id'), primary_key=True)
    genre = Column(String(100))
    is_bestseller = Column(Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'general',
    }
    
    def __init__(self, book_id, title, author, year_published, isbn=None, genre=None, is_bestseller=False, quantity=1):
        super().__init__(book_id, title, author, year_published, isbn, quantity)
        self.genre = genre
        self.is_bestseller = is_bestseller

class RareBook(Book):
    __tablename__ = 'rare_books'
    
    book_id = Column(String, ForeignKey('books.book_id'), primary_key=True)
    estimated_value = Column(Float)
    rarity_level = Column(Integer, default=1)
    requires_gloves = Column(Boolean, default=False)
    special_handling_notes = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'rare',
    }
    
    def __init__(self, book_id, title, author, year_published, isbn=None, estimated_value=None, rarity_level=1, special_handling_notes="", quantity=1):
        super().__init__(book_id, title, author, year_published, isbn, quantity)
        self.estimated_value = estimated_value
        self.rarity_level = rarity_level
        self.requires_gloves = rarity_level > 5
        self.special_handling_notes = special_handling_notes

class AncientScript(Book):
    __tablename__ = 'ancient_scripts'
    
    book_id = Column(String, ForeignKey('books.book_id'), primary_key=True)
    origin = Column(String(100))
    language = Column(String(100))
    translation_available = Column(Boolean, default=False)
    digital_copy_available = Column(Boolean, default=False)
    preservation_requirements = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'ancient',
    }
    
    def __init__(self, book_id, title, author, year_published, isbn=None, origin=None, language=None, translation_available=False, quantity=1):
        super().__init__(book_id, title, author, year_published, isbn, quantity)
        self.origin = origin
        self.language = language
        self.translation_available = translation_available
        self.digital_copy_available = False
        self.preservation_requirements = ""

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    type = Column(String(50))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    registration_date = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    active = Column(Boolean, default=True)
    role = Column(Enum(UserRole))
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }
    
    # Relationships
    lending_records = relationship("LendingRecord", back_populates="user")
    
    def __init__(self, user_id, name, email, password):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.registration_date = datetime.now()
        self.active = True

class Librarian(User):
    __tablename__ = 'librarians'
    
    user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    department = Column(String(100))
    staff_id = Column(String(50))
    admin_level = Column(Integer, default=1)
    
    __mapper_args__ = {
        'polymorphic_identity': 'librarian',
    }
    
    def __init__(self, user_id, name, email, password, department=None, staff_id=None, admin_level=1):
        super().__init__(user_id, name, email, password)
        self.department = department
        self.staff_id = staff_id
        self.admin_level = admin_level
        self.role = UserRole.LIBRARIAN

class Scholar(User):
    __tablename__ = 'scholars'
    
    user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    institution = Column(String(255))
    field_of_study = Column(String(255))
    academic_level = Column(String(50), default="General")
    research_topics = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'scholar',
    }
    
    def __init__(self, user_id, name, email, password, institution=None, field_of_study=None, academic_level="General"):
        super().__init__(user_id, name, email, password)
        self.institution = institution
        self.field_of_study = field_of_study
        self.academic_level = academic_level
        self.research_topics = ""
        self.role = UserRole.SCHOLAR

class Guest(User):
    __tablename__ = 'guests'
    
    user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    address = Column(String(255))
    phone = Column(String(20))
    membership_type = Column(String(50), default="Standard")
    membership_expiry = Column(DateTime)
    
    __mapper_args__ = {
        'polymorphic_identity': 'guest',
    }
    
    def __init__(self, user_id, name, email, password, address=None, phone=None, membership_type="Standard", membership_expiry=None):
        super().__init__(user_id, name, email, password)
        self.address = address
        self.phone = phone
        self.membership_type = membership_type
        self.membership_expiry = membership_expiry
        self.role = UserRole.GUEST

class Section(Base):
    __tablename__ = 'sections'
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    access_level = Column(Integer, default=0)
    
    # Relationships
    books = relationship("Book", secondary=book_section_association, back_populates="sections")
    
    def __init__(self, id, name, description, access_level=0):
        self.id = id
        self.name = name
        self.description = description
        self.access_level = access_level

class LendingRecord(Base):
    __tablename__ = 'lending_records'
    
    record_id = Column(String, primary_key=True)
    book_id = Column(String, ForeignKey('books.book_id'), nullable=False)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    checkout_date = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime)
    return_date = Column(DateTime)
    status = Column(Enum(LendingStatus), default=LendingStatus.ACTIVE)
    renewal_count = Column(Integer, default=0)
    late_fee = Column(Float, default=0.0)
    notes = Column(Text)
    
    # Relationships
    book = relationship("Book", back_populates="lending_records")
    user = relationship("User", back_populates="lending_records")
    
    def __init__(self, record_id, book_id, user_id, checkout_date=None):
        self.record_id = record_id
        self.book_id = book_id
        self.user_id = user_id
        self.checkout_date = checkout_date or datetime.now()
        self.renewal_count = 0
        self.late_fee = 0.0
        self.notes = ""
        self.status = LendingStatus.ACTIVE
