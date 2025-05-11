
from enum import Enum, auto
from datetime import datetime

class Permission(Enum):
    
    VIEW_BOOK = auto()
    BORROW_BOOK = auto()
    MODIFY_BOOK = auto()
    DELETE_BOOK = auto()
    VIEW_USER = auto()
    MODIFY_USER = auto()
    DELETE_USER = auto()
    VIEW_SECTION = auto()
    MODIFY_SECTION = auto()
    VIEW_LENDING = auto()
    MODIFY_LENDING = auto()
    GENERATE_REPORTS = auto()
    MANAGE_SYSTEM = auto()

class AccessLevel(Enum):
    
    PUBLIC = 0
    RESTRICTED = 1
    HIGHLY_RESTRICTED = 2

class AccessControl:
    
    
    def __init__(self):
        
        self._role_permissions = self._initialize_role_permissions()
        self._section_access_levels = {}
        self._access_logs = []
    
    def _initialize_role_permissions(self):
        
        from models.user import UserRole
        
        permissions = {
            UserRole.LIBRARIAN: {
                Permission.VIEW_BOOK,
                Permission.BORROW_BOOK,
                Permission.MODIFY_BOOK,
                Permission.DELETE_BOOK,
                Permission.VIEW_USER,
                Permission.MODIFY_USER,
                Permission.DELETE_USER,
                Permission.VIEW_SECTION,
                Permission.MODIFY_SECTION,
                Permission.VIEW_LENDING,
                Permission.MODIFY_LENDING,
                Permission.GENERATE_REPORTS,
                Permission.MANAGE_SYSTEM
            },
            UserRole.SCHOLAR: {
                Permission.VIEW_BOOK,
                Permission.BORROW_BOOK,
                Permission.VIEW_SECTION,
                Permission.VIEW_LENDING
            },
            UserRole.GUEST: {
                Permission.VIEW_BOOK,
                Permission.BORROW_BOOK,
                Permission.VIEW_SECTION
            }
        }
        
        return permissions
    
    def set_section_access_level(self, section_id, access_level):
        
        self._section_access_levels[section_id] = access_level
    
    def get_section_access_level(self, section_id):
        
        return self._section_access_levels.get(section_id, AccessLevel.PUBLIC)
    
    def has_permission(self, user, permission):
        
        role = user.get_role()
        
        if role == UserRole.LIBRARIAN:
            if user.admin_level == 1 and permission in [Permission.DELETE_BOOK, Permission.DELETE_USER, Permission.MANAGE_SYSTEM]:
                return False
            
            if user.admin_level == 3:
                return True
        
        role_permissions = self._role_permissions.get(role, set())
        return permission in role_permissions
    
    def can_access_section(self, user, section_id):
        
        access_level = self.get_section_access_level(section_id)
        role = user.get_role()
        
        if role == UserRole.LIBRARIAN:
            if access_level == AccessLevel.HIGHLY_RESTRICTED:
                return user.admin_level == 3
            elif access_level == AccessLevel.RESTRICTED:
                return user.admin_level >= 2
            else:
                return True
        
        elif role == UserRole.SCHOLAR:
            if access_level == AccessLevel.HIGHLY_RESTRICTED:
                return False
            elif access_level == AccessLevel.RESTRICTED:
                return user.academic_level in ["Professor", "Distinguished"]
            else:
                return True
        
        else:
            return access_level == AccessLevel.PUBLIC
    
    def can_borrow_book(self, user, book, section_id=None):
        
        if not self.has_permission(user, Permission.BORROW_BOOK):
            return False
        
        if book.get_lending_period() == 0:
            return False
        
        if section_id and not self.can_access_section(user, section_id):
            return False
        
        from models.book import RareBook, AncientScript
        from models.user import UserRole
        
        role = user.get_role()
        
        if isinstance(book, AncientScript):
            return False
        
        if isinstance(book, RareBook):
            if role == UserRole.GUEST:
                return False
            
            if role == UserRole.SCHOLAR:
                return user.academic_level in ["Graduate", "Professor", "Distinguished"]
        
        return True
    
    def log_access_attempt(self, user_id, resource_type, resource_id, action, success):
        
        self._access_logs.append({
            'timestamp': datetime.now(),
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'success': success
        })
    
    def get_access_logs(self, **filters):
        
        logs = self._access_logs
        
        if 'user_id' in filters:
            logs = [log for log in logs if log['user_id'] == filters['user_id']]
        
        if 'resource_type' in filters:
            logs = [log for log in logs if log['resource_type'] == filters['resource_type']]
        
        if 'resource_id' in filters:
            logs = [log for log in logs if log['resource_id'] == filters['resource_id']]
        
        if 'action' in filters:
            logs = [log for log in logs if log['action'] == filters['action']]
        
        if 'success' in filters:
            logs = [log for log in logs if log['success'] == filters['success']]
        
        if 'start_date' in filters:
            logs = [log for log in logs if log['timestamp'] >= filters['start_date']]
        
        if 'end_date' in filters:
            logs = [log for log in logs if log['timestamp'] <= filters['end_date']]
        
        return logs
