"""
User Factory implementation for the Enchanted Library system.
This module implements the Factory Pattern for creating different types of users.
"""
import uuid
from models.user import Librarian, Scholar, Guest


class UserFactory:
    """Factory class for creating different types of users."""
    
    @staticmethod
    def create_user(user_type, name, email, password, **kwargs):
        """
        Create a new user of the specified type.
        
        Args:
            user_type (str): Type of user to create ('librarian', 'scholar', or 'guest')
            name (str): Full name of the user
            email (str): Email address of the user
            password (str): Password for authentication
            **kwargs: Additional parameters specific to the user type
            
        Returns:
            User: A new user instance of the specified type
            
        Raises:
            ValueError: If an invalid user type is specified
        """
        # Generate a unique ID for the user
        user_id = str(uuid.uuid4())
        
        # Create the appropriate user type
        if user_type.lower() == 'librarian':
            return UserFactory._create_librarian(user_id, name, email, password, **kwargs)
        elif user_type.lower() == 'scholar':
            return UserFactory._create_scholar(user_id, name, email, password, **kwargs)
        elif user_type.lower() == 'guest':
            return UserFactory._create_guest(user_id, name, email, password, **kwargs)
        else:
            raise ValueError(f"Invalid user type: {user_type}")
    
    @staticmethod
    def _create_librarian(user_id, name, email, password, **kwargs):
        """Create a new librarian user."""
        department = kwargs.get('department')
        staff_id = kwargs.get('staff_id')
        
        librarian = Librarian(user_id, name, email, password, department, staff_id)
        
        # Set additional properties if provided
        if 'admin_level' in kwargs:
            librarian.admin_level = kwargs['admin_level']
        
        return librarian
    
    @staticmethod
    def _create_scholar(user_id, name, email, password, **kwargs):
        """Create a new scholar user."""
        institution = kwargs.get('institution')
        field_of_study = kwargs.get('field_of_study')
        
        scholar = Scholar(user_id, name, email, password, institution, field_of_study)
        
        # Set additional properties if provided
        if 'academic_level' in kwargs:
            scholar.academic_level = kwargs['academic_level']
        
        # Add research topics if provided
        if 'research_topics' in kwargs:
            for topic in kwargs['research_topics']:
                scholar.add_research_topic(topic)
        
        return scholar
    
    @staticmethod
    def _create_guest(user_id, name, email, password, **kwargs):
        """Create a new guest user."""
        address = kwargs.get('address')
        phone = kwargs.get('phone')
        
        guest = Guest(user_id, name, email, password, address, phone)
        
        # Set additional properties if provided
        if 'membership_type' in kwargs:
            guest.membership_type = kwargs['membership_type']
        
        if 'membership_expiry' in kwargs:
            guest.membership_expiry = kwargs['membership_expiry']
        
        return guest
