"""
Book Builder implementation for the Enchanted Library system.
This module implements the Builder Pattern for creating complex book objects.
"""
from models.book import BookCondition, BookStatus
from patterns.creational.book_factory import BookFactory


class BookBuilder:
    """Builder class for creating complex book objects with many optional attributes."""
    
    def __init__(self):
        """Initialize the builder with default values."""
        self._book_type = None
        self._title = None
        self._author = None
        self._year_published = None
        self._isbn = None
        self._condition = BookCondition.GOOD
        self._status = BookStatus.AVAILABLE
        self._location = None
        
        # General book attributes
        self._genre = None
        self._is_bestseller = False
        
        # Rare book attributes
        self._estimated_value = None
        self._rarity_level = 1
        self._special_handling_notes = ""
        
        # Ancient script attributes
        self._origin = None
        self._language = None
        self._translation_available = False
        self._preservation_requirements = []
        self._digital_copy_available = False
    
    def set_book_type(self, book_type):
        """Set the type of book to build."""
        if book_type not in ['general', 'rare', 'ancient']:
            raise ValueError(f"Invalid book type: {book_type}")
        self._book_type = book_type
        return self
    
    def set_title(self, title):
        """Set the title of the book."""
        self._title = title
        return self
    
    def set_author(self, author):
        """Set the author of the book."""
        self._author = author
        return self
    
    def set_year_published(self, year):
        """Set the publication year of the book."""
        self._year_published = year
        return self
    
    def set_isbn(self, isbn):
        """Set the ISBN of the book."""
        self._isbn = isbn
        return self
    
    def set_condition(self, condition):
        """Set the condition of the book."""
        self._condition = condition
        return self
    
    def set_status(self, status):
        """Set the status of the book."""
        self._status = status
        return self
    
    def set_location(self, location):
        """Set the location of the book in the library."""
        self._location = location
        return self
    
    # General book specific methods
    def set_genre(self, genre):
        """Set the genre of the book (for general books)."""
        self._genre = genre
        return self
    
    def set_bestseller(self, is_bestseller):
        """Set whether the book is a bestseller (for general books)."""
        self._is_bestseller = is_bestseller
        return self
    
    # Rare book specific methods
    def set_estimated_value(self, value):
        """Set the estimated value of the book (for rare books)."""
        self._estimated_value = value
        return self
    
    def set_rarity_level(self, level):
        """Set the rarity level of the book (for rare books)."""
        self._rarity_level = level
        return self
    
    def set_special_handling_notes(self, notes):
        """Set special handling notes for the book (for rare books)."""
        self._special_handling_notes = notes
        return self
    
    # Ancient script specific methods
    def set_origin(self, origin):
        """Set the origin of the ancient script."""
        self._origin = origin
        return self
    
    def set_language(self, language):
        """Set the language of the ancient script."""
        self._language = language
        return self
    
    def set_translation_available(self, available):
        """Set whether a translation is available for the ancient script."""
        self._translation_available = available
        return self
    
    def add_preservation_requirement(self, requirement):
        """Add a preservation requirement for the ancient script."""
        self._preservation_requirements.append(requirement)
        return self
    
    def set_digital_copy_available(self, available):
        """Set whether a digital copy is available for the ancient script."""
        self._digital_copy_available = available
        return self
    
    def build(self):
        """
        Build and return the book object with all the specified attributes.
        
        Returns:
            Book: The constructed book object
            
        Raises:
            ValueError: If required attributes are missing
        """
        # Validate required attributes
        if not self._book_type:
            raise ValueError("Book type is required")
        if not self._title:
            raise ValueError("Title is required")
        if not self._author:
            raise ValueError("Author is required")
        if not self._year_published:
            raise ValueError("Year published is required")
        
        # Prepare kwargs based on book type
        kwargs = {'isbn': self._isbn}
        
        if self._book_type == 'general':
            kwargs['genre'] = self._genre
            kwargs['is_bestseller'] = self._is_bestseller
        
        elif self._book_type == 'rare':
            kwargs['estimated_value'] = self._estimated_value
            kwargs['rarity_level'] = self._rarity_level
            kwargs['special_handling_notes'] = self._special_handling_notes
        
        elif self._book_type == 'ancient':
            kwargs['origin'] = self._origin
            kwargs['language'] = self._language
            kwargs['translation_available'] = self._translation_available
            kwargs['preservation_requirements'] = self._preservation_requirements
            kwargs['digital_copy_available'] = self._digital_copy_available
        
        # Create the book using the factory
        book = BookFactory.create_book(
            self._book_type,
            self._title,
            self._author,
            self._year_published,
            **kwargs
        )
        
        # Set common attributes
        book.condition = self._condition
        book.status = self._status
        book.location = self._location
        
        return book


class BookDirector:
    """
    Director class that uses the BookBuilder to create predefined book configurations.
    This simplifies the creation of common book types.
    """
    
    @staticmethod
    def create_standard_fiction_book(title, author, year_published, genre):
        """Create a standard fiction book with default settings."""
        return (BookBuilder()
                .set_book_type('general')
                .set_title(title)
                .set_author(author)
                .set_year_published(year_published)
                .set_genre(genre)
                .set_condition(BookCondition.GOOD)
                .set_status(BookStatus.AVAILABLE)
                .build())
    
    @staticmethod
    def create_bestseller(title, author, year_published, genre):
        """Create a bestseller book with appropriate settings."""
        return (BookBuilder()
                .set_book_type('general')
                .set_title(title)
                .set_author(author)
                .set_year_published(year_published)
                .set_genre(genre)
                .set_bestseller(True)
                .set_condition(BookCondition.EXCELLENT)
                .set_status(BookStatus.AVAILABLE)
                .build())
    
    @staticmethod
    def create_valuable_rare_book(title, author, year_published, estimated_value, rarity_level):
        """Create a valuable rare book with appropriate settings."""
        return (BookBuilder()
                .set_book_type('rare')
                .set_title(title)
                .set_author(author)
                .set_year_published(year_published)
                .set_estimated_value(estimated_value)
                .set_rarity_level(rarity_level)
                .set_condition(BookCondition.GOOD)
                .set_status(BookStatus.AVAILABLE)
                .build())
    
    @staticmethod
    def create_ancient_manuscript(title, author, year_published, origin, language):
        """Create an ancient manuscript with appropriate settings."""
        builder = (BookBuilder()
                  .set_book_type('ancient')
                  .set_title(title)
                  .set_author(author)
                  .set_year_published(year_published)
                  .set_origin(origin)
                  .set_language(language)
                  .set_condition(BookCondition.FAIR)
                  .set_status(BookStatus.AVAILABLE))
        
        # Add standard preservation requirements
        builder.add_preservation_requirement("Temperature control: 18-20°C")
        builder.add_preservation_requirement("Humidity control: 40-45%")
        builder.add_preservation_requirement("Light exposure: <50 lux")
        
        return builder.build()
