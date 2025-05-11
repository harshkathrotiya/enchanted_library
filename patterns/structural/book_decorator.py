

from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class BookDecorator(ABC):
    
    
    def __init__(self, book):
        
        self._book = book
    
    @property
    def book_id(self):
        return self._book.book_id
    
    @property
    def title(self):
        return self._book.title
    
    @property
    def author(self):
        return self._book.author
    
    @property
    def year_published(self):
        return self._book.year_published
    
    @property
    def isbn(self):
        return self._book.isbn
    
    @property
    def condition(self):
        return self._book.condition
    
    @condition.setter
    def condition(self, value):
        self._book.condition = value
    
    @property
    def status(self):
        return self._book.status
    
    @status.setter
    def status(self, value):
        self._book.status = value
    
    @property
    def location(self):
        return self._book.location
    
    @location.setter
    def location(self, value):
        self._book.location = value
    
    @property
    def quantity(self):
        return self._book.quantity
    
    @quantity.setter
    def quantity(self, value):
        self._book.quantity = value
    
    @property
    def available_quantity(self):
        return self._book.available_quantity
    
    def decrease_available_quantity(self):
        return self._book.decrease_available_quantity()
    
    def increase_available_quantity(self):
        return self._book.increase_available_quantity()
    
    def get_lending_period(self):
        return self._book.get_lending_period()
    
    def get_late_fee(self, days_overdue):
        return self._book.get_late_fee(days_overdue)
    
    def needs_restoration(self):
        return self._book.needs_restoration()
    
    def record_borrowing(self, user_id, borrow_date, due_date):
        self._book.record_borrowing(user_id, borrow_date, due_date)
    
    def record_return(self, return_date):
        self._book.record_return(return_date)
    
    def __str__(self):
        return str(self._book)

class DigitalCopyDecorator(BookDecorator):
    
    
    def __init__(self, book, digital_url=None, format_type="PDF"):
        
        super().__init__(book)
        self._digital_url = digital_url
        self._format_type = format_type
        self._download_count = 0
    
    @property
    def digital_url(self):
        return self._digital_url
    
    @digital_url.setter
    def digital_url(self, value):
        self._digital_url = value
    
    @property
    def format_type(self):
        return self._format_type
    
    @format_type.setter
    def format_type(self, value):
        self._format_type = value
    
    @property
    def download_count(self):
        return self._download_count
    
    def download(self):
        
        self._download_count += 1
        return {
            'success': True,
            'message': f"Downloaded {self.title} in {self._format_type} format",
            'url': self._digital_url,
            'download_count': self._download_count
        }
    
    def get_lending_period(self):
        original_period = super().get_lending_period()
        return original_period + 7
    
    def __str__(self):
        return f"{super().__str__()} [Digital Copy Available]"

class AutoReminderDecorator(BookDecorator):
    
    
    def __init__(self, book, notification_service, reminder_days=3):
        
        super().__init__(book)
        self._notification_service = notification_service
        self._reminder_days = reminder_days
        self._reminders_sent = []
    
    def record_borrowing(self, user_id, borrow_date, due_date):
        
        super().record_borrowing(user_id, borrow_date, due_date)
        
        reminder_date = due_date - timedelta(days=self._reminder_days)
        self._reminders_sent.append({
            'user_id': user_id,
            'due_date': due_date,
            'reminder_date': reminder_date,
            'sent': False
        })
    
    def check_reminders(self, catalog):
        
        today = datetime.now()
        sent_reminders = []
        
        for reminder in self._reminders_sent:
            if not reminder['sent'] and today >= reminder['reminder_date']:
                user = catalog.get_user(reminder['user_id'])
                if user:
                    subject = f"Reminder: {self.title} is due soon"
                    message = (
                        f"This is a friendly reminder that the book '{self.title}' "
                        f"is due on {reminder['due_date'].strftime('%Y-%m-%d')}. "
                        f"Please return it on time to avoid late fees."
                    )
                    
                    self._notification_service.send_notification(
                        user.email, subject, message
                    )
                    
                    reminder['sent'] = True
                    sent_reminders.append(reminder)
        
        return sent_reminders
    
    def __str__(self):
        return f"{super().__str__()} [Auto-Reminder Enabled]"

class RestrictedAccessDecorator(BookDecorator):
    
    
    def __init__(self, book, access_control, required_permission=None, access_log=True):
        
        super().__init__(book)
        self._access_control = access_control
        self._required_permission = required_permission
        self._access_log = access_log
        self._access_attempts = []
    
    def can_access(self, user):
        
        has_access = True
        
        if self._required_permission:
            has_access = self._access_control.has_permission(user, self._required_permission)
        
        if self._access_log:
            self._access_attempts.append({
                'timestamp': datetime.now(),
                'user_id': user.user_id,
                'user_name': user.name,
                'success': has_access
            })
        
        return has_access
    
    def get_access_log(self):
        
        return self._access_attempts
    
    def __str__(self):
        return f"{super().__str__()} [Restricted Access]"
