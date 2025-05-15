
import json
from datetime import datetime
import os
import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from models.book import BookCondition, BookStatus
from models.user import UserRole
from models.lending import LendingStatus
from patterns.creational.book_factory import BookFactory
from patterns.creational.user_factory import UserFactory
from database.db_session import db_session, init_db
from database.models import Book as DBBook
from database.models import GeneralBook as DBGeneralBook
from database.models import RareBook as DBRareBook
from database.models import AncientScript as DBAncientScript
from database.models import User as DBUser
from database.models import Librarian as DBLibrarian
from database.models import Scholar as DBScholar
from database.models import Guest as DBGuest
from database.models import Section as DBSection
from database.models import LendingRecord as DBLendingRecord

class DataPersistence:

    @staticmethod
    def initialize_database():
        try:
            init_db()
            return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False

    @staticmethod
    def save_catalog_to_database(catalog):
        try:
            # Save books
            for book in catalog._books.values():
                db_book = db_session.query(DBBook).filter_by(book_id=book.book_id).first()

                if db_book is None:
                    # Create new book
                    from models.book import GeneralBook, RareBook, AncientScript

                    if isinstance(book, GeneralBook):
                        db_book = DBGeneralBook(
                            book_id=book.book_id,
                            title=book.title,
                            author=book.author,
                            year_published=book.year_published,
                            isbn=book.isbn,
                            genre=book.genre,
                            is_bestseller=book.is_bestseller,
                            quantity=book.quantity
                        )

                    elif isinstance(book, RareBook):
                        db_book = DBRareBook(
                            book_id=book.book_id,
                            title=book.title,
                            author=book.author,
                            year_published=book.year_published,
                            isbn=book.isbn,
                            estimated_value=book.estimated_value,
                            rarity_level=book.rarity_level,
                            special_handling_notes=book.special_handling_notes,
                            quantity=book.quantity
                        )

                    elif isinstance(book, AncientScript):
                        db_book = DBAncientScript(
                            book_id=book.book_id,
                            title=book.title,
                            author=book.author,
                            year_published=book.year_published,
                            isbn=book.isbn,
                            origin=book.origin,
                            language=book.language,
                            translation_available=book.translation_available,
                            quantity=book.quantity
                        )

                        db_book.digital_copy_available = book.digital_copy_available
                        db_book.preservation_requirements = "\n".join(book.preservation_requirements)

                    db_book.condition = book.condition
                    db_book.status = book.status
                    db_book.location = book.location
                    db_book.available_quantity = book.available_quantity

                    db_session.add(db_book)
                else:
                    # Update existing book
                    db_book.title = book.title
                    db_book.author = book.author
                    db_book.year_published = book.year_published
                    db_book.isbn = book.isbn
                    db_book.condition = book.condition
                    db_book.status = book.status
                    db_book.location = book.location
                    db_book.quantity = book.quantity
                    db_book.available_quantity = book.available_quantity

                    from models.book import GeneralBook, RareBook, AncientScript

                    if isinstance(book, GeneralBook) and isinstance(db_book, DBGeneralBook):
                        db_book.genre = book.genre
                        db_book.is_bestseller = book.is_bestseller

                    elif isinstance(book, RareBook) and isinstance(db_book, DBRareBook):
                        db_book.estimated_value = book.estimated_value
                        db_book.rarity_level = book.rarity_level
                        db_book.requires_gloves = book.requires_gloves
                        db_book.special_handling_notes = book.special_handling_notes

                    elif isinstance(book, AncientScript) and isinstance(db_book, DBAncientScript):
                        db_book.origin = book.origin
                        db_book.language = book.language
                        db_book.translation_available = book.translation_available
                        db_book.digital_copy_available = book.digital_copy_available
                        db_book.preservation_requirements = "\n".join(book.preservation_requirements)

            # Save sections
            for section in catalog._sections.values():
                db_section = db_session.query(DBSection).filter_by(id=section["id"]).first()

                if db_section is None:
                    # Create new section
                    db_section = DBSection(
                        id=section["id"],
                        name=section["name"],
                        description=section["description"],
                        access_level=section["access_level"]
                    )
                    db_session.add(db_section)
                else:
                    # Update existing section
                    db_section.name = section["name"]
                    db_section.description = section["description"]
                    db_section.access_level = section["access_level"]

                # Clear existing book associations
                db_section.books = []

                # Add book associations
                for book_id in section["books"]:
                    db_book = db_session.query(DBBook).filter_by(book_id=book_id).first()
                    if db_book:
                        db_section.books.append(db_book)

            db_session.commit()
            return True

        except Exception as e:
            db_session.rollback()
            print(f"Error saving catalog to database: {e}")
            return False

    @staticmethod
    def load_catalog_from_database(catalog):
        try:
            catalog._books.clear()
            catalog._sections.clear()

            # Load books
            db_books = db_session.query(DBBook).all()

            for db_book in db_books:
                try:
                    # Get the book ID from the database
                    book_id = db_book.book_id

                    if isinstance(db_book, DBGeneralBook):
                        # Use the factory's internal methods to avoid setter issues
                        book = BookFactory._create_general_book(
                            book_id,
                            db_book.title,
                            db_book.author,
                            db_book.year_published,
                            isbn=db_book.isbn,
                            genre=db_book.genre,
                            is_bestseller=db_book.is_bestseller
                        )

                    elif isinstance(db_book, DBRareBook):
                        book = BookFactory._create_rare_book(
                            book_id,
                            db_book.title,
                            db_book.author,
                            db_book.year_published,
                            isbn=db_book.isbn,
                            estimated_value=db_book.estimated_value,
                            rarity_level=db_book.rarity_level,
                            special_handling_notes=db_book.special_handling_notes
                        )

                    elif isinstance(db_book, DBAncientScript):
                        book = BookFactory._create_ancient_script(
                            book_id,
                            db_book.title,
                            db_book.author,
                            db_book.year_published,
                            isbn=db_book.isbn,
                            origin=db_book.origin,
                            language=db_book.language,
                            translation_available=db_book.translation_available
                        )

                        book.digital_copy_available = db_book.digital_copy_available

                        if db_book.preservation_requirements:
                            for req in db_book.preservation_requirements.split("\n"):
                                if req.strip():
                                    book.add_preservation_requirement(req.strip())

                    # Set properties using direct attribute access or setters as appropriate
                    book.condition = db_book.condition
                    book.status = db_book.status
                    book.location = db_book.location
                    book.quantity = db_book.quantity
                    book._available_quantity = db_book.available_quantity

                    catalog._books[book.book_id] = book
                except Exception as e:
                    print(f"Error loading book {db_book.title} from database: {e}")

            # Load sections
            db_sections = db_session.query(DBSection).all()

            for db_section in db_sections:
                try:
                    section = {
                        "id": db_section.id,
                        "name": db_section.name,
                        "description": db_section.description,
                        "access_level": db_section.access_level,
                        "books": [book.book_id for book in db_section.books]
                    }
                    catalog._sections[section["id"]] = section
                except Exception as e:
                    print(f"Error loading section {db_section.name} from database: {e}")

            return True

        except Exception as e:
            print(f"Error loading catalog from database: {e}")
            return False

    @staticmethod
    def save_users_to_database(catalog):
        success = True

        # Save users one by one to handle potential errors individually
        for user in catalog._users.values():
            try:
                # Check if user with this email already exists but with different ID
                existing_email = db_session.query(DBUser).filter_by(email=user.email).first()
                if existing_email and existing_email.user_id != user.user_id:
                    print(f"Warning: User with email {user.email} already exists with different ID. Skipping.")
                    continue

                db_user = db_session.query(DBUser).filter_by(user_id=user.user_id).first()

                if db_user is None:
                    # Create new user
                    if user.get_role() == UserRole.LIBRARIAN:
                        db_user = DBLibrarian(
                            user_id=user.user_id,
                            name=user.name,
                            email=user.email,
                            password=user._password,
                            department=user.department,
                            staff_id=user.staff_id,
                            admin_level=user.admin_level
                        )

                    elif user.get_role() == UserRole.SCHOLAR:
                        db_user = DBScholar(
                            user_id=user.user_id,
                            name=user.name,
                            email=user.email,
                            password=user._password,
                            institution=user.institution,
                            field_of_study=user.field_of_study,
                            academic_level=user.academic_level
                        )

                        db_user.research_topics = "\n".join(user.research_topics)

                    elif user.get_role() == UserRole.GUEST:
                        db_user = DBGuest(
                            user_id=user.user_id,
                            name=user.name,
                            email=user.email,
                            password=user._password,
                            address=user.address,
                            phone=user.phone,
                            membership_type=user.membership_type,
                            membership_expiry=user.membership_expiry
                        )

                    db_user.registration_date = user.registration_date
                    db_user.last_login = user.last_login
                    db_user.active = user.active

                    db_session.add(db_user)
                    db_session.commit()
                else:
                    # Update existing user
                    db_user.name = user.name
                    # Only update email if it's not already taken by another user
                    if db_user.email != user.email:
                        existing_email = db_session.query(DBUser).filter_by(email=user.email).first()
                        if not existing_email or existing_email.user_id == user.user_id:
                            db_user.email = user.email

                    db_user.password = user._password
                    db_user.last_login = user.last_login
                    db_user.active = user.active

                    if user.get_role() == UserRole.LIBRARIAN and isinstance(db_user, DBLibrarian):
                        db_user.department = user.department
                        db_user.staff_id = user.staff_id
                        db_user.admin_level = user.admin_level

                    elif user.get_role() == UserRole.SCHOLAR and isinstance(db_user, DBScholar):
                        db_user.institution = user.institution
                        db_user.field_of_study = user.field_of_study
                        db_user.academic_level = user.academic_level
                        db_user.research_topics = "\n".join(user.research_topics)

                    elif user.get_role() == UserRole.GUEST and isinstance(db_user, DBGuest):
                        db_user.address = user.address
                        db_user.phone = user.phone
                        db_user.membership_type = user.membership_type
                        db_user.membership_expiry = user.membership_expiry

                    db_session.commit()
            except Exception as e:
                db_session.rollback()
                print(f"Error saving user {user.name} to database: {e}")
                success = False

        # Save lending records
        for record in catalog._lending_records.values():
            try:
                db_record = db_session.query(DBLendingRecord).filter_by(record_id=record.record_id).first()

                if db_record is None:
                    # Create new lending record
                    db_record = DBLendingRecord(
                        record_id=record.record_id,
                        book_id=record.book_id,
                        user_id=record.user_id,
                        checkout_date=record.checkout_date
                    )
                    db_session.add(db_record)

                # Update record fields
                db_record.due_date = record.due_date
                db_record.return_date = record.return_date
                db_record.status = record.status
                db_record.renewal_count = record.renewal_count
                db_record.late_fee = record.late_fee
                db_record.notes = record.notes

                db_session.commit()
            except Exception as e:
                db_session.rollback()
                print(f"Error saving lending record {record.record_id} to database: {e}")
                success = False

        return success

    @staticmethod
    def load_users_from_database(catalog):
        try:
            catalog._users.clear()
            catalog._lending_records.clear()

            # Load users
            db_users = db_session.query(DBUser).all()

            for db_user in db_users:
                try:
                    # Create user with the same ID from the database
                    user_id = db_user.user_id

                    if isinstance(db_user, DBLibrarian):
                        user = UserFactory._create_librarian(
                            user_id,
                            db_user.name,
                            db_user.email,
                            db_user.password,
                            department=db_user.department,
                            staff_id=db_user.staff_id
                        )
                        user.admin_level = db_user.admin_level

                    elif isinstance(db_user, DBScholar):
                        user = UserFactory._create_scholar(
                            user_id,
                            db_user.name,
                            db_user.email,
                            db_user.password,
                            institution=db_user.institution,
                            field_of_study=db_user.field_of_study
                        )
                        user.academic_level = db_user.academic_level

                        if db_user.research_topics:
                            for topic in db_user.research_topics.split("\n"):
                                if topic.strip():
                                    user.add_research_topic(topic.strip())

                    else:  # Guest
                        user = UserFactory._create_guest(
                            user_id,
                            db_user.name,
                            db_user.email,
                            db_user.password,
                            address=db_user.address,
                            phone=db_user.phone
                        )
                        user.membership_type = db_user.membership_type
                        user.membership_expiry = db_user.membership_expiry

                    # Set other properties using direct attribute access to avoid setter issues
                    user._registration_date = db_user.registration_date
                    user._last_login = db_user.last_login
                    user.active = db_user.active

                    catalog._users[user.user_id] = user
                except Exception as e:
                    print(f"Error loading user {db_user.name} from database: {e}")

            # Load lending records
            from models.lending import LendingRecord

            db_records = db_session.query(DBLendingRecord).all()

            for db_record in db_records:
                try:
                    record = LendingRecord(
                        db_record.record_id,
                        db_record.book_id,
                        db_record.user_id,
                        db_record.checkout_date
                    )

                    # Use direct attribute access to avoid setter issues
                    record.due_date = db_record.due_date
                    record._return_date = db_record.return_date
                    record._status = db_record.status
                    record._renewal_count = db_record.renewal_count
                    record._late_fee = db_record.late_fee
                    record._notes = db_record.notes

                    catalog._lending_records[record.record_id] = record
                except Exception as e:
                    print(f"Error loading lending record {db_record.record_id} from database: {e}")

            return True

        except Exception as e:
            print(f"Error loading users from database: {e}")
            return False

    # Legacy methods for backward compatibility
    @staticmethod
    def save_catalog_to_json(catalog, file_path="library_catalog.json"):
        print("Warning: Using legacy JSON persistence. Consider using database persistence instead.")
        try:
            data = {
                "books": [],
                "sections": [],
                "last_updated": datetime.now().isoformat()
            }

            for book in catalog._books.values():
                book_data = {
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "year_published": book.year_published,
                    "isbn": book.isbn,
                    "condition": book.condition.name,
                    "status": book.status.name,
                    "location": book.location
                }

                from models.book import GeneralBook, RareBook, AncientScript

                if isinstance(book, GeneralBook):
                    book_data["type"] = "general"
                    book_data["genre"] = book.genre
                    book_data["is_bestseller"] = book.is_bestseller

                elif isinstance(book, RareBook):
                    book_data["type"] = "rare"
                    book_data["estimated_value"] = book.estimated_value
                    book_data["rarity_level"] = book.rarity_level
                    book_data["special_handling_notes"] = book.special_handling_notes

                elif isinstance(book, AncientScript):
                    book_data["type"] = "ancient"
                    book_data["origin"] = book.origin
                    book_data["language"] = book.language
                    book_data["translation_available"] = book.translation_available
                    book_data["digital_copy_available"] = book.digital_copy_available
                    book_data["preservation_requirements"] = book.preservation_requirements

                data["books"].append(book_data)

            for section in catalog._sections.values():
                section_data = {
                    "id": section["id"],
                    "name": section["name"],
                    "description": section["description"],
                    "access_level": section["access_level"],
                    "books": section["books"]
                }
                data["sections"].append(section_data)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving catalog to JSON: {e}")
            return False

    @staticmethod
    def load_catalog_from_json(catalog, file_path="library_catalog.json"):
        print("Warning: Using legacy JSON persistence. Consider using database persistence instead.")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            catalog._books.clear()
            catalog._sections.clear()

            for book_data in data.get("books", []):
                book_type = book_data.get("type", "general")

                if book_type == "general":
                    book = BookFactory.create_book(
                        "general",
                        book_data["title"],
                        book_data["author"],
                        book_data["year_published"],
                        isbn=book_data.get("isbn"),
                        genre=book_data.get("genre"),
                        is_bestseller=book_data.get("is_bestseller", False)
                    )

                elif book_type == "rare":
                    book = BookFactory.create_book(
                        "rare",
                        book_data["title"],
                        book_data["author"],
                        book_data["year_published"],
                        isbn=book_data.get("isbn"),
                        estimated_value=book_data.get("estimated_value"),
                        rarity_level=book_data.get("rarity_level", 1),
                        special_handling_notes=book_data.get("special_handling_notes", "")
                    )

                elif book_type == "ancient":
                    book = BookFactory.create_book(
                        "ancient",
                        book_data["title"],
                        book_data["author"],
                        book_data["year_published"],
                        isbn=book_data.get("isbn"),
                        origin=book_data.get("origin"),
                        language=book_data.get("language"),
                        translation_available=book_data.get("translation_available", False)
                    )

                    book.digital_copy_available = book_data.get("digital_copy_available", False)

                    for req in book_data.get("preservation_requirements", []):
                        book.add_preservation_requirement(req)

                book.book_id = book_data["book_id"]
                book.condition = BookCondition[book_data.get("condition", "GOOD")]
                book.status = BookStatus[book_data.get("status", "AVAILABLE")]
                book.location = book_data.get("location")

                catalog._books[book.book_id] = book

            for section_data in data.get("sections", []):
                section = {
                    "id": section_data["id"],
                    "name": section_data["name"],
                    "description": section_data["description"],
                    "access_level": section_data["access_level"],
                    "books": section_data["books"]
                }
                catalog._sections[section["id"]] = section

            return True

        except Exception as e:
            print(f"Error loading catalog from JSON: {e}")
            return False

    @staticmethod
    def save_users_to_json(catalog, file_path="library_users.json"):
        print("Warning: Using legacy JSON persistence. Consider using database persistence instead.")
        try:
            data = {
                "users": [],
                "last_updated": datetime.now().isoformat()
            }

            for user in catalog._users.values():
                user_data = {
                    "user_id": user.user_id,
                    "name": user.name,
                    "email": user.email,
                    "password": user._password,
                    "registration_date": user.registration_date.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "active": user.active,
                    "role": user.get_role().name
                }

                if user.get_role() == UserRole.LIBRARIAN:
                    user_data["department"] = user.department
                    user_data["staff_id"] = user.staff_id
                    user_data["admin_level"] = user.admin_level

                elif user.get_role() == UserRole.SCHOLAR:
                    user_data["institution"] = user.institution
                    user_data["field_of_study"] = user.field_of_study
                    user_data["academic_level"] = user.academic_level
                    user_data["research_topics"] = user.research_topics

                elif user.get_role() == UserRole.GUEST:
                    user_data["address"] = user.address
                    user_data["phone"] = user.phone
                    user_data["membership_type"] = user.membership_type
                    user_data["membership_expiry"] = user.membership_expiry.isoformat() if user.membership_expiry else None

                user_data["borrowed_books"] = []
                for book in user.borrowed_books:
                    book_data = {
                        "book_id": book["book_id"],
                        "borrow_date": book["borrow_date"].isoformat(),
                        "due_date": book["due_date"].isoformat(),
                        "returned": book["returned"],
                        "return_date": book.get("return_date").isoformat() if book.get("return_date") else None
                    }
                    user_data["borrowed_books"].append(book_data)

                user_data["reading_history"] = []
                for book in user.reading_history:
                    book_data = {
                        "book_id": book["book_id"],
                        "borrow_date": book["borrow_date"].isoformat(),
                        "due_date": book["due_date"].isoformat(),
                        "returned": book["returned"],
                        "return_date": book.get("return_date").isoformat() if book.get("return_date") else None
                    }
                    user_data["reading_history"].append(book_data)

                data["users"].append(user_data)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving users to JSON: {e}")
            return False

    @staticmethod
    def load_users_from_json(catalog, file_path="library_users.json"):
        print("Warning: Using legacy JSON persistence. Consider using database persistence instead.")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            catalog._users.clear()

            for user_data in data.get("users", []):
                role = user_data.get("role", "GUEST")

                if role == "LIBRARIAN":
                    user = UserFactory.create_user(
                        "librarian",
                        user_data["name"],
                        user_data["email"],
                        user_data["password"],
                        department=user_data.get("department"),
                        staff_id=user_data.get("staff_id"),
                        admin_level=user_data.get("admin_level", 1)
                    )

                elif role == "SCHOLAR":
                    user = UserFactory.create_user(
                        "scholar",
                        user_data["name"],
                        user_data["email"],
                        user_data["password"],
                        institution=user_data.get("institution"),
                        field_of_study=user_data.get("field_of_study"),
                        academic_level=user_data.get("academic_level", "General")
                    )

                    for topic in user_data.get("research_topics", []):
                        user.add_research_topic(topic)

                else:
                    user = UserFactory.create_user(
                        "guest",
                        user_data["name"],
                        user_data["email"],
                        user_data["password"],
                        address=user_data.get("address"),
                        phone=user_data.get("phone"),
                        membership_type=user_data.get("membership_type", "Standard")
                    )

                    if user_data.get("membership_expiry"):
                        user.membership_expiry = datetime.fromisoformat(user_data["membership_expiry"])

                user.user_id = user_data["user_id"]
                user._registration_date = datetime.fromisoformat(user_data["registration_date"])
                if user_data.get("last_login"):
                    user._last_login = datetime.fromisoformat(user_data["last_login"])
                user.active = user_data.get("active", True)

                for book in user_data.get("borrowed_books", []):
                    borrowed_book = {
                        "book_id": book["book_id"],
                        "borrow_date": datetime.fromisoformat(book["borrow_date"]),
                        "due_date": datetime.fromisoformat(book["due_date"]),
                        "returned": book["returned"]
                    }
                    if book.get("return_date"):
                        borrowed_book["return_date"] = datetime.fromisoformat(book["return_date"])
                    user._borrowed_books.append(borrowed_book)

                for book in user_data.get("reading_history", []):
                    history_book = {
                        "book_id": book["book_id"],
                        "borrow_date": datetime.fromisoformat(book["borrow_date"]),
                        "due_date": datetime.fromisoformat(book["due_date"]),
                        "returned": book["returned"]
                    }
                    if book.get("return_date"):
                        history_book["return_date"] = datetime.fromisoformat(book["return_date"])
                    user._reading_history.append(history_book)

                catalog._users[user.user_id] = user

            return True

        except Exception as e:
            print(f"Error loading users from JSON: {e}")
            return False
