"""
Book Factory implementation for the Enchanted Library system.
This module implements the Factory Pattern for creating different types of books.
"""
import uuid
from models.book import GeneralBook, RareBook, AncientScript


class BookFactory:
    """Factory class for creating different types of books."""
    
    @staticmethod
    def create_book(book_type, title, author, year_published, **kwargs):
        """
        Create a new book of the specified type.
        
        Args:
            book_type (str): Type of book to create ('general', 'rare', or 'ancient')
            title (str): Title of the book
            author (str): Author of the book
            year_published (int): Year the book was published
            **kwargs: Additional parameters specific to the book type
            
        Returns:
            Book: A new book instance of the specified type
            
        Raises:
            ValueError: If an invalid book type is specified
        """
        # Generate a unique ID for the book
        book_id = str(uuid.uuid4())
        
        # Create the appropriate book type
        if book_type.lower() == 'general':
            return BookFactory._create_general_book(book_id, title, author, year_published, **kwargs)
        elif book_type.lower() == 'rare':
            return BookFactory._create_rare_book(book_id, title, author, year_published, **kwargs)
        elif book_type.lower() == 'ancient':
            return BookFactory._create_ancient_script(book_id, title, author, year_published, **kwargs)
        else:
            raise ValueError(f"Invalid book type: {book_type}")
    
    @staticmethod
    def _create_general_book(book_id, title, author, year_published, **kwargs):
        """Create a new general book."""
        isbn = kwargs.get('isbn')
        genre = kwargs.get('genre')
        
        book = GeneralBook(book_id, title, author, year_published, isbn, genre)
        
        # Set additional properties if provided
        if 'is_bestseller' in kwargs:
            book.is_bestseller = kwargs['is_bestseller']
        
        return book
    
    @staticmethod
    def _create_rare_book(book_id, title, author, year_published, **kwargs):
        """Create a new rare book."""
        isbn = kwargs.get('isbn')
        estimated_value = kwargs.get('estimated_value')
        rarity_level = kwargs.get('rarity_level', 1)
        
        book = RareBook(book_id, title, author, year_published, isbn, estimated_value, rarity_level)
        
        # Set additional properties if provided
        if 'special_handling_notes' in kwargs:
            book.special_handling_notes = kwargs['special_handling_notes']
        
        return book
    
    @staticmethod
    def _create_ancient_script(book_id, title, author, year_published, **kwargs):
        """Create a new ancient script."""
        isbn = kwargs.get('isbn')
        origin = kwargs.get('origin')
        language = kwargs.get('language')
        translation_available = kwargs.get('translation_available', False)
        
        book = AncientScript(book_id, title, author, year_published, isbn, origin, language, translation_available)
        
        # Set additional properties if provided
        if 'digital_copy_available' in kwargs:
            book.digital_copy_available = kwargs['digital_copy_available']
        
        # Add preservation requirements if provided
        if 'preservation_requirements' in kwargs:
            for req in kwargs['preservation_requirements']:
                book.add_preservation_requirement(req)
        
        return book
