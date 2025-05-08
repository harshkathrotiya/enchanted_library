"""
Data Persistence implementation for the Enchanted Library system.
This module provides functionality to save and load library data to/from JSON files.
"""
import json
from datetime import datetime
import os

from models.book import BookCondition, BookStatus
from models.user import UserRole
from patterns.creational.book_factory import BookFactory
from patterns.creational.user_factory import UserFactory


class DataPersistence:
    """Class for saving and loading library data to/from JSON files."""
    
    @staticmethod
    def save_catalog_to_json(catalog, file_path="library_catalog.json"):
        """
        Save the library catalog to a JSON file.
        
        Args:
            catalog: The library catalog to save
            file_path (str): Path to save the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare data for serialization
            data = {
                "books": [],
                "sections": [],
                "last_updated": datetime.now().isoformat()
            }
            
            # Serialize books
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
                
                # Add book type specific data
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
            
            # Serialize sections
            for section in catalog._sections.values():
                section_data = {
                    "id": section["id"],
                    "name": section["name"],
                    "description": section["description"],
                    "access_level": section["access_level"],
                    "books": section["books"]
                }
                data["sections"].append(section_data)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving catalog to JSON: {e}")
            return False
    
    @staticmethod
    def load_catalog_from_json(catalog, file_path="library_catalog.json"):
        """
        Load the library catalog from a JSON file.
        
        Args:
            catalog: The library catalog to update
            file_path (str): Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        try:
            # Read from file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing data
            catalog._books.clear()
            catalog._sections.clear()
            
            # Load books
            for book_data in data.get("books", []):
                book_type = book_data.get("type", "general")
                
                # Create book based on type
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
                    
                    # Set additional properties
                    book.digital_copy_available = book_data.get("digital_copy_available", False)
                    
                    # Add preservation requirements
                    for req in book_data.get("preservation_requirements", []):
                        book.add_preservation_requirement(req)
                
                # Set common properties
                book.book_id = book_data["book_id"]  # Use the original ID
                book.condition = BookCondition[book_data.get("condition", "GOOD")]
                book.status = BookStatus[book_data.get("status", "AVAILABLE")]
                book.location = book_data.get("location")
                
                # Add to catalog
                catalog._books[book.book_id] = book
            
            # Load sections
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
        """
        Save the library users to a JSON file.
        
        Args:
            catalog: The library catalog containing users
            file_path (str): Path to save the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare data for serialization
            data = {
                "users": [],
                "last_updated": datetime.now().isoformat()
            }
            
            # Serialize users
            for user in catalog._users.values():
                user_data = {
                    "user_id": user.user_id,
                    "name": user.name,
                    "email": user.email,
                    "password": user._password,  # Note: In a real system, this would be hashed
                    "registration_date": user.registration_date.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "active": user.active,
                    "role": user.get_role().name
                }
                
                # Add role specific data
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
                
                # Add borrowed books
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
                
                # Add reading history
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
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving users to JSON: {e}")
            return False
    
    @staticmethod
    def load_users_from_json(catalog, file_path="library_users.json"):
        """
        Load the library users from a JSON file.
        
        Args:
            catalog: The library catalog to update
            file_path (str): Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        try:
            # Read from file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing users
            catalog._users.clear()
            
            # Load users
            for user_data in data.get("users", []):
                role = user_data.get("role", "GUEST")
                
                # Create user based on role
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
                    
                    # Add research topics
                    for topic in user_data.get("research_topics", []):
                        user.add_research_topic(topic)
                
                else:  # GUEST
                    user = UserFactory.create_user(
                        "guest",
                        user_data["name"],
                        user_data["email"],
                        user_data["password"],
                        address=user_data.get("address"),
                        phone=user_data.get("phone"),
                        membership_type=user_data.get("membership_type", "Standard")
                    )
                    
                    # Set membership expiry
                    if user_data.get("membership_expiry"):
                        user.membership_expiry = datetime.fromisoformat(user_data["membership_expiry"])
                
                # Set common properties
                user.user_id = user_data["user_id"]  # Use the original ID
                user._registration_date = datetime.fromisoformat(user_data["registration_date"])
                if user_data.get("last_login"):
                    user._last_login = datetime.fromisoformat(user_data["last_login"])
                user.active = user_data.get("active", True)
                
                # Add borrowed books
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
                
                # Add reading history
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
                
                # Add to catalog
                catalog._users[user.user_id] = user
            
            return True
        
        except Exception as e:
            print(f"Error loading users from JSON: {e}")
            return False
