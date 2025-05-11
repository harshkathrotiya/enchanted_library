
from datetime import datetime, timedelta

from models.book import BookCondition, BookStatus
from models.user import UserRole
from patterns.creational.book_factory import BookFactory
from patterns.creational.user_factory import UserFactory
from patterns.creational.book_builder import BookBuilder, BookDirector
from patterns.behavioral.action_command import CommandInvoker, CheckoutBookCommand, ReturnBookCommand, AddBookCommand
from patterns.structural.data_persistence import DataPersistence
from services.preservation import PreservationService, PreservationAction
from services.recommendation import RecommendationService
from patterns.structural.legacy_adapter import LegacyRecordFormat
from services.fee_calculator import FeeCalculator

class CommandLineInterface:

    def __init__(self, library, catalog, event_manager):

        self._library = library
        self._catalog = catalog
        self._event_manager = event_manager
        self._command_invoker = CommandInvoker()
        self._preservation_service = PreservationService(catalog, event_manager)
        self._recommendation_service = RecommendationService(catalog)
        self._current_user = None
        self._data_persistence = DataPersistence()

        from patterns.structural.legacy_adapter import LegacyRecordAdapter
        from patterns.behavioral.lending_strategy import LendingStrategyContext

        self._legacy_adapter = LegacyRecordAdapter(catalog)
        self._lending_strategy = LendingStrategyContext()

    def start(self):

        print("Enchanted Library CLI")
        print("Type 'help' for a list of commands, 'exit' to quit.")

        while True:
            if self._current_user:
                print(f"\nLogged in as: {self._current_user.name} ({self._current_user.get_role().name})")
            else:
                print("\nNot logged in")

            command = input("\nEnter command: ").strip().lower()

            if command == 'exit':
                print("Goodbye!")
                break

            self._process_command(command)

    def _process_command(self, command):
        

        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:]

        if cmd == 'help':
            self._show_help()
        elif cmd == 'login':
            self._login()
        elif cmd == 'logout':
            self._logout()
        elif cmd == 'search':
            self._search_books(args)
        elif cmd == 'view':
            if len(args) > 0 and args[0] == 'book':
                self._view_book(args[1:])
            elif len(args) > 0 and args[0] == 'user':
                self._view_user(args[1:])
            else:
                print("Invalid view command. Try 'view book <id>' or 'view user <id>'")
        elif cmd == 'add':
            if len(args) > 0 and args[0] == 'book':
                self._add_book()
            elif len(args) > 0 and args[0] == 'user':
                self._add_user()
            else:
                print("Invalid add command. Try 'add book' or 'add user'")
        elif cmd == 'checkout':
            self._checkout_book(args)
        elif cmd == 'return':
            self._return_book(args)
        elif cmd == 'recommend':
            self._recommend_books(args)
        elif cmd == 'preservation':
            self._preservation_menu(args)
        elif cmd == 'import':
            self._import_legacy_records(args)
        elif cmd == 'export':
            self._export_data(args)
        elif cmd == 'report':
            self._generate_report(args)
        elif cmd == 'project':
            self._manage_research_project(args)
        elif cmd == 'seasonal':
            self._manage_seasonal_strategy(args)
        elif cmd == 'section':
            self._section_management_menu(args)
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for a list of commands")

        if not parts:
            return

        main_command = parts[0]

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
        print("\nAdvanced commands:")
        print("  section             - Access section management menu")
        print("  preservation        - Access preservation menu")
        print("  import <format>     - Import legacy records (csv/json/handwritten)")
        print("  export <format>     - Export library data (csv/json)")
        print("  report <type>       - Generate reports (overdue/condition/usage)")
        print("  project             - Manage research projects")
        print("  seasonal            - Manage seasonal lending strategies")
        print("  undo                - Undo the last command")
        print("  exit                - Exit the system")

    def _login(self):

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

        if not self._current_user:
            print("Not logged in")
            return

        print(f"Logged out {self._current_user.name}")
        self._current_user = None

    def _list_books(self):

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

        books = self._catalog.search_books(title=search_term) + self._catalog.search_books(author=search_term)

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

        availability = self._library.get_book_availability(book_id)
        print(f"\nAvailability:   {availability['message']}")

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

        if not self._current_user:
            print("Please log in first")
            return

        command = CheckoutBookCommand(self._catalog, book_id, self._current_user.user_id)
        result = self._command_invoker.execute_command(command)

        if result['success']:
            print(result['message'])
            print(f"Due date: {result['due_date'].strftime('%Y-%m-%d')}")

            book = self._catalog.get_book(book_id)
            self._event_manager.book_borrowed(book, self._current_user)
        else:
            print(f"Error: {result['message']}")

    def _return_book(self, book_id):

        if not self._current_user:
            print("Please log in first")
            return

        condition_changed = input("Has the book's condition changed? (y/n): ").lower() == 'y'

        command = ReturnBookCommand(self._catalog, book_id, self._current_user.user_id, condition_changed)
        result = self._command_invoker.execute_command(command)

        if result['success']:
            print(result['message'])

            book = self._catalog.get_book(book_id)
            self._event_manager.book_returned(book, self._current_user)

            if condition_changed and self._preservation_service.check_needs_restoration(book):
                print("Note: This book needs restoration")
        else:
            print(f"Error: {result['message']}")

    def _add_book(self):

        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can add books")
            return

        print("\nAdd a new book:")

        book_type = input("Book type (general/rare/ancient): ").lower()
        if book_type not in ['general', 'rare', 'ancient']:
            print("Invalid book type")
            return

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

        if book_type == 'general':
            genre = input("Genre (optional): ")
            is_bestseller = input("Is bestseller? (y/n): ").lower() == 'y'

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

        section_name = input("Section name (optional): ")
        if not section_name:
            section_name = None

        command = AddBookCommand(self._catalog, book, section_name)
        result = self._command_invoker.execute_command(command)

        if result['success']:
            print(result['message'])
            print(f"Book ID: {result['book_id']}")

            self._event_manager.book_added(book)
        else:
            print(f"Error: {result['message']}")

    def _add_user(self):

        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can add users")
            return

        print("\nAdd a new user:")

        user_type = input("User type (librarian/scholar/guest): ").lower()
        if user_type not in ['librarian', 'scholar', 'guest']:
            print("Invalid user type")
            return

        name = input("Name: ")
        email = input("Email: ")
        password = input("Password: ")

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

            user = UserFactory.create_user('scholar', name, email, password,
                                          institution=institution, field_of_study=field_of_study,
                                          academic_level=academic_level)

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

            user = UserFactory.create_user('guest', name, email, password,
                                          address=address, phone=phone,
                                          membership_type=membership_type)

            from datetime import datetime, timedelta
            user.membership_expiry = datetime.now() + timedelta(days=365)

        user_id = self._catalog.add_user(user)

        print(f"User added successfully")
        print(f"User ID: {user_id}")

        self._event_manager.user_registered(user)

    def _recommend_books(self):

        if not self._current_user:
            print("Please log in first")
            return

        recommendations = self._recommendation_service.get_recommendations(self._current_user.user_id)

        if not recommendations:
            print("No recommendations available")
            return

        print("\nRecommended Books:")
        print("-" * 80)
        print(f"{'Title':<30} | {'Author':<20} | {'Year':<6} | {'Type':<10}")
        print("-" * 80)

        for book in recommendations:
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

        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can send books for restoration")
            return

        book = self._catalog.get_book(book_id)

        if not book:
            print(f"Book not found: {book_id}")
            return

        if not self._preservation_service.check_needs_restoration(book):
            print("This book does not need restoration")
            proceed = input("Proceed anyway? (y/n): ").lower() == 'y'
            if not proceed:
                return

        notes = input("Restoration notes (optional): ")

        result = self._preservation_service.add_to_restoration_queue(book, priority=5, notes=notes)

        if result['success']:
            print(result['message'])
            print(f"Estimated completion: {result['estimated_completion'].strftime('%Y-%m-%d')}")

            self._catalog.update_book(book)

            self._event_manager.book_needs_restoration(book)
        else:
            print(f"Error: {result['message']}")

    def _save_data(self):

        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can save library data")
            return

        catalog_file = input("Catalog file name (default: library_catalog.json): ").strip()
        if not catalog_file:
            catalog_file = "library_catalog.json"

        success = DataPersistence.save_catalog_to_json(self._catalog, catalog_file)
        if success:
            print(f"Catalog data saved to {catalog_file}")
        else:
            print(f"Error saving catalog data to {catalog_file}")

        users_file = input("Users file name (default: library_users.json): ").strip()
        if not users_file:
            users_file = "library_users.json"

        success = DataPersistence.save_users_to_json(self._catalog, users_file)
        if success:
            print(f"User data saved to {users_file}")
        else:
            print(f"Error saving user data to {users_file}")

    def _load_data(self):

        if not self._current_user or self._current_user.get_role() != UserRole.LIBRARIAN:
            print("Permission denied: Only librarians can load library data")
            return

        catalog_file = input("Catalog file name (default: library_catalog.json): ").strip()
        if not catalog_file:
            catalog_file = "library_catalog.json"

        success = DataPersistence.load_catalog_from_json(self._catalog, catalog_file)
        if success:
            print(f"Catalog data loaded from {catalog_file}")
        else:
            print(f"Error loading catalog data from {catalog_file}")

        users_file = input("Users file name (default: library_users.json): ").strip()
        if not users_file:
            users_file = "library_users.json"

        success = DataPersistence.load_users_from_json(self._catalog, users_file)
        if success:
            print(f"User data loaded from {users_file}")
        else:
            print(f"Error loading user data from {users_file}")

    def _undo_last_command(self):

        result = self._command_invoker.undo_last_command()

        if result['success']:
            print(result['message'])
        else:
            print(f"Error: {result['message']}")

    def _section_management_menu(self, args):
        

        if not self._current_user:
            print("Please log in first")
            return

        if self._current_user.get_role().name != 'LIBRARIAN':
            print("Permission denied: Only librarians can manage sections")
            return

        if not args:
            print("\nSection Management Menu:")
            print("  section list                - List all sections")
            print("  section view <id>           - View section details")
            print("  section add                 - Add a new section")
            print("  section edit <id>           - Edit a section")
            print("  section delete <id>         - Delete a section")
            print("  section assign <book> <section> - Assign a book to a section")
            print("  section remove <book> <section> - Remove a book from a section")
            return

        action = args[0]

        if action == 'list':
            self._list_sections()

        elif action == 'view' and len(args) > 1:
            self._view_section(args[1])

        elif action == 'add':
            self._add_section()

        elif action == 'edit' and len(args) > 1:
            self._edit_section(args[1])

        elif action == 'delete' and len(args) > 1:
            self._delete_section(args[1])

        elif action == 'assign' and len(args) > 2:
            self._assign_book_to_section(args[1], args[2])

        elif action == 'remove' and len(args) > 2:
            self._remove_book_from_section(args[1], args[2])

        else:
            print("Invalid section command")
            print("Type 'section' for a list of section commands")

    def _view_section(self, section_id):
        

        section = self._catalog.get_section(section_id)

        if not section:
            print(f"Section not found: {section_id}")
            return

        print(f"\nSection Details: {section['name']}")
        print("-" * 80)
        print(f"ID: {section['id']}")
        print(f"Name: {section['name']}")
        print(f"Description: {section['description']}")

        access_level_names = ["Public", "Restricted", "Highly Restricted"]
        access_level = section['access_level']
        if 0 <= access_level < len(access_level_names):
            access_level_name = access_level_names[access_level]
        else:
            access_level_name = f"Level {access_level}"

        print(f"Access Level: {access_level_name}")
        print(f"Book Count: {len(section['books'])}")

        if section['books']:
            print("\nBooks in this section:")
            print("-" * 80)
            print(f"{'ID':<36} | {'Title':<30} | {'Author':<20} | {'Status':<10}")
            print("-" * 80)

            for book_id in section['books']:
                book = self._catalog.get_book(book_id)
                if book:
                    print(f"{book.book_id:<36} | {book.title:<30} | {book.author:<20} | {book.status.name:<10}")

    def _add_section(self):
        

        print("\nAdd a new section:")

        name = input("Section name: ")
        if not name:
            print("Section name is required")
            return

        for section in self._catalog._sections.values():
            if section['name'].lower() == name.lower():
                print(f"Section name '{name}' already exists")
                return

        description = input("Description: ")

        access_level_options = ["0 - Public", "1 - Restricted", "2 - Highly Restricted"]
        print("\nAccess Levels:")
        for option in access_level_options:
            print(f"  {option}")

        try:
            access_level = int(input("Access level (0-2): "))
            if access_level < 0 or access_level > 2:
                raise ValueError()
        except ValueError:
            print("Invalid access level")
            return

        section_id = self._catalog.add_section(name, description, access_level)

        if section_id:
            print(f"Section '{name}' added successfully")
            print(f"Section ID: {section_id}")
        else:
            print("Failed to add section")

    def _edit_section(self, section_id):
        

        section = self._catalog.get_section(section_id)

        if not section:
            print(f"Section not found: {section_id}")
            return

        print(f"\nEdit section: {section['name']}")

        name = input(f"Section name [{section['name']}]: ")
        if not name:
            name = section['name']
        else:
            for s_id, s in self._catalog._sections.items():
                if s_id != section_id and s['name'].lower() == name.lower():
                    print(f"Section name '{name}' already exists")
                    return

        description = input(f"Description [{section['description']}]: ")
        if not description:
            description = section['description']

        access_level_options = ["0 - Public", "1 - Restricted", "2 - Highly Restricted"]
        print("\nAccess Levels:")
        for option in access_level_options:
            print(f"  {option}")

        try:
            access_level_input = input(f"Access level (0-2) [{section['access_level']}]: ")
            if access_level_input:
                access_level = int(access_level_input)
                if access_level < 0 or access_level > 2:
                    raise ValueError()
            else:
                access_level = section['access_level']
        except ValueError:
            print("Invalid access level")
            return

        section['name'] = name
        section['description'] = description
        section['access_level'] = access_level

        print(f"Section '{name}' updated successfully")

    def _delete_section(self, section_id):
        

        section = self._catalog.get_section(section_id)

        if not section:
            print(f"Section not found: {section_id}")
            return

        if section['books']:
            confirm = input(f"Section '{section['name']}' contains {len(section['books'])} books. "
                          f"Deleting this section will remove these books from the section, "
                          f"but not from the catalog. Continue? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled")
                return

        if section_id in self._catalog._sections:
            del self._catalog._sections[section_id]
            print(f"Section '{section['name']}' deleted successfully")
        else:
            print("Failed to delete section")

    def _assign_book_to_section(self, book_id, section_id):
        

        book = self._catalog.get_book(book_id)
        if not book:
            print(f"Book not found: {book_id}")
            return

        section = self._catalog.get_section(section_id)
        if not section:
            print(f"Section not found: {section_id}")
            return

        result = self._catalog.add_book_to_section(book_id, section_id)

        if result:
            print(f"Book '{book.title}' assigned to section '{section['name']}' successfully")
        else:
            print("Failed to assign book to section")

    def _remove_book_from_section(self, book_id, section_id):
        

        book = self._catalog.get_book(book_id)
        if not book:
            print(f"Book not found: {book_id}")
            return

        section = self._catalog.get_section(section_id)
        if not section:
            print(f"Section not found: {section_id}")
            return

        if book_id not in section['books']:
            print(f"Book '{book.title}' is not in section '{section['name']}'")
            return

        section['books'].remove(book_id)
        print(f"Book '{book.title}' removed from section '{section['name']}' successfully")
