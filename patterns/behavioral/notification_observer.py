
from abc import ABC, abstractmethod
from datetime import datetime

class LibraryEvent:
    
    
    def __init__(self, event_type, data=None):
        
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        return f"{self.event_type} event at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class LibraryObserver(ABC):
    
    
    @abstractmethod
    def update(self, event):
        
        pass

class LibrarySubject:
    
    
    def __init__(self):
        
        self._observers = []
    
    def attach(self, observer):
        
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event):
        
        for observer in self._observers:
            observer.update(event)

class LibraryEventManager(LibrarySubject):
    
    
    def __init__(self):
        
        super().__init__()
        self._events = []
    
    @property
    def events(self):
        return self._events
    
    def book_added(self, book):
        
        event = LibraryEvent("book_added", {
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author
        })
        self._events.append(event)
        self.notify(event)
    
    def book_removed(self, book_id, title=None):
        
        event = LibraryEvent("book_removed", {
            "book_id": book_id,
            "title": title
        })
        self._events.append(event)
        self.notify(event)
    
    def book_borrowed(self, book, user):
        
        event = LibraryEvent("book_borrowed", {
            "book_id": book.book_id,
            "title": book.title,
            "user_id": user.user_id,
            "user_name": user.name
        })
        self._events.append(event)
        self.notify(event)
    
    def book_returned(self, book, user):
        
        event = LibraryEvent("book_returned", {
            "book_id": book.book_id,
            "title": book.title,
            "user_id": user.user_id,
            "user_name": user.name
        })
        self._events.append(event)
        self.notify(event)
    
    def book_overdue(self, book, user, days_overdue):
        
        event = LibraryEvent("book_overdue", {
            "book_id": book.book_id,
            "title": book.title,
            "user_id": user.user_id,
            "user_name": user.name,
            "days_overdue": days_overdue
        })
        self._events.append(event)
        self.notify(event)
    
    def book_needs_restoration(self, book):
        
        event = LibraryEvent("book_needs_restoration", {
            "book_id": book.book_id,
            "title": book.title,
            "condition": book.condition.name
        })
        self._events.append(event)
        self.notify(event)
    
    def user_registered(self, user):
        
        event = LibraryEvent("user_registered", {
            "user_id": user.user_id,
            "name": user.name,
            "role": user.get_role().name
        })
        self._events.append(event)
        self.notify(event)

class LibrarianNotificationObserver(LibraryObserver):
    
    
    def __init__(self, notification_service):
        
        self._notification_service = notification_service
        self._librarian_emails = []
    
    def add_librarian_email(self, email):
        
        if email not in self._librarian_emails:
            self._librarian_emails.append(email)
    
    def update(self, event):
        
        if event.event_type in ["book_overdue", "book_needs_restoration"]:
            subject = f"Library Alert: {event.event_type.replace('_', ' ').title()}"
            
            if event.event_type == "book_overdue":
                message = (
                    f"The book '{event.data['title']}' is overdue by {event.data['days_overdue']} days. "
                    f"It was borrowed by {event.data['user_name']}."
                )
            elif event.event_type == "book_needs_restoration":
                message = (
                    f"The book '{event.data['title']}' needs restoration. "
                    f"Current condition: {event.data['condition']}."
                )
            
            for email in self._librarian_emails:
                self._notification_service.send_notification(email, subject, message)

class UserNotificationObserver(LibraryObserver):
    
    
    def __init__(self, notification_service, user_service):
        
        self._notification_service = notification_service
        self._user_service = user_service
    
    def update(self, event):
        
        if event.event_type == "book_borrowed":
            user_id = event.data['user_id']
            user = self._user_service.get_user(user_id)
            
            if user:
                subject = "Book Checkout Confirmation"
                message = f"You have borrowed '{event.data['title']}'. Please return it on time."
                self._notification_service.send_notification(user.email, subject, message)
        
        elif event.event_type == "book_returned":
            user_id = event.data['user_id']
            user = self._user_service.get_user(user_id)
            
            if user:
                subject = "Book Return Confirmation"
                message = f"Thank you for returning '{event.data['title']}'."
                self._notification_service.send_notification(user.email, subject, message)

class LoggingObserver(LibraryObserver):
    
    
    def __init__(self, log_file_path):
        
        self._log_file_path = log_file_path
    
    def update(self, event):
        
        log_entry = f"[{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {event.event_type}: {event.data}\n"
        
        try:
            with open(self._log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")

class NotificationService:
    
    
    def send_notification(self, recipient, subject, message):
        
        print(f"Notification to {recipient}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("-" * 50)
        
        return True
