

import csv
import json
from datetime import datetime

from models.book import BookCondition, BookStatus
from patterns.creational.book_factory import BookFactory
from patterns.creational.user_factory import UserFactory

class LegacyRecordFormat:
    
    CSV = "csv"
    JSON = "json"
    HANDWRITTEN = "handwritten"

class LegacyRecordAdapter:
    
    
    def __init__(self, catalog):
        
        self._catalog = catalog
    
    def import_legacy_books(self, file_path, format_type):
        
        if format_type == LegacyRecordFormat.CSV:
            return self._import_from_csv(file_path)
        elif format_type == LegacyRecordFormat.JSON:
            return self._import_from_json(file_path)
        elif format_type == LegacyRecordFormat.HANDWRITTEN:
            return self._import_from_handwritten(file_path)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _import_from_csv(self, file_path):
        
        imported_count = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    try:
                        book_type = row.get('type', 'general').lower()
                        
                        book = BookFactory.create_book(
                            book_type,
                            row['title'],
                            row['author'],
                            int(row['year_published']),
                            isbn=row.get('isbn'),
                            quantity=int(row.get('quantity', 1))
                        )
                        
                        if book_type == 'general':
                            book.genre = row.get('genre')
                            book.is_bestseller = row.get('is_bestseller', '').lower() == 'true'
                        elif book_type == 'rare':
                            if 'estimated_value' in row:
                                book.estimated_value = float(row['estimated_value'])
                            if 'rarity_level' in row:
                                book.rarity_level = int(row['rarity_level'])
                        elif book_type == 'ancient':
                            book.origin = row.get('origin')
                            book.language = row.get('language')
                            book.translation_available = row.get('translation_available', '').lower() == 'true'
                        
                        if 'condition' in row:
                            try:
                                book.condition = BookCondition[row['condition'].upper()]
                            except KeyError:
                                book.condition = BookCondition.GOOD
                        
                        self._catalog.add_book(book)
                        
                        if 'section' in row and row['section']:
                            section = self._catalog.get_section_by_name(row['section'])
                            if not section:
                                section_id = self._catalog.add_section(row['section'], f"Section for {row['section']} books")
                            else:
                                section_id = section['id']
                            self._catalog.add_book_to_section(book.book_id, section_id)
                        
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Error importing row {reader.line_num}: {str(e)}")
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to import CSV file: {str(e)}",
                'imported_count': imported_count,
                'errors': errors
            }
        
        return {
            'success': True,
            'message': f"Successfully imported {imported_count} books from CSV",
            'imported_count': imported_count,
            'errors': errors
        }
    
    def _import_from_json(self, file_path):
        
        imported_count = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                
                for book_data in data.get('books', []):
                    try:
                        book_type = book_data.get('type', 'general').lower()
                        
                        book = BookFactory.create_book(
                            book_type,
                            book_data['title'],
                            book_data['author'],
                            int(book_data['year_published']),
                            isbn=book_data.get('isbn'),
                            quantity=int(book_data.get('quantity', 1))
                        )
                        
                        if book_type == 'general':
                            book.genre = book_data.get('genre')
                            book.is_bestseller = book_data.get('is_bestseller', False)
                        elif book_type == 'rare':
                            if 'estimated_value' in book_data:
                                book.estimated_value = float(book_data['estimated_value'])
                            if 'rarity_level' in book_data:
                                book.rarity_level = int(book_data['rarity_level'])
                        elif book_type == 'ancient':
                            book.origin = book_data.get('origin')
                            book.language = book_data.get('language')
                            book.translation_available = book_data.get('translation_available', False)
                        
                        if 'condition' in book_data:
                            try:
                                book.condition = BookCondition[book_data['condition'].upper()]
                            except KeyError:
                                book.condition = BookCondition.GOOD
                        
                        self._catalog.add_book(book)
                        
                        if 'section' in book_data and book_data['section']:
                            section = self._catalog.get_section_by_name(book_data['section'])
                            if not section:
                                section_id = self._catalog.add_section(book_data['section'], f"Section for {book_data['section']} books")
                            else:
                                section_id = section['id']
                            self._catalog.add_book_to_section(book.book_id, section_id)
                        
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Error importing book {book_data.get('title', 'unknown')}: {str(e)}")
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to import JSON file: {str(e)}",
                'imported_count': imported_count,
                'errors': errors
            }
        
        return {
            'success': True,
            'message': f"Successfully imported {imported_count} books from JSON",
            'imported_count': imported_count,
            'errors': errors
        }
    
    def _import_from_handwritten(self, file_path):
        
        imported_count = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as hw_file:
                lines = hw_file.readlines()
                
                current_book = {}
                for line in lines:
                    line = line.strip()
                    if not line:
                        if current_book and 'title' in current_book and 'author' in current_book:
                            try:
                                book_type = current_book.get('type', 'general').lower()
                                
                                book = BookFactory.create_book(
                                    book_type,
                                    current_book['title'],
                                    current_book['author'],
                                    int(current_book.get('year', datetime.now().year)),
                                    isbn=current_book.get('isbn'),
                                    quantity=int(current_book.get('quantity', 1))
                                )
                                
                                if book_type == 'general':
                                    book.genre = current_book.get('genre')
                                    book.is_bestseller = current_book.get('bestseller', '').lower() == 'yes'
                                elif book_type == 'rare':
                                    if 'value' in current_book:
                                        book.estimated_value = float(current_book['value'])
                                    if 'rarity' in current_book:
                                        book.rarity_level = int(current_book['rarity'])
                                elif book_type == 'ancient':
                                    book.origin = current_book.get('origin')
                                    book.language = current_book.get('language')
                                    book.translation_available = current_book.get('translation', '').lower() == 'yes'
                                
                                if 'condition' in current_book:
                                    condition_map = {
                                        'excellent': BookCondition.EXCELLENT,
                                        'good': BookCondition.GOOD,
                                        'fair': BookCondition.FAIR,
                                        'poor': BookCondition.POOR,
                                        'critical': BookCondition.CRITICAL
                                    }
                                    book.condition = condition_map.get(
                                        current_book['condition'].lower(), 
                                        BookCondition.GOOD
                                    )
                                
                                self._catalog.add_book(book)
                                
                                if 'section' in current_book and current_book['section']:
                                    section = self._catalog.get_section_by_name(current_book['section'])
                                    if not section:
                                        section_id = self._catalog.add_section(
                                            current_book['section'], 
                                            f"Section for {current_book['section']} books"
                                        )
                                    else:
                                        section_id = section['id']
                                    self._catalog.add_book_to_section(book.book_id, section_id)
                                
                                imported_count += 1
                            except Exception as e:
                                errors.append(f"Error importing book {current_book.get('title', 'unknown')}: {str(e)}")
                        
                        current_book = {}
                    elif ':' in line:
                        key, value = line.split(':', 1)
                        current_book[key.strip().lower()] = value.strip()
                
                if current_book and 'title' in current_book and 'author' in current_book:
                    try:
                        book_type = current_book.get('type', 'general').lower()
                        book = BookFactory.create_book(
                            book_type,
                            current_book['title'],
                            current_book['author'],
                            int(current_book.get('year', datetime.now().year)),
                            isbn=current_book.get('isbn'),
                            quantity=int(current_book.get('quantity', 1))
                        )
                        
                        self._catalog.add_book(book)
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Error importing book {current_book.get('title', 'unknown')}: {str(e)}")
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to import handwritten file: {str(e)}",
                'imported_count': imported_count,
                'errors': errors
            }
        
        return {
            'success': True,
            'message': f"Successfully imported {imported_count} books from handwritten records",
            'imported_count': imported_count,
            'errors': errors
        }
