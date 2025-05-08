"""
Action Command implementation for the Enchanted Library system.
This module implements the Command Pattern for undoable library actions.
"""
from abc import ABC, abstractmethod
from datetime import datetime

from models.book import BookStatus
from models.lending import LendingStatus


class LibraryCommand(ABC):
    """Abstract base class for library commands."""
    
    @abstractmethod
    def execute(self):
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self):
        """Undo the command."""
        pass


class CommandHistory:
    """Class that keeps track of executed commands for undo functionality."""
    
    def __init__(self):
        """Initialize the command history with an empty list."""
        self._history = []
    
    def push(self, command):
        """
        Add a command to the history.
        
        Args:
            command (LibraryCommand): The command to add
        """
        self._history.append(command)
    
    def pop(self):
        """
        Remove and return the last command from the history.
        
        Returns:
            LibraryCommand: The last command, or None if history is empty
        """
        if self._history:
            return self._history.pop()
        return None
    
    def clear(self):
        """Clear the command history."""
        self._history.clear()
    
    def __len__(self):
        return len(self._history)


class CheckoutBookCommand(LibraryCommand):
    """Command for checking out a book."""
    
    def __init__(self, catalog, book_id, user_id):
        """
        Initialize the checkout command.
        
        Args:
            catalog: The library catalog
            book_id (str): ID of the book to check out
            user_id (str): ID of the user checking out the book
        """
        self._catalog = catalog
        self._book_id = book_id
        self._user_id = user_id
        self._lending_record = None
        self._previous_book_status = None
    
    def execute(self):
        """
        Execute the checkout command.
        
        Returns:
            dict: Result of the checkout operation
        """
        # Get the book and user
        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)
        
        if not book:
            return {'success': False, 'message': 'Book not found'}
        
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        # Save the previous book status for undo
        self._previous_book_status = book.status
        
        # Check if the book is available
        if book.status != BookStatus.AVAILABLE:
            return {'success': False, 'message': f'Book is not available (current status: {book.status.name})'}
        
        # Create a lending record
        import uuid
        from datetime import timedelta
        
        record_id = str(uuid.uuid4())
        checkout_date = datetime.now()
        due_date = checkout_date + timedelta(days=book.get_lending_period())
        
        from models.lending import LendingRecord
        lending_record = LendingRecord(record_id, self._book_id, self._user_id, checkout_date)
        lending_record.due_date = due_date
        
        # Update the book status
        book.status = BookStatus.BORROWED
        book.record_borrowing(self._user_id, checkout_date, due_date)
        
        # Update the user's borrowed books
        user.borrow_book(self._book_id, due_date)
        
        # Save the changes
        self._catalog.add_lending_record(lending_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)
        
        # Save the lending record for undo
        self._lending_record = lending_record
        
        return {
            'success': True,
            'message': 'Book checked out successfully',
            'lending_record': lending_record,
            'due_date': due_date
        }
    
    def undo(self):
        """
        Undo the checkout command.
        
        Returns:
            dict: Result of the undo operation
        """
        if not self._lending_record:
            return {'success': False, 'message': 'No checkout to undo'}
        
        # Get the book and user
        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)
        
        if not book or not user:
            return {'success': False, 'message': 'Book or user not found'}
        
        # Restore the book status
        book.status = self._previous_book_status
        
        # Update the lending record
        self._lending_record.status = LendingStatus.RETURNED
        self._lending_record._return_date = datetime.now()
        
        # Update the user's borrowed books
        user.return_book(self._book_id)
        
        # Save the changes
        self._catalog.update_lending_record(self._lending_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)
        
        return {
            'success': True,
            'message': 'Checkout undone successfully'
        }


class ReturnBookCommand(LibraryCommand):
    """Command for returning a book."""
    
    def __init__(self, catalog, book_id, user_id, condition_changed=False):
        """
        Initialize the return command.
        
        Args:
            catalog: The library catalog
            book_id (str): ID of the book to return
            user_id (str): ID of the user returning the book
            condition_changed (bool): Whether the book's condition has changed
        """
        self._catalog = catalog
        self._book_id = book_id
        self._user_id = user_id
        self._condition_changed = condition_changed
        self._lending_record = None
        self._previous_book_status = None
        self._previous_book_condition = None
    
    def execute(self):
        """
        Execute the return command.
        
        Returns:
            dict: Result of the return operation
        """
        # Get the book and user
        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)
        
        if not book:
            return {'success': False, 'message': 'Book not found'}
        
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        # Save the previous book status and condition for undo
        self._previous_book_status = book.status
        self._previous_book_condition = book.condition
        
        # Find the active lending record for this book and user
        user_lending_records = self._catalog.get_user_lending_records(self._user_id)
        active_record = None
        
        for record in user_lending_records:
            if record.book_id == self._book_id and record.status == LendingStatus.ACTIVE:
                active_record = record
                break
        
        if not active_record:
            return {'success': False, 'message': 'No active lending record found for this book and user'}
        
        # Save the lending record for undo
        self._lending_record = active_record
        
        # Process the return
        return_date = datetime.now()
        late_fee = 0.0
        
        # Check if the book is overdue
        if active_record.is_overdue():
            days_overdue = active_record.days_overdue()
            late_fee = book.get_late_fee(days_overdue)
            active_record.late_fee = late_fee
        
        # Update the lending record
        active_record.return_book(return_date, self._condition_changed)
        
        # Update the book status and condition if needed
        if self._condition_changed:
            from models.book import BookCondition
            # Downgrade the book's condition
            current_condition = book.condition
            conditions = list(BookCondition)
            current_index = conditions.index(current_condition)
            
            if current_index < len(conditions) - 1:
                book.condition = conditions[current_index + 1]
        
        book.status = BookStatus.AVAILABLE
        book.record_return(return_date)
        
        # Update the user's borrowed books
        user.return_book(self._book_id)
        
        # Save the changes
        self._catalog.update_lending_record(active_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)
        
        result = {
            'success': True,
            'message': 'Book returned successfully',
            'return_date': return_date
        }
        
        if late_fee > 0:
            result['late_fee'] = late_fee
            result['message'] += f' with a late fee of ${late_fee:.2f}'
        
        return result
    
    def undo(self):
        """
        Undo the return command.
        
        Returns:
            dict: Result of the undo operation
        """
        if not self._lending_record:
            return {'success': False, 'message': 'No return to undo'}
        
        # Get the book and user
        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)
        
        if not book or not user:
            return {'success': False, 'message': 'Book or user not found'}
        
        # Restore the book status and condition
        book.status = self._previous_book_status
        book.condition = self._previous_book_condition
        
        # Update the lending record
        self._lending_record.status = LendingStatus.ACTIVE
        self._lending_record._return_date = None
        
        # Update the user's borrowed books
        # This is more complex as we need to add the book back to the user's borrowed books
        # For simplicity, we'll just add it as a new borrowing
        user.borrow_book(self._book_id, self._lending_record.due_date)
        
        # Save the changes
        self._catalog.update_lending_record(self._lending_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)
        
        return {
            'success': True,
            'message': 'Return undone successfully'
        }


class AddBookCommand(LibraryCommand):
    """Command for adding a book to the catalog."""
    
    def __init__(self, catalog, book, section_name=None):
        """
        Initialize the add book command.
        
        Args:
            catalog: The library catalog
            book: The book to add
            section_name (str, optional): Name of the section to add the book to
        """
        self._catalog = catalog
        self._book = book
        self._section_name = section_name
        self._book_id = None
        self._section_id = None
    
    def execute(self):
        """
        Execute the add book command.
        
        Returns:
            dict: Result of the add operation
        """
        # Add the book to the catalog
        self._book_id = self._catalog.add_book(self._book)
        
        # Add the book to the specified section if provided
        if self._section_name:
            section = self._catalog.get_section_by_name(self._section_name)
            if section:
                self._section_id = section['id']
                self._catalog.add_book_to_section(self._book_id, self._section_id)
            else:
                # Create the section if it doesn't exist
                self._section_id = self._catalog.add_section(self._section_name, f"Section for {self._section_name} books")
                self._catalog.add_book_to_section(self._book_id, self._section_id)
        
        return {
            'success': True,
            'message': 'Book added successfully',
            'book_id': self._book_id,
            'section_id': self._section_id
        }
    
    def undo(self):
        """
        Undo the add book command.
        
        Returns:
            dict: Result of the undo operation
        """
        if not self._book_id:
            return {'success': False, 'message': 'No book to remove'}
        
        # Remove the book from the catalog
        self._catalog.remove_book(self._book_id)
        
        return {
            'success': True,
            'message': 'Book removal undone successfully'
        }


class CommandInvoker:
    """Class that invokes commands and manages the command history."""
    
    def __init__(self):
        """Initialize the invoker with an empty command history."""
        self._history = CommandHistory()
    
    def execute_command(self, command):
        """
        Execute a command and add it to the history.
        
        Args:
            command (LibraryCommand): The command to execute
            
        Returns:
            dict: Result of the command execution
        """
        result = command.execute()
        
        if result.get('success', False):
            self._history.push(command)
        
        return result
    
    def undo_last_command(self):
        """
        Undo the last executed command.
        
        Returns:
            dict: Result of the undo operation, or a message if no command to undo
        """
        command = self._history.pop()
        
        if command:
            return command.undo()
        else:
            return {'success': False, 'message': 'No command to undo'}
    
    def clear_history(self):
        """Clear the command history."""
        self._history.clear()
    
    def history_size(self):
        """
        Get the size of the command history.
        
        Returns:
            int: Number of commands in the history
        """
        return len(self._history)
