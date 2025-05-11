
import uuid
from models.user import Librarian, Scholar, Guest

class UserFactory:
    
    
    @staticmethod
    def create_user(user_type, name, email, password, **kwargs):
        
        user_id = str(uuid.uuid4())
        
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
        
        department = kwargs.get('department')
        staff_id = kwargs.get('staff_id')
        
        librarian = Librarian(user_id, name, email, password, department, staff_id)
        
        if 'admin_level' in kwargs:
            librarian.admin_level = kwargs['admin_level']
        
        return librarian
    
    @staticmethod
    def _create_scholar(user_id, name, email, password, **kwargs):
        
        institution = kwargs.get('institution')
        field_of_study = kwargs.get('field_of_study')
        
        scholar = Scholar(user_id, name, email, password, institution, field_of_study)
        
        if 'academic_level' in kwargs:
            scholar.academic_level = kwargs['academic_level']
        
        if 'research_topics' in kwargs:
            for topic in kwargs['research_topics']:
                scholar.add_research_topic(topic)
        
        return scholar
    
    @staticmethod
    def _create_guest(user_id, name, email, password, **kwargs):
        
        address = kwargs.get('address')
        phone = kwargs.get('phone')
        
        guest = Guest(user_id, name, email, password, address, phone)
        
        if 'membership_type' in kwargs:
            guest.membership_type = kwargs['membership_type']
        
        if 'membership_expiry' in kwargs:
            guest.membership_expiry = kwargs['membership_expiry']
        
        return guest
