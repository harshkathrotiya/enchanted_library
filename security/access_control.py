"""
Access Control implementation for the Enchanted Library system.
This module implements role-based access control for library resources.
"""
from enum import Enum, auto
from datetime import datetime


class Permission(Enum):
    """Enum representing the different permissions in the system."""
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
    """Enum representing the different access levels for library sections."""
    PUBLIC = 0
    RESTRICTED = 1
    HIGHLY_RESTRICTED = 2


class AccessControl:
    """Class for managing access control in the library system."""
    
    def __init__(self):
        """Initialize the access control system."""
        self._role_permissions = self._initialize_role_permissions()
        self._section_access_levels = {}
        self._access_logs = []
    
    def _initialize_role_permissions(self):
        """
        Initialize the permissions for each role.
        
        Returns:
            dict: Dictionary mapping roles to their permissions
        """
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
        """
        Set the access level for a library section.
        
        Args:
            section_id (str): ID of the section
            access_level (AccessLevel): Required access level for the section
        """
        self._section_access_levels[section_id] = access_level
    
    def get_section_access_level(self, section_id):
        """
        Get the access level for a library section.
        
        Args:
            section_id (str): ID of the section
            
        Returns:
            AccessLevel: Required access level for the section, or PUBLIC if not set
        """
        return self._section_access_levels.get(section_id, AccessLevel.PUBLIC)
    
    def has_permission(self, user, permission):
        """
        Check if a user has a specific permission.
        
        Args:
            user: The user to check
            permission (Permission): The permission to check for
            
        Returns:
            bool: True if the user has the permission, False otherwise
        """
        role = user.get_role()
        
        # Special case for librarians with different admin levels
        if role == UserRole.LIBRARIAN:
            # Admin level 1 librarians can't delete books or users
            if user.admin_level == 1 and permission in [Permission.DELETE_BOOK, Permission.DELETE_USER, Permission.MANAGE_SYSTEM]:
                return False
            
            # Admin level 3 librarians have all permissions
            if user.admin_level == 3:
                return True
        
        # Check if the role has the permission
        role_permissions = self._role_permissions.get(role, set())
        return permission in role_permissions
    
    def can_access_section(self, user, section_id):
        """
        Check if a user can access a specific library section.
        
        Args:
            user: The user to check
            section_id (str): ID of the section
            
        Returns:
            bool: True if the user can access the section, False otherwise
        """
        access_level = self.get_section_access_level(section_id)
        role = user.get_role()
        
        # Librarians can access all sections based on their admin level
        if role == UserRole.LIBRARIAN:
            if access_level == AccessLevel.HIGHLY_RESTRICTED:
                return user.admin_level == 3
            elif access_level == AccessLevel.RESTRICTED:
                return user.admin_level >= 2
            else:
                return True
        
        # Scholars can access some restricted sections based on their academic level
        elif role == UserRole.SCHOLAR:
            if access_level == AccessLevel.HIGHLY_RESTRICTED:
                return False  # Only librarians can access highly restricted sections
            elif access_level == AccessLevel.RESTRICTED:
                return user.academic_level in ["Professor", "Distinguished"]
            else:
                return True
        
        # Guests can only access public sections
        else:
            return access_level == AccessLevel.PUBLIC
    
    def can_borrow_book(self, user, book, section_id=None):
        """
        Check if a user can borrow a specific book.
        
        Args:
            user: The user to check
            book: The book to check
            section_id (str, optional): ID of the section the book is in
            
        Returns:
            bool: True if the user can borrow the book, False otherwise
        """
        # Check if the user has the borrow permission
        if not self.has_permission(user, Permission.BORROW_BOOK):
            return False
        
        # Check if the book can be borrowed at all
        if book.get_lending_period() == 0:
            return False
        
        # Check if the user can access the section the book is in
        if section_id and not self.can_access_section(user, section_id):
            return False
        
        # Additional checks based on book type and user role
        from models.book import RareBook, AncientScript
        from models.user import UserRole
        
        role = user.get_role()
        
        if isinstance(book, AncientScript):
            # Ancient scripts can't be borrowed, only viewed in the library
            return False
        
        if isinstance(book, RareBook):
            # Rare books can only be borrowed by librarians and scholars
            if role == UserRole.GUEST:
                return False
            
            # Scholars need to be at least at the Graduate level to borrow rare books
            if role == UserRole.SCHOLAR:
                return user.academic_level in ["Graduate", "Professor", "Distinguished"]
        
        return True
    
    def log_access_attempt(self, user_id, resource_type, resource_id, action, success):
        """
        Log an access attempt.
        
        Args:
            user_id (str): ID of the user attempting access
            resource_type (str): Type of resource being accessed
            resource_id (str): ID of the resource being accessed
            action (str): Action being attempted
            success (bool): Whether access was granted
        """
        self._access_logs.append({
            'timestamp': datetime.now(),
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'success': success
        })
    
    def get_access_logs(self, **filters):
        """
        Get access logs, optionally filtered.
        
        Args:
            **filters: Filters to apply to the logs
            
        Returns:
            list: Filtered access logs
        """
        logs = self._access_logs
        
        # Apply filters
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
