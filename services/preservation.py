"""
Preservation Module implementation for the Enchanted Library system.
This module provides services for book preservation and restoration.
"""
from datetime import datetime, timedelta

from models.book import BookCondition, BookStatus


class PreservationService:
    """Service for managing book preservation and restoration."""
    
    def __init__(self):
        """Initialize the preservation service."""
        self._restoration_queue = []
        self._restoration_history = []
        self._condition_thresholds = {
            'general': BookCondition.POOR,  # General books need restoration when in poor condition
            'rare': BookCondition.FAIR,     # Rare books need restoration when in fair condition
            'ancient': BookCondition.GOOD   # Ancient scripts need restoration when in good condition (not excellent)
        }
        self._restoration_durations = {
            'general': 7,    # 7 days for general books
            'rare': 14,      # 14 days for rare books
            'ancient': 30    # 30 days for ancient scripts
        }
    
    def check_needs_restoration(self, book):
        """
        Check if a book needs restoration based on its condition and type.
        
        Args:
            book: The book to check
            
        Returns:
            bool: True if the book needs restoration, False otherwise
        """
        # Determine the book type
        from models.book import GeneralBook, RareBook, AncientScript
        
        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'  # Default
        
        # Get the condition threshold for this book type
        threshold = self._condition_thresholds.get(book_type, BookCondition.POOR)
        
        # Check if the book's condition is at or worse than the threshold
        return book.condition.value >= threshold.value
    
    def add_to_restoration_queue(self, book, priority=0, notes=None):
        """
        Add a book to the restoration queue.
        
        Args:
            book: The book to restore
            priority (int): Priority level (0-10, with 10 being highest)
            notes (str, optional): Notes about the restoration
            
        Returns:
            dict: Result of the operation
        """
        # Check if the book is already in the queue
        for item in self._restoration_queue:
            if item['book_id'] == book.book_id:
                return {
                    'success': False,
                    'message': 'Book is already in the restoration queue'
                }
        
        # Check if the book is available for restoration
        if book.status != BookStatus.AVAILABLE and book.status != BookStatus.RESTORATION:
            return {
                'success': False,
                'message': f'Book is not available for restoration (current status: {book.status.name})'
            }
        
        # Determine the book type and estimated duration
        from models.book import GeneralBook, RareBook, AncientScript
        
        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'  # Default
        
        duration_days = self._restoration_durations.get(book_type, 7)
        
        # Add the book to the queue
        queue_item = {
            'book_id': book.book_id,
            'title': book.title,
            'book_type': book_type,
            'condition': book.condition,
            'priority': priority,
            'notes': notes,
            'added_date': datetime.now(),
            'estimated_duration': duration_days,
            'estimated_completion': datetime.now() + timedelta(days=duration_days)
        }
        
        self._restoration_queue.append(queue_item)
        
        # Update the book's status
        book.status = BookStatus.RESTORATION
        
        return {
            'success': True,
            'message': 'Book added to restoration queue',
            'estimated_completion': queue_item['estimated_completion']
        }
    
    def remove_from_restoration_queue(self, book_id):
        """
        Remove a book from the restoration queue.
        
        Args:
            book_id (str): ID of the book to remove
            
        Returns:
            dict: Result of the operation
        """
        # Find the book in the queue
        for i, item in enumerate(self._restoration_queue):
            if item['book_id'] == book_id:
                # Remove the book from the queue
                removed_item = self._restoration_queue.pop(i)
                
                return {
                    'success': True,
                    'message': 'Book removed from restoration queue',
                    'item': removed_item
                }
        
        return {
            'success': False,
            'message': 'Book not found in restoration queue'
        }
    
    def get_restoration_queue(self, sort_by='priority'):
        """
        Get the current restoration queue.
        
        Args:
            sort_by (str): Field to sort by ('priority', 'added_date', 'estimated_completion')
            
        Returns:
            list: Sorted restoration queue
        """
        if sort_by == 'priority':
            return sorted(self._restoration_queue, key=lambda x: (-x['priority'], x['added_date']))
        elif sort_by == 'added_date':
            return sorted(self._restoration_queue, key=lambda x: x['added_date'])
        elif sort_by == 'estimated_completion':
            return sorted(self._restoration_queue, key=lambda x: x['estimated_completion'])
        else:
            return self._restoration_queue
    
    def complete_restoration(self, book_id, new_condition=None, notes=None):
        """
        Complete the restoration of a book.
        
        Args:
            book_id (str): ID of the book that was restored
            new_condition (BookCondition, optional): New condition of the book
            notes (str, optional): Notes about the restoration
            
        Returns:
            dict: Result of the operation
        """
        # Find the book in the queue
        queue_item = None
        for i, item in enumerate(self._restoration_queue):
            if item['book_id'] == book_id:
                queue_item = self._restoration_queue.pop(i)
                break
        
        if not queue_item:
            return {
                'success': False,
                'message': 'Book not found in restoration queue'
            }
        
        # Record the restoration in the history
        history_item = {
            'book_id': book_id,
            'title': queue_item['title'],
            'book_type': queue_item['book_type'],
            'original_condition': queue_item['condition'],
            'new_condition': new_condition or BookCondition.GOOD,
            'start_date': queue_item['added_date'],
            'completion_date': datetime.now(),
            'duration': (datetime.now() - queue_item['added_date']).days,
            'notes': notes or queue_item['notes']
        }
        
        self._restoration_history.append(history_item)
        
        return {
            'success': True,
            'message': 'Restoration completed successfully',
            'history_item': history_item
        }
    
    def get_restoration_history(self, book_id=None, start_date=None, end_date=None):
        """
        Get the restoration history, optionally filtered.
        
        Args:
            book_id (str, optional): Filter by book ID
            start_date (datetime, optional): Filter by start date
            end_date (datetime, optional): Filter by end date
            
        Returns:
            list: Filtered restoration history
        """
        history = self._restoration_history
        
        # Apply filters
        if book_id:
            history = [item for item in history if item['book_id'] == book_id]
        
        if start_date:
            history = [item for item in history if item['completion_date'] >= start_date]
        
        if end_date:
            history = [item for item in history if item['completion_date'] <= end_date]
        
        return sorted(history, key=lambda x: x['completion_date'], reverse=True)
    
    def get_books_needing_restoration(self, catalog):
        """
        Get all books in the catalog that need restoration.
        
        Args:
            catalog: The library catalog
            
        Returns:
            list: Books that need restoration
        """
        books_needing_restoration = []
        
        for book in catalog._books.values():
            if self.check_needs_restoration(book) and book.status != BookStatus.RESTORATION:
                books_needing_restoration.append(book)
        
        return books_needing_restoration
    
    def get_restoration_recommendations(self, catalog):
        """
        Get recommendations for books that should be restored soon.
        
        Args:
            catalog: The library catalog
            
        Returns:
            list: Books recommended for restoration with priority levels
        """
        recommendations = []
        
        for book in catalog._books.values():
            # Skip books already in restoration
            if book.status == BookStatus.RESTORATION:
                continue
            
            # Determine the book type
            from models.book import GeneralBook, RareBook, AncientScript
            
            if isinstance(book, GeneralBook):
                book_type = 'general'
            elif isinstance(book, RareBook):
                book_type = 'rare'
            elif isinstance(book, AncientScript):
                book_type = 'ancient'
            else:
                book_type = 'general'  # Default
            
            # Calculate priority based on book type and condition
            priority = 0
            
            # Book type factor
            type_factor = {'general': 1, 'rare': 2, 'ancient': 3}
            
            # Condition factor
            condition_factor = {
                BookCondition.EXCELLENT: 0,
                BookCondition.GOOD: 1,
                BookCondition.FAIR: 2,
                BookCondition.POOR: 3,
                BookCondition.CRITICAL: 4
            }
            
            # Calculate priority (0-10)
            priority = min(10, type_factor.get(book_type, 1) * condition_factor.get(book.condition, 0))
            
            # Only include books with priority > 0
            if priority > 0:
                recommendations.append({
                    'book': book,
                    'priority': priority,
                    'reason': f"{book_type.capitalize()} book in {book.condition.name} condition"
                })
        
        # Sort by priority (highest first)
        return sorted(recommendations, key=lambda x: x['priority'], reverse=True)
