
import uuid
from models.book import GeneralBook, RareBook, AncientScript

class BookFactory:
    

    @staticmethod
    def create_book(book_type, title, author, year_published, **kwargs):
        
        book_id = str(uuid.uuid4())

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
        
        isbn = kwargs.get('isbn')
        genre = kwargs.get('genre')
        quantity = kwargs.get('quantity', 1)

        book = GeneralBook(book_id, title, author, year_published, isbn, genre, quantity=quantity)

        if 'is_bestseller' in kwargs:
            book.is_bestseller = kwargs['is_bestseller']

        return book

    @staticmethod
    def _create_rare_book(book_id, title, author, year_published, **kwargs):
        
        isbn = kwargs.get('isbn')
        estimated_value = kwargs.get('estimated_value')
        rarity_level = kwargs.get('rarity_level', 1)
        quantity = kwargs.get('quantity', 1)

        book = RareBook(book_id, title, author, year_published, isbn, estimated_value, rarity_level)
        book.quantity = quantity

        if 'special_handling_notes' in kwargs:
            book.special_handling_notes = kwargs['special_handling_notes']

        return book

    @staticmethod
    def _create_ancient_script(book_id, title, author, year_published, **kwargs):
        
        isbn = kwargs.get('isbn')
        origin = kwargs.get('origin')
        language = kwargs.get('language')
        translation_available = kwargs.get('translation_available', False)
        quantity = kwargs.get('quantity', 1)

        book = AncientScript(book_id, title, author, year_published, isbn, origin, language, translation_available)
        book.quantity = quantity

        if 'digital_copy_available' in kwargs:
            book.digital_copy_available = kwargs['digital_copy_available']

        if 'preservation_requirements' in kwargs:
            for req in kwargs['preservation_requirements']:
                book.add_preservation_requirement(req)

        return book
