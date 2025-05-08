"""
Main application for the Enchanted Library system.
This module serves as the entry point for the library management system.
"""
import sys
from datetime import datetime, timedelta

from models.book import BookCondition, BookStatus
from models.user import UserRole
from patterns.creational.book_factory import BookFactory
from patterns.creational.user_factory import UserFactory
from patterns.creational.catalog_singleton import Catalog
from patterns.creational.book_builder import BookDirector
from patterns.structural.library_facade import LibraryFacade
from patterns.behavioral.notification_observer import (
    LibraryEventManager, LibrarianNotificationObserver,
    UserNotificationObserver, LoggingObserver, NotificationService
)
from ui.cli import CommandLineInterface
from ui.gui.app import launch_gui


def initialize_sample_data():
    """Initialize the library with sample data for testing."""
    catalog = Catalog()

    # Create some sample books
    books = [
        BookFactory.create_book('general', 'The Great Gatsby', 'F. Scott Fitzgerald', 1925,
                               isbn='9780743273565', genre='Fiction'),
        BookFactory.create_book('general', 'To Kill a Mockingbird', 'Harper Lee', 1960,
                               isbn='9780061120084', genre='Fiction'),
        BookFactory.create_book('general', 'The Hobbit', 'J.R.R. Tolkien', 1937,
                               isbn='9780547928227', genre='Fantasy'),
        BookFactory.create_book('rare', 'Pride and Prejudice (First Edition)', 'Jane Austen', 1813,
                               estimated_value=15000, rarity_level=8),
        BookFactory.create_book('rare', 'The Origin of Species', 'Charles Darwin', 1859,
                               estimated_value=8000, rarity_level=7),
        BookFactory.create_book('ancient', 'The Iliad', 'Homer', -800,
                               origin='Ancient Greece', language='Ancient Greek', translation_available=True)
    ]

    # Add books to the catalog
    for book in books:
        catalog.add_book(book)

    # Create some sample users
    users = [
        UserFactory.create_user('librarian', 'Alice Johnson', 'alice@library.com', 'password123',
                               department='Fiction', staff_id='L001', admin_level=3),
        UserFactory.create_user('librarian', 'Bob Smith', 'bob@library.com', 'password123',
                               department='Non-Fiction', staff_id='L002', admin_level=2),
        UserFactory.create_user('scholar', 'Carol Davis', 'carol@university.edu', 'password123',
                               institution='University of Eldoria', field_of_study='Literature',
                               academic_level='Professor'),
        UserFactory.create_user('scholar', 'David Wilson', 'david@university.edu', 'password123',
                               institution='University of Eldoria', field_of_study='History',
                               academic_level='Graduate'),
        UserFactory.create_user('guest', 'Eve Brown', 'eve@example.com', 'password123',
                               address='123 Main St', phone='555-1234',
                               membership_type='Premium',
                               membership_expiry=datetime.now() + timedelta(days=365))
    ]

    # Add users to the catalog
    for user in users:
        catalog.add_user(user)

    # Create some library sections
    sections = [
        ('Fiction', 'General fiction books', 0),
        ('Non-Fiction', 'General non-fiction books', 0),
        ('Fantasy', 'Fantasy and science fiction books', 0),
        ('Rare Books', 'Rare and valuable books', 1),
        ('Ancient Manuscripts', 'Ancient manuscripts and scrolls', 2)
    ]

    # Add sections to the catalog
    section_ids = {}
    for name, description, access_level in sections:
        section_id = catalog.add_section(name, description, access_level)
        section_ids[name] = section_id

    # Add books to sections
    catalog.add_book_to_section(books[0].book_id, section_ids['Fiction'])
    catalog.add_book_to_section(books[1].book_id, section_ids['Fiction'])
    catalog.add_book_to_section(books[2].book_id, section_ids['Fantasy'])
    catalog.add_book_to_section(books[3].book_id, section_ids['Rare Books'])
    catalog.add_book_to_section(books[4].book_id, section_ids['Rare Books'])
    catalog.add_book_to_section(books[5].book_id, section_ids['Ancient Manuscripts'])

    print("Sample data initialized successfully.")
    return catalog


def setup_event_system():
    """Set up the event notification system."""
    # Create the notification service
    notification_service = NotificationService()

    # Create the event manager
    event_manager = LibraryEventManager()

    # Create observers
    librarian_observer = LibrarianNotificationObserver(notification_service)
    librarian_observer.add_librarian_email('alice@library.com')
    librarian_observer.add_librarian_email('bob@library.com')

    # Create a user service (using the catalog for simplicity)
    user_service = Catalog()
    user_observer = UserNotificationObserver(notification_service, user_service)

    # Create a logging observer
    logging_observer = LoggingObserver('library_events.log')

    # Attach observers to the event manager
    event_manager.attach(librarian_observer)
    event_manager.attach(user_observer)
    event_manager.attach(logging_observer)

    return event_manager


def main():
    """Main entry point for the Enchanted Library system."""
    print("Welcome to the Enchanted Library Management System")
    print("=" * 50)

    # Initialize sample data
    catalog = initialize_sample_data()

    # Set up the event system
    event_manager = setup_event_system()

    # Create the library facade
    library = LibraryFacade()

    # Check command line arguments for interface choice
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'gui':
        # Launch the GUI
        launch_gui(library, catalog, event_manager)
    else:
        # Ask the user which interface to use
        print("\nChoose an interface:")
        print("1. Command Line Interface (CLI)")
        print("2. Graphical User Interface (GUI)")

        choice = input("Enter your choice (1/2): ").strip()

        if choice == '2':
            # Launch the GUI
            launch_gui(library, catalog, event_manager)
        else:
            # Create and start the CLI
            cli = CommandLineInterface(library, catalog, event_manager)
            cli.start()


if __name__ == "__main__":
    main()
