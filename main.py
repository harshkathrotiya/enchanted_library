
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

    catalog = Catalog()

    books = [
        BookFactory.create_book('general', 'The White Tiger', 'Aravind Adiga', 2008,
                               isbn='9781416562603', genre='Fiction'),
        BookFactory.create_book('general', 'The God of Small Things', 'Arundhati Roy', 1997,
                               isbn='9780679457312', genre='Fiction'),
        BookFactory.create_book('general', 'Midnight\'s Children', 'Salman Rushdie', 1981,
                               isbn='9780099578512', genre='Fantasy'),
        BookFactory.create_book('rare', 'Gitanjali (First Edition)', 'Rabindranath Tagore', 1910,
                               estimated_value=18000, rarity_level=9),
        BookFactory.create_book('rare', 'Discovery of India', 'Jawaharlal Nehru', 1946,
                               estimated_value=12000, rarity_level=8),
        BookFactory.create_book('ancient', 'Arthashastra', 'Kautilya', -300,
                               origin='Ancient India', language='Sanskrit', translation_available=True)
    ]

    for book in books:
        catalog.add_book(book)

    users = [
        UserFactory.create_user('librarian', 'Aarav Sharma', 'aarav@library.com', 'password123',
                               department='Fiction', staff_id='L001', admin_level=3),
        UserFactory.create_user('librarian', 'Priya Patel', 'priya@library.com', 'password123',
                               department='Non-Fiction', staff_id='L002', admin_level=2),
        UserFactory.create_user('scholar', 'Dr. Vikram Mehta', 'vikram@university.edu', 'password123',
                               institution='University of Delhi', field_of_study='Literature',
                               academic_level='Professor'),
        UserFactory.create_user('scholar', 'Neha Gupta', 'neha@university.edu', 'password123',
                               institution='University of Mumbai', field_of_study='History',
                               academic_level='Graduate'),
        UserFactory.create_user('guest', 'Arjun Singh', 'arjun@example.com', 'password123',
                               address='42 Gandhi Road', phone='9876543210',
                               membership_type='Premium',
                               membership_expiry=datetime.now() + timedelta(days=365))
    ]

    for user in users:
        catalog.add_user(user)

    sections = [
        ('Fiction', 'Contemporary Indian fiction', 0),
        ('Non-Fiction', 'Indian non-fiction and biographies', 0),
        ('Classical Literature', 'Classical Indian literature', 0),
        ('Rare Books', 'Rare and valuable Indian books', 1),
        ('Ancient Manuscripts', 'Ancient Sanskrit and regional manuscripts', 2)
    ]

    section_ids = {}
    for name, description, access_level in sections:
        section_id = catalog.add_section(name, description, access_level)
        section_ids[name] = section_id

    catalog.add_book_to_section(books[0].book_id, section_ids['Fiction'])
    catalog.add_book_to_section(books[1].book_id, section_ids['Fiction'])
    catalog.add_book_to_section(books[2].book_id, section_ids['Classical Literature'])
    catalog.add_book_to_section(books[3].book_id, section_ids['Rare Books'])
    catalog.add_book_to_section(books[4].book_id, section_ids['Non-Fiction'])
    catalog.add_book_to_section(books[5].book_id, section_ids['Ancient Manuscripts'])

    print("Sample data initialized successfully.")
    return catalog

def setup_event_system():

    notification_service = NotificationService()

    event_manager = LibraryEventManager()

    librarian_observer = LibrarianNotificationObserver(notification_service)
    librarian_observer.add_librarian_email('aarav@library.com')
    librarian_observer.add_librarian_email('priya@library.com')

    user_service = Catalog()
    user_observer = UserNotificationObserver(notification_service, user_service)

    logging_observer = LoggingObserver('library_events.log')

    event_manager.attach(librarian_observer)
    event_manager.attach(user_observer)
    event_manager.attach(logging_observer)

    return event_manager

def main():

    print("Welcome to the Enchanted Library Management System")
    print("=" * 50)

    catalog = initialize_sample_data()

    event_manager = setup_event_system()

    library = LibraryFacade()

    if len(sys.argv) > 1 and sys.argv[1].lower() == 'gui':
        launch_gui(library, catalog, event_manager)
    else:
        print("\nChoose an interface:")
        print("1. Command Line Interface (CLI)")
        print("2. Graphical User Interface (GUI)")

        choice = input("Enter your choice (1/2): ").strip()

        if choice == '2':
            launch_gui(library, catalog, event_manager)
        else:
            cli = CommandLineInterface(library, catalog, event_manager)
            cli.start()

if __name__ == "__main__":
    main()
