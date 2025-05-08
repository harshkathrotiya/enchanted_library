"""
Command-Line Interface for the Enchanted Library system.
This module provides a text-based interface for interacting with the library.
"""
from datetime import datetime

from models.book import BookCondition, BookStatus
from models.user import UserRole
from patterns.creational.book_factory import BookFactory
from patterns.creational.user_factory import UserFactory
from patterns.creational.book_builder import BookBuilder, BookDirector
from patterns.behavioral.action_command import CommandInvoker, CheckoutBookCommand, ReturnBookCommand, AddBookCommand
from patterns.structural.data_persistence import DataPersistence
from services.preservation import PreservationService
from services.recommendation import RecommendationService


class CommandLineInterface:
    """Command-line interface for the Enchanted Library system."""

    def __init__(self, library, catalog, event_manager):
        """
        Initialize the CLI with required components.

        Args:
            library: The library facade
            catalog: The library catalog
            event_manager: The event manager
        """
        self._library = library
        self._catalog = catalog
        self._event_manager = event_manager
        self._command_invoker = CommandInvoker()
        self._preservation_service = PreservationService()
        self._recommendation_service = RecommendationService(catalog)
        self._current_user = None

    def start(self):
        """Start the command-line interface."""
        print("Enchanted Library CLI")
        print("Type 'help' for a list of commands, 'exit' to quit.")

        while True:
            # Display current user
            if self._current_user:
                print(f"\nLogged in as: {self._current_user.name} ({self._current_user.get_role().name})")
            else:
                print("\nNot logged in")

            # Get command
            command = input("\nEnter command: ").strip().lower()

            if command == 'exit':
                print("Goodbye!")
                break

            self._process_command(command)

    def _process_command(self, command):
        """
        Process a user command.

        Args:
            command (str): The command to process
        """
        # Split the command into parts
        parts = command.split()

        if not parts:
            return

        main_command = parts[0]

        # Process the command
        if main_command == 'help':
            self._show_help()

        elif main_command == 'login':
            self._login()

        elif main_command == 'logout':
            self._logout()

        elif main_command == 'list':
            if len(parts) > 1:
                if parts[1] == 'books':
                    self._list_books()
                elif parts[1] == 'users':
                    self._list_users()
                elif parts[1] == 'sections':
                    self._list_sections()
                else:
                    print(f"Unknown list type: {parts[1]}")
            else:
                print("Please specify what to list (books, users, sections)")

        elif main_command == 'search':
            if len(parts) > 1:
                search_term = ' '.join(parts[1:])
                self._search_books(search_term)
            else:
                print("Please provide a search term")

        elif main_command == 'view':
            if len(parts) > 1:
                if parts[1] == 'book':
                    if len(parts) > 2:
                        self._view_book(parts[2])
                    else:
                        print("Please provide a book ID")
                elif parts[1] == 'user':
                    if len(parts) > 2:
                        self._view_user(parts[2])
                    else:
                        print("Please provide a user ID")
                else:
                    print(f"Unknown view type: {parts[1]}")
            else:
                print("Please specify what to view (book, user)")

        elif main_command == 'checkout':
            if len(parts) > 1:
                self._checkout_book(parts[1])
            else:
                print("Please provide a book ID")

        elif main_command == 'return':
            if len(parts) > 1:
                self._return_book(parts[1])
            else:
                print("Please provide a book ID")

        elif main_command == 'add':
            if len(parts) > 1:
                if parts[1] == 'book':
                    self._add_book()
                elif parts[1] == 'user':
                    self._add_user()
                else:
                    print(f"Unknown add type: {parts[1]}")
            else:
                print("Please specify what to add (book, user)")

        elif main_command == 'recommend':
            self._recommend_books()

        elif main_command == 'restore':
            if len(parts) > 1:
                self._restore_book(parts[1])
            else:
                print("Please provide a book ID")

        elif main_command == 'save' and len(parts) > 1 and parts[1] == 'data':
            self._save_data()

        elif main_command == 'load' and len(parts) > 1 and parts[1] == 'data':
            self._load_data()

        elif main_command == 'undo':
            self._undo_last_command()

        else:
            print(f"Unknown command: {main_command}")

    def _show_help(self):
        """Show the help menu."""
        print("\nAvailable commands:")
        print("  help                - Show this help menu")
        print("  login               - Log in to the system")
        print("  logout              - Log out of the system")
        print("  list books          - List all books")
        print("  list users          - List all users")
        print("  list sections       - List all library sections")
        print("  search <term>       - Search for books")
        print("  view book <id>      - View details of a book")
        print("  view user <id>      - View details of a user")
        print("  checkout <book_id>  - Check out a book")
        print("  return <book_id>    - Return a book")
        print("  add book            - Add a new book")
        print("  add user            - Add a new user")
        print("  recommend           - Get book recommendations")
        print("  restore <book_id>   - Send a book for restoration")
        print("  save data           - Save library data to JSON files")
        print("  load data           - Load library data from JSON files")
        print("  undo                - Undo the last command")
        print("  exit                - Exit the system")

    def _login(self):
        """Log in to the system."""
        if self._current_user:
            print("Already logged in. Please log out first.")
            return

        email = input("Email: ")
        password = input("Password: ")

        user = self._library.authenticate_user(email, password)

        if user:
            self._current_user = user
            print(f"Logged in as {user.name}")
        else:
            print("Invalid email or password")

    def _logout(self):
        """Log out of the system."""
        if not self._current_user:
            print("Not logged in")
            return

        print(f"Logged out {self._current_user.name}")
        self._current_user = None

    def _list_books(self):
        """List all books in the catalog."""
        books = list(self._catalog._books.values())

        if not books:
            print("No books found")
            return

        print("\nBooks in the catalog:")
        print("-" * 80)
        print(f"{'ID':<36} | {'Title':<30} | {'Author':<20} | {'Status':<10}")
        print("-" * 80)

        for book in books:
            print(f"{book.book_id:<36} | {book.title:<30} | {book.author:<20} | {book.status.name:<10}")

    def _list_users(self):
        """List all users in the catalog."""
        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can list users")
            return

        users = list(self._catalog._users.values())

        if not users:
            print("No users found")
            return

        print("\nUsers in the catalog:")
        print("-" * 80)
        print(f"{'ID':<36} | {'Name':<20} | {'Email':<25} | {'Role':<10}")
        print("-" * 80)

        for user in users:
            print(f"{user.user_id:<36} | {user.name:<20} | {user.email:<25} | {user.get_role().name:<10}")

    def _list_sections(self):
        """List all library sections."""
        sections = list(self._catalog._sections.values())

        if not sections:
            print("No sections found")
            return

        print("\nLibrary sections:")
        print("-" * 80)
        print(f"{'ID':<36} | {'Name':<20} | {'Access Level':<12} | {'Book Count':<10}")
        print("-" * 80)

        for section in sections:
            print(f"{section['id']:<36} | {section['name']:<20} | {section['access_level']:<12} | {len(section['books']):<10}")

    def _search_books(self, search_term):
        """
        Search for books in the catalog.

        Args:
            search_term (str): Term to search for
        """
        # Search in title and author
        books = self._catalog.search_books(title=search_term) + self._catalog.search_books(author=search_term)

        # Remove duplicates
        unique_books = {}
        for book in books:
            unique_books[book.book_id] = book

        books = list(unique_books.values())

        if not books:
            print(f"No books found matching '{search_term}'")
            return

        print(f"\nBooks matching '{search_term}':")
        print("-" * 80)
        print(f"{'ID':<36} | {'Title':<30} | {'Author':<20} | {'Status':<10}")
        print("-" * 80)

        for book in books:
            print(f"{book.book_id:<36} | {book.title:<30} | {book.author:<20} | {book.status.name:<10}")

    def _view_book(self, book_id):
        """
        View details of a book.

        Args:
            book_id (str): ID of the book to view
        """
        book = self._catalog.get_book(book_id)

        if not book:
            print(f"Book not found: {book_id}")
            return

        print("\nBook Details:")
        print(f"ID:             {book.book_id}")
        print(f"Title:          {book.title}")
        print(f"Author:         {book.author}")
        print(f"Year Published: {book.year_published}")
        print(f"ISBN:           {book.isbn or 'N/A'}")
        print(f"Condition:      {book.condition.name}")
        print(f"Status:         {book.status.name}")
        print(f"Location:       {book.location or 'N/A'}")

        # Display book type specific details
        from models.book import GeneralBook, RareBook, AncientScript

        if isinstance(book, GeneralBook):
            print(f"Type:           General Book")
            print(f"Genre:          {book.genre or 'N/A'}")
            print(f"Is Bestseller:  {book.is_bestseller}")
        elif isinstance(book, RareBook):
            print(f"Type:           Rare Book")
            print(f"Estimated Value: ${book.estimated_value or 'N/A'}")
            print(f"Rarity Level:   {book.rarity_level}/10")
            print(f"Requires Gloves: {book.requires_gloves}")
            if book.special_handling_notes:
                print(f"Handling Notes: {book.special_handling_notes}")
        elif isinstance(book, AncientScript):
            print(f"Type:           Ancient Script")
            print(f"Origin:         {book.origin or 'N/A'}")
            print(f"Language:       {book.language or 'N/A'}")
            print(f"Translation:    {'Available' if book.translation_available else 'Not Available'}")
            print(f"Digital Copy:   {'Available' if book.digital_copy_available else 'Not Available'}")
            if book.preservation_requirements:
                print("Preservation Requirements:")
                for req in book.preservation_requirements:
                    print(f"  - {req}")

        # Display availability information
        availability = self._library.get_book_availability(book_id)
        print(f"\nAvailability:   {availability['message']}")

        # Display lending information
        if book.status == BookStatus.BORROWED:
            lending_records = self._catalog.get_book_lending_records(book_id)
            active_records = [r for r in lending_records if r.status.name == 'ACTIVE']

            if active_records:
                record = active_records[0]
                user = self._catalog.get_user(record.user_id)
                print(f"\nCurrently borrowed by: {user.name if user else 'Unknown'}")
                print(f"Due date:             {record.due_date.strftime('%Y-%m-%d')}")

                if record.is_overdue():
                    days_overdue = record.days_overdue()
                    print(f"Overdue by:            {days_overdue} days")
                    print(f"Late fee:              ${book.get_late_fee(days_overdue):.2f}")

    def _view_user(self, user_id):
        """
        View details of a user.

        Args:
            user_id (str): ID of the user to view
        """
        # Check permissions
        if not self._current_user or (self._current_user.get_role() != UserRole.LIBRARIAN and self._current_user.user_id != user_id):
            print("Permission denied: You can only view your own user details or you need to be a librarian")
            return

        user = self._catalog.get_user(user_id)

        if not user:
            print(f"User not found: {user_id}")
            return

        print("\nUser Details:")
        print(f"ID:               {user.user_id}")
        print(f"Name:             {user.name}")
        print(f"Email:            {user.email}")
        print(f"Role:             {user.get_role().name}")
        print(f"Registration Date: {user.registration_date.strftime('%Y-%m-%d')}")
        print(f"Last Login:       {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
        print(f"Active:           {user.active}")

        # Display role specific details
        if user.get_role() == UserRole.LIBRARIAN:
            print(f"Department:       {user.department or 'N/A'}")
            print(f"Staff ID:         {user.staff_id or 'N/A'}")
            print(f"Admin Level:      {user.admin_level}")
        elif user.get_role() == UserRole.SCHOLAR:
            print(f"Institution:      {user.institution or 'N/A'}")
            print(f"Field of Study:   {user.field_of_study or 'N/A'}")
            print(f"Academic Level:   {user.academic_level}")
            if user.research_topics:
                print("Research Topics:")
                for topic in user.research_topics:
                    print(f"  - {topic}")
        elif user.get_role() == UserRole.GUEST:
            print(f"Address:          {user.address or 'N/A'}")
            print(f"Phone:            {user.phone or 'N/A'}")
            print(f"Membership Type:  {user.membership_type}")
            print(f"Membership Expiry: {user.membership_expiry.strftime('%Y-%m-%d') if user.membership_expiry else 'N/A'}")
            print(f"Membership Valid: {user.is_membership_valid()}")

        # Display borrowed books
        borrowed_books = self._library.get_user_borrowed_books(user_id)

        if borrowed_books:
            print("\nCurrently Borrowed Books:")
            print("-" * 80)
            print(f"{'Title':<30} | {'Author':<20} | {'Due Date':<10} | {'Status':<10}")
            print("-" * 80)

            for item in borrowed_books:
                book = item['book']
                due_date = item['due_date']
                status = "Overdue" if due_date < datetime.now() else "On Time"

                print(f"{book.title:<30} | {book.author:<20} | {due_date.strftime('%Y-%m-%d'):<10} | {status:<10}")

    def _checkout_book(self, book_id):
        """
        Check out a book.

        Args:
            book_id (str): ID of the book to check out
        """
        if not self._current_user:
            print("Please log in first")
            return

        # Create and execute the checkout command
        command = CheckoutBookCommand(self._catalog, book_id, self._current_user.user_id)
        result = self._command_invoker.execute_command(command)

        if result['success']:
            print(result['message'])
            print(f"Due date: {result['due_date'].strftime('%Y-%m-%d')}")

            # Notify the event manager
            book = self._catalog.get_book(book_id)
            self._event_manager.book_borrowed(book, self._current_user)
        else:
            print(f"Error: {result['message']}")

    def _return_book(self, book_id):
        """
        Return a book.

        Args:
            book_id (str): ID of the book to return
        """
        if not self._current_user:
            print("Please log in first")
            return

        # Ask if the book's condition has changed
        condition_changed = input("Has the book's condition changed? (y/n): ").lower() == 'y'

        # Create and execute the return command
        command = ReturnBookCommand(self._catalog, book_id, self._current_user.user_id, condition_changed)
        result = self._command_invoker.execute_command(command)

        if result['success']:
            print(result['message'])

            # Notify the event manager
            book = self._catalog.get_book(book_id)
            self._event_manager.book_returned(book, self._current_user)

            # Check if the book needs restoration
            if condition_changed and self._preservation_service.check_needs_restoration(book):
                print("Note: This book needs restoration")
        else:
            print(f"Error: {result['message']}")

    def _add_book(self):
        """Add a new book to the catalog."""
        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can add books")
            return

        print("\nAdd a new book:")

        # Get book type
        book_type = input("Book type (general/rare/ancient): ").lower()
        if book_type not in ['general', 'rare', 'ancient']:
            print("Invalid book type")
            return

        # Get common book information
        title = input("Title: ")
        author = input("Author: ")

        try:
            year_published = int(input("Year published: "))
        except ValueError:
            print("Invalid year")
            return

        isbn = input("ISBN (optional): ")
        if not isbn:
            isbn = None

        # Get book type specific information
        if book_type == 'general':
            genre = input("Genre (optional): ")
            is_bestseller = input("Is bestseller? (y/n): ").lower() == 'y'

            # Create the book using the builder
            builder = BookBuilder()
            book = (builder
                    .set_book_type('general')
                    .set_title(title)
                    .set_author(author)
                    .set_year_published(year_published)
                    .set_isbn(isbn)
                    .set_genre(genre)
                    .set_bestseller(is_bestseller)
                    .build())

        elif book_type == 'rare':
            try:
                estimated_value = float(input("Estimated value ($): "))
            except ValueError:
                print("Invalid value")
                return

            try:
                rarity_level = int(input("Rarity level (1-10): "))
                if rarity_level < 1 or rarity_level > 10:
                    raise ValueError()
            except ValueError:
                print("Invalid rarity level")
                return

            special_handling_notes = input("Special handling notes (optional): ")

            # Create the book using the builder
            builder = BookBuilder()
            book = (builder
                    .set_book_type('rare')
                    .set_title(title)
                    .set_author(author)
                    .set_year_published(year_published)
                    .set_isbn(isbn)
                    .set_estimated_value(estimated_value)
                    .set_rarity_level(rarity_level)
                    .set_special_handling_notes(special_handling_notes)
                    .build())

        elif book_type == 'ancient':
            origin = input("Origin (optional): ")
            language = input("Language (optional): ")
            translation_available = input("Translation available? (y/n): ").lower() == 'y'
            digital_copy_available = input("Digital copy available? (y/n): ").lower() == 'y'

            # Create the book using the builder
            builder = BookBuilder()
            book = (builder
                    .set_book_type('ancient')
                    .set_title(title)
                    .set_author(author)
                    .set_year_published(year_published)
                    .set_isbn(isbn)
                    .set_origin(origin)
                    .set_language(language)
                    .set_translation_available(translation_available)
                    .set_digital_copy_available(digital_copy_available)
                    .build())

        # Get the section to add the book to
        section_name = input("Section name (optional): ")
        if not section_name:
            section_name = None

        # Create and execute the add book command
        command = AddBookCommand(self._catalog, book, section_name)
        result = self._command_invoker.execute_command(command)

        if result['success']:
            print(result['message'])
            print(f"Book ID: {result['book_id']}")

            # Notify the event manager
            self._event_manager.book_added(book)
        else:
            print(f"Error: {result['message']}")

    def _add_user(self):
        """Add a new user to the catalog."""
        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can add users")
            return

        print("\nAdd a new user:")

        # Get user type
        user_type = input("User type (librarian/scholar/guest): ").lower()
        if user_type not in ['librarian', 'scholar', 'guest']:
            print("Invalid user type")
            return

        # Get common user information
        name = input("Name: ")
        email = input("Email: ")
        password = input("Password: ")

        # Get user type specific information
        if user_type == 'librarian':
            department = input("Department (optional): ")
            staff_id = input("Staff ID (optional): ")

            try:
                admin_level = int(input("Admin level (1-3): "))
                if admin_level < 1 or admin_level > 3:
                    raise ValueError()
            except ValueError:
                print("Invalid admin level")
                return

            # Create the user
            user = UserFactory.create_user('librarian', name, email, password,
                                          department=department, staff_id=staff_id,
                                          admin_level=admin_level)

        elif user_type == 'scholar':
            institution = input("Institution (optional): ")
            field_of_study = input("Field of study (optional): ")

            academic_level = input("Academic level (General/Graduate/Professor/Distinguished): ")
            if academic_level not in ["General", "Graduate", "Professor", "Distinguished"]:
                print("Invalid academic level")
                return

            # Create the user
            user = UserFactory.create_user('scholar', name, email, password,
                                          institution=institution, field_of_study=field_of_study,
                                          academic_level=academic_level)

            # Add research topics
            while True:
                topic = input("Add research topic (leave empty to finish): ")
                if not topic:
                    break
                user.add_research_topic(topic)

        elif user_type == 'guest':
            address = input("Address (optional): ")
            phone = input("Phone (optional): ")

            membership_type = input("Membership type (Standard/Premium): ")
            if membership_type not in ["Standard", "Premium"]:
                print("Invalid membership type")
                return

            # Create the user
            user = UserFactory.create_user('guest', name, email, password,
                                          address=address, phone=phone,
                                          membership_type=membership_type)

            # Set membership expiry
            from datetime import datetime, timedelta
            user.membership_expiry = datetime.now() + timedelta(days=365)

        # Add the user to the catalog
        user_id = self._catalog.add_user(user)

        print(f"User added successfully")
        print(f"User ID: {user_id}")

        # Notify the event manager
        self._event_manager.user_registered(user)

    def _recommend_books(self):
        """Get book recommendations."""
        if not self._current_user:
            print("Please log in first")
            return

        # Get recommendations for the current user
        recommendations = self._recommendation_service.get_recommendations(self._current_user.user_id)

        if not recommendations:
            print("No recommendations available")
            return

        print("\nRecommended Books:")
        print("-" * 80)
        print(f"{'Title':<30} | {'Author':<20} | {'Year':<6} | {'Type':<10}")
        print("-" * 80)

        for book in recommendations:
            # Determine book type
            from models.book import GeneralBook, RareBook, AncientScript

            if isinstance(book, GeneralBook):
                book_type = "General"
            elif isinstance(book, RareBook):
                book_type = "Rare"
            elif isinstance(book, AncientScript):
                book_type = "Ancient"
            else:
                book_type = "Unknown"

            print(f"{book.title:<30} | {book.author:<20} | {book.year_published:<6} | {book_type:<10}")

    def _restore_book(self, book_id):
        """
        Send a book for restoration.

        Args:
            book_id (str): ID of the book to restore
        """
        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can send books for restoration")
            return

        book = self._catalog.get_book(book_id)

        if not book:
            print(f"Book not found: {book_id}")
            return

        # Check if the book needs restoration
        if not self._preservation_service.check_needs_restoration(book):
            print("This book does not need restoration")
            proceed = input("Proceed anyway? (y/n): ").lower() == 'y'
            if not proceed:
                return

        # Get restoration notes
        notes = input("Restoration notes (optional): ")

        # Add the book to the restoration queue
        result = self._preservation_service.add_to_restoration_queue(book, priority=5, notes=notes)

        if result['success']:
            print(result['message'])
            print(f"Estimated completion: {result['estimated_completion'].strftime('%Y-%m-%d')}")

            # Update the book in the catalog
            self._catalog.update_book(book)

            # Notify the event manager
            self._event_manager.book_needs_restoration(book)
        else:
            print(f"Error: {result['message']}")

    def _save_data(self):
        """Save library data to JSON files."""
        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can save library data")
            return

        # Save catalog data
        catalog_file = input("Catalog file name (default: library_catalog.json): ").strip()
        if not catalog_file:
            catalog_file = "library_catalog.json"

        success = DataPersistence.save_catalog_to_json(self._catalog, catalog_file)
        if success:
            print(f"Catalog data saved to {catalog_file}")
        else:
            print(f"Error saving catalog data to {catalog_file}")

        # Save user data
        users_file = input("Users file name (default: library_users.json): ").strip()
        if not users_file:
            users_file = "library_users.json"

        success = DataPersistence.save_users_to_json(self._catalog, users_file)
        if success:
            print(f"User data saved to {users_file}")
        else:
            print(f"Error saving user data to {users_file}")

    def _load_data(self):
        """Load library data from JSON files."""
        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can load library data")
            return

        # Load catalog data
        catalog_file = input("Catalog file name (default: library_catalog.json): ").strip()
        if not catalog_file:
            catalog_file = "library_catalog.json"

        success = DataPersistence.load_catalog_from_json(self._catalog, catalog_file)
        if success:
            print(f"Catalog data loaded from {catalog_file}")
        else:
            print(f"Error loading catalog data from {catalog_file}")

        # Load user data
        users_file = input("Users file name (default: library_users.json): ").strip()
        if not users_file:
            users_file = "library_users.json"

        success = DataPersistence.load_users_from_json(self._catalog, users_file)
        if success:
            print(f"User data loaded from {users_file}")
        else:
            print(f"Error loading user data from {users_file}")

    def _undo_last_command(self):
        """Undo the last command."""
        result = self._command_invoker.undo_last_command()

        if result['success']:
            print(result['message'])
        else:
            print(f"Error: {result['message']}")
