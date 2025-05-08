"""
Notification Observer implementation for the Enchanted Library system.
This module implements the Observer Pattern for library notifications.
"""
from abc import ABC, abstractmethod
from datetime import datetime


class LibraryEvent:
    """Class representing an event in the library system."""
    
    def __init__(self, event_type, data=None):
        """
        Initialize a new library event.
        
        Args:
            event_type (str): Type of the event
            data (dict, optional): Additional data for the event
        """
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        return f"{self.event_type} event at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class LibraryObserver(ABC):
    """Abstract base class for library event observers."""
    
    @abstractmethod
    def update(self, event):
        """
        Update the observer with a new event.
        
        Args:
            event (LibraryEvent): The event that occurred
        """
        pass


class LibrarySubject:
    """Subject class that notifies observers about library events."""
    
    def __init__(self):
        """Initialize the subject with an empty list of observers."""
        self._observers = []
    
    def attach(self, observer):
        """
        Attach an observer to the subject.
        
        Args:
            observer (LibraryObserver): The observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        """
        Detach an observer from the subject.
        
        Args:
            observer (LibraryObserver): The observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event):
        """
        Notify all observers about an event.
        
        Args:
            event (LibraryEvent): The event to notify about
        """
        for observer in self._observers:
            observer.update(event)


class LibraryEventManager(LibrarySubject):
    """Manager class for library events that acts as the concrete subject."""
    
    def __init__(self):
        """Initialize the event manager."""
        super().__init__()
        self._events = []
    
    @property
    def events(self):
        return self._events
    
    def book_added(self, book):
        """
        Notify observers that a book was added.
        
        Args:
            book: The book that was added
        """
        event = LibraryEvent("book_added", {
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author
        })
        self._events.append(event)
        self.notify(event)
    
    def book_removed(self, book_id, title=None):
        """
        Notify observers that a book was removed.
        
        Args:
            book_id (str): ID of the book that was removed
            title (str, optional): Title of the book
        """
        event = LibraryEvent("book_removed", {
            "book_id": book_id,
            "title": title
        })
        self._events.append(event)
        self.notify(event)
    
    def book_borrowed(self, book, user):
        """
        Notify observers that a book was borrowed.
        
        Args:
            book: The book that was borrowed
            user: The user who borrowed the book
        """
        event = LibraryEvent("book_borrowed", {
            "book_id": book.book_id,
            "title": book.title,
            "user_id": user.user_id,
            "user_name": user.name
        })
        self._events.append(event)
        self.notify(event)
    
    def book_returned(self, book, user):
        """
        Notify observers that a book was returned.
        
        Args:
            book: The book that was returned
            user: The user who returned the book
        """
        event = LibraryEvent("book_returned", {
            "book_id": book.book_id,
            "title": book.title,
            "user_id": user.user_id,
            "user_name": user.name
        })
        self._events.append(event)
        self.notify(event)
    
    def book_overdue(self, book, user, days_overdue):
        """
        Notify observers that a book is overdue.
        
        Args:
            book: The overdue book
            user: The user who borrowed the book
            days_overdue (int): Number of days the book is overdue
        """
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
        """
        Notify observers that a book needs restoration.
        
        Args:
            book: The book that needs restoration
        """
        event = LibraryEvent("book_needs_restoration", {
            "book_id": book.book_id,
            "title": book.title,
            "condition": book.condition.name
        })
        self._events.append(event)
        self.notify(event)
    
    def user_registered(self, user):
        """
        Notify observers that a new user was registered.
        
        Args:
            user: The user that was registered
        """
        event = LibraryEvent("user_registered", {
            "user_id": user.user_id,
            "name": user.name,
            "role": user.get_role().name
        })
        self._events.append(event)
        self.notify(event)


class LibrarianNotificationObserver(LibraryObserver):
    """Observer that sends notifications to librarians."""
    
    def __init__(self, notification_service):
        """
        Initialize the observer with a notification service.
        
        Args:
            notification_service: Service to send notifications
        """
        self._notification_service = notification_service
        self._librarian_emails = []
    
    def add_librarian_email(self, email):
        """
        Add a librarian email to the notification list.
        
        Args:
            email (str): Email address of the librarian
        """
        if email not in self._librarian_emails:
            self._librarian_emails.append(email)
    
    def update(self, event):
        """
        Update the observer with a new event and send notifications if needed.
        
        Args:
            event (LibraryEvent): The event that occurred
        """
        # Only send notifications for certain event types
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
            
            # Send notification to all librarians
            for email in self._librarian_emails:
                self._notification_service.send_notification(email, subject, message)


class UserNotificationObserver(LibraryObserver):
    """Observer that sends notifications to users."""
    
    def __init__(self, notification_service, user_service):
        """
        Initialize the observer with notification and user services.
        
        Args:
            notification_service: Service to send notifications
            user_service: Service to look up user information
        """
        self._notification_service = notification_service
        self._user_service = user_service
    
    def update(self, event):
        """
        Update the observer with a new event and send notifications if needed.
        
        Args:
            event (LibraryEvent): The event that occurred
        """
        # Send notifications to users for relevant events
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
    """Observer that logs all library events."""
    
    def __init__(self, log_file_path):
        """
        Initialize the observer with a log file path.
        
        Args:
            log_file_path (str): Path to the log file
        """
        self._log_file_path = log_file_path
    
    def update(self, event):
        """
        Update the observer with a new event and log it.
        
        Args:
            event (LibraryEvent): The event that occurred
        """
        log_entry = f"[{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {event.event_type}: {event.data}\n"
        
        try:
            with open(self._log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file: {e}")


class NotificationService:
    """Service for sending notifications to users."""
    
    def send_notification(self, recipient, subject, message):
        """
        Send a notification to a recipient.
        
        Args:
            recipient (str): Email address of the recipient
            subject (str): Subject of the notification
            message (str): Content of the notification
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise
        """
        # In a real system, this would send an email or other notification
        # For now, just print the notification
        print(f"Notification to {recipient}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("-" * 50)
        
        return True
