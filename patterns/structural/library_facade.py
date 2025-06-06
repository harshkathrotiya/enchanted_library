
import uuid
from datetime import datetime

from models.book import BookStatus
from models.lending import LendingRecord, LendingStatus
from patterns.creational.catalog_singleton import Catalog
from security.access_control import AccessControl
from services.fee_calculator import FeeCalculator

class LibraryFacade:
    

    def __init__(self):
        
        self._catalog = Catalog()
        self._access_control = AccessControl()
        self._fee_calculator = FeeCalculator()

    def add_book(self, book, section_name=None):
        
        book_id = self._catalog.add_book(book)

        if section_name:
            section = self._catalog.get_section_by_name(section_name)
            if section:
                self._catalog.add_book_to_section(book_id, section['id'])
            else:
                section_id = self._catalog.add_section(section_name, f"Section for {section_name} books")
                self._catalog.add_book_to_section(book_id, section_id)

        return book_id

    def search_books(self, **kwargs):
        
        return self._catalog.search_books(**kwargs)

    def register_user(self, user):
        
        return self._catalog.add_user(user)

    def authenticate_user(self, email, password):
        
        for user in self._catalog._users.values():
            if user.email == email and user._password == password:
                user.record_login()
                self._catalog.update_user(user)
                return user
        return None

    def checkout_book(self, book_id, user_id):
        
        book = self._catalog.get_book(book_id)
        user = self._catalog.get_user(user_id)

        if not book:
            return {'success': False, 'message': 'Book not found'}

        if not user:
            return {'success': False, 'message': 'User not found'}

        if book.available_quantity <= 0:
            return {'success': False, 'message': f'No copies of this book are available (current status: {book.status.name})'}

        section = None
        for s in self._catalog._sections.values():
            if book_id in s['books']:
                section = s
                break

        if section and not user.can_access_section(section['name']):
            return {'success': False, 'message': f'User does not have permission to access the {section["name"]} section'}

        user_lending_records = self._catalog.get_user_lending_records(user_id)
        active_loans = [r for r in user_lending_records if r.status == LendingStatus.ACTIVE]

        if len(active_loans) >= user.get_max_books():
            return {'success': False, 'message': f'User has reached their borrowing limit of {user.get_max_books()} books'}

        if book.get_lending_period() == 0:
            return {'success': False, 'message': 'This book can only be viewed in the library and cannot be borrowed'}

        record_id = str(uuid.uuid4())
        checkout_date = datetime.now()

        from datetime import timedelta
        due_date = checkout_date + timedelta(days=book.get_lending_period())

        lending_record = LendingRecord(record_id, book_id, user_id, checkout_date)
        lending_record.due_date = due_date

        book.decrease_available_quantity()
        book.record_borrowing(user_id, checkout_date, due_date)

        user.borrow_book(book_id, due_date)

        self._catalog.add_lending_record(lending_record)
        self._catalog.update_book(book)
        self._catalog.update_user(user)

        return {
            'success': True,
            'message': 'Book checked out successfully',
            'lending_record': lending_record,
            'due_date': due_date
        }

    def return_book(self, book_id, user_id, condition_changed=False):
        
        book = self._catalog.get_book(book_id)
        user = self._catalog.get_user(user_id)

        if not book:
            return {'success': False, 'message': 'Book not found'}

        if not user:
            return {'success': False, 'message': 'User not found'}

        user_lending_records = self._catalog.get_user_lending_records(user_id)
        active_record = None

        for record in user_lending_records:
            if record.book_id == book_id and record.status == LendingStatus.ACTIVE:
                active_record = record
                break

        if not active_record:
            return {'success': False, 'message': 'No active lending record found for this book and user'}

        return_date = datetime.now()
        late_fee = 0.0

        if active_record.is_overdue():
            days_overdue = active_record.days_overdue()
            late_fee = book.get_late_fee(days_overdue)
            active_record.late_fee = late_fee

        active_record.return_book(return_date, condition_changed)

        if condition_changed:
            from models.book import BookCondition
            current_condition = book.condition
            conditions = list(BookCondition)
            current_index = conditions.index(current_condition)

            if current_index < len(conditions) - 1:
                book.condition = conditions[current_index + 1]

        book.increase_available_quantity()
        book.record_return(return_date)

        user.return_book(book_id)

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

    def get_user_borrowed_books(self, user_id):
        
        user = self._catalog.get_user(user_id)

        if not user:
            return []

        borrowed_books = []
        for book_info in user.borrowed_books:
            if not book_info['returned']:
                book = self._catalog.get_book(book_info['book_id'])
                if book:
                    borrowed_books.append({
                        'book': book,
                        'borrow_date': book_info['borrow_date'],
                        'due_date': book_info['due_date']
                    })

        return borrowed_books

    def get_book_availability(self, book_id):
        
        book = self._catalog.get_book(book_id)

        if not book:
            return {'available': False, 'message': 'Book not found'}

        if book.available_quantity > 0:
            return {'available': True, 'message': f'Book is available ({book.available_quantity} of {book.quantity} copies available)'}
        else:
            if book.status == BookStatus.BORROWED:
                lending_records = self._catalog.get_book_lending_records(book_id)
                active_records = [r for r in lending_records if r.status == LendingStatus.ACTIVE]

                if active_records:
                    record = active_records[0]
                    user = self._catalog.get_user(record.user_id)
                    due_date = record.due_date

                    return {
                        'available': False,
                        'message': f'Book is currently borrowed by {user.name if user else "unknown user"}',
                        'due_date': due_date
                    }

            return {'available': False, 'message': f'Book is not available (status: {book.status.name})'}

    def get_overdue_books(self):
        
        overdue_records = self._catalog.get_overdue_records()
        result = []

        for record in overdue_records:
            book = self._catalog.get_book(record.book_id)
            user = self._catalog.get_user(record.user_id)

            if book and user:
                days_overdue = record.days_overdue()
                late_fee = book.get_late_fee(days_overdue)

                result.append({
                    'record': record,
                    'book': book,
                    'user': user,
                    'days_overdue': days_overdue,
                    'late_fee': late_fee
                })

        return result
