
from abc import ABC, abstractmethod
from datetime import datetime

from models.book import BookStatus
from models.lending import LendingStatus

class LibraryCommand(ABC):
    @abstractmethod
    def execute(self):
        
        pass
    @abstractmethod
    def undo(self):
        
        pass
class CommandHistory:
    

    def __init__(self):
        
        self._history = []

    def push(self, command):
        
        self._history.append(command)

    def pop(self):
        
        if self._history:
            return self._history.pop()
        return None

    def clear(self):
        
        self._history.clear()

    def __len__(self):
        return len(self._history)

class CheckoutBookCommand(LibraryCommand):
    

    def __init__(self, catalog, book_id, user_id):
        
        self._catalog = catalog
        self._book_id = book_id
        self._user_id = user_id
        self._lending_record = None
        self._previous_book_status = None
        self._previous_available_quantity = None

    def execute(self):
        
        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)

        if not book:
            return {'success': False, 'message': 'Book not found'}

        if not user:
            return {'success': False, 'message': 'User not found'}

        self._previous_book_status = book.status
        self._previous_available_quantity = book.available_quantity

        if book.available_quantity <= 0:
            return {'success': False, 'message': f'No copies of this book are available (current status: {book.status.name})'}

        import uuid
        from datetime import timedelta

        record_id = str(uuid.uuid4())
        checkout_date = datetime.now()
        due_date = checkout_date + timedelta(days=book.get_lending_period())

        from models.lending import LendingRecord
        lending_record = LendingRecord(record_id, self._book_id, self._user_id, checkout_date)
        lending_record.due_date = due_date

        book.decrease_available_quantity()
        book.record_borrowing(self._user_id, checkout_date, due_date)

        user.borrow_book(self._book_id, due_date)

        self._catalog.add_lending_record(lending_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)

        self._lending_record = lending_record

        return {
            'success': True,
            'message': 'Book checked out successfully',
            'lending_record': lending_record,
            'due_date': due_date
        }

    def undo(self):
        
        if not self._lending_record:
            return {'success': False, 'message': 'No checkout to undo'}

        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)

        if not book or not user:
            return {'success': False, 'message': 'Book or user not found'}

        book.increase_available_quantity()
        if book.status != self._previous_book_status:
            book.status = self._previous_book_status

        self._lending_record.status = LendingStatus.RETURNED
        self._lending_record._return_date = datetime.now()

        user.return_book(self._book_id)

        self._catalog.update_lending_record(self._lending_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)

        return {
            'success': True,
            'message': 'Checkout undone successfully'
        }

class ReturnBookCommand(LibraryCommand):
    

    def __init__(self, catalog, book_id, user_id, condition_changed=False):
        
        self._catalog = catalog
        self._book_id = book_id
        self._user_id = user_id
        self._condition_changed = condition_changed
        self._lending_record = None
        self._previous_book_status = None
        self._previous_book_condition = None
        self._previous_available_quantity = None

    def execute(self):
        
        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)

        if not book:
            return {'success': False, 'message': 'Book not found'}

        if not user:
            return {'success': False, 'message': 'User not found'}

        self._previous_book_status = book.status
        self._previous_book_condition = book.condition
        self._previous_available_quantity = book.available_quantity

        user_lending_records = self._catalog.get_user_lending_records(self._user_id)
        active_record = None

        for record in user_lending_records:
            if record.book_id == self._book_id and record.status == LendingStatus.ACTIVE:
                active_record = record
                break

        if not active_record:
            return {'success': False, 'message': 'No active lending record found for this book and user'}

        self._lending_record = active_record

        return_date = datetime.now()
        late_fee = 0.0

        if active_record.is_overdue():
            days_overdue = active_record.days_overdue()
            late_fee = book.get_late_fee(days_overdue)
            active_record.late_fee = late_fee

        active_record.return_book(return_date, self._condition_changed)

        if self._condition_changed:
            from models.book import BookCondition
            current_condition = book.condition
            conditions = list(BookCondition)
            current_index = conditions.index(current_condition)

            if current_index < len(conditions) - 1:
                book.condition = conditions[current_index + 1]

        book.increase_available_quantity()
        book.record_return(return_date)

        user.return_book(self._book_id)

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
        
        if not self._lending_record:
            return {'success': False, 'message': 'No return to undo'}

        book = self._catalog.get_book(self._book_id)
        user = self._catalog.get_user(self._user_id)

        if not book or not user:
            return {'success': False, 'message': 'Book or user not found'}

        if book.available_quantity > self._previous_available_quantity:
            book.decrease_available_quantity()

        book.status = self._previous_book_status
        book.condition = self._previous_book_condition

        self._lending_record.status = LendingStatus.ACTIVE
        self._lending_record._return_date = None

        user.borrow_book(self._book_id, self._lending_record.due_date)

        self._catalog.update_lending_record(self._lending_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)

        return {
            'success': True,
            'message': 'Return undone successfully'
        }

class AddBookCommand(LibraryCommand):
    

    def __init__(self, catalog, book, section_name=None):
        
        self._catalog = catalog
        self._book = book
        self._section_name = section_name
        self._book_id = None
        self._section_id = None

    def execute(self):
        
        self._book_id = self._catalog.add_book(self._book)

        if self._section_name:
            section = self._catalog.get_section_by_name(self._section_name)
            if section:
                self._section_id = section['id']
                self._catalog.add_book_to_section(self._book_id, self._section_id)
            else:
                self._section_id = self._catalog.add_section(self._section_name, f"Section for {self._section_name} books")
                self._catalog.add_book_to_section(self._book_id, self._section_id)

        return {
            'success': True,
            'message': 'Book added successfully',
            'book_id': self._book_id,
            'section_id': self._section_id
        }

    def undo(self):
        
        if not self._book_id:
            return {'success': False, 'message': 'No book to remove'}

        self._catalog.remove_book(self._book_id)

        return {
            'success': True,
            'message': 'Book removal undone successfully'
        }

class CommandInvoker:
    

    def __init__(self):
        
        self._history = CommandHistory()

    def execute_command(self, command):
        
        result = command.execute()

        if result.get('success', False):
            self._history.push(command)

        return result

    def undo_last_command(self):
        
        command = self._history.pop()

        if command:
            return command.undo()
        else:
            return {'success': False, 'message': 'No command to undo'}

    def clear_history(self):
        
        self._history.clear()

    def history_size(self):
        
        return len(self._history)
