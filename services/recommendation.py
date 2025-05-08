"""
Recommendation Service implementation for the Enchanted Library system.
This module provides book recommendations based on user reading history and interests.
"""
from collections import Counter


class RecommendationService:
    """Service for generating book recommendations for users."""
    
    def __init__(self, catalog):
        """
        Initialize the recommendation service with a catalog.
        
        Args:
            catalog: The library catalog
        """
        self._catalog = catalog
        self._user_preferences = {}  # User ID -> preferences
    
    def update_user_preferences(self, user_id, preferences):
        """
        Update a user's preferences for recommendations.
        
        Args:
            user_id (str): ID of the user
            preferences (dict): User preferences (genres, authors, topics, etc.)
        """
        if user_id not in self._user_preferences:
            self._user_preferences[user_id] = preferences
        else:
            self._user_preferences[user_id].update(preferences)
    
    def analyze_reading_history(self, user_id):
        """
        Analyze a user's reading history to extract preferences.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            dict: Extracted preferences
        """
        user = self._catalog.get_user(user_id)
        
        if not user:
            return {}
        
        # Get the user's reading history
        reading_history = user.reading_history
        
        if not reading_history:
            return {}
        
        # Extract book information from reading history
        genres = []
        authors = []
        years = []
        
        for record in reading_history:
            book_id = record.get('book_id')
            if book_id:
                book = self._catalog.get_book(book_id)
                if book:
                    # Extract genre if available
                    if hasattr(book, 'genre') and book.genre:
                        genres.append(book.genre)
                    
                    # Extract author
                    authors.append(book.author)
                    
                    # Extract year
                    years.append(book.year_published)
        
        # Count occurrences to find preferences
        genre_counts = Counter(genres)
        author_counts = Counter(authors)
        year_counts = Counter(years)
        
        # Extract top preferences
        preferences = {
            'favorite_genres': [genre for genre, count in genre_counts.most_common(3)],
            'favorite_authors': [author for author, count in author_counts.most_common(3)],
            'preferred_eras': self._extract_preferred_eras(year_counts)
        }
        
        # Update the user's preferences
        self.update_user_preferences(user_id, preferences)
        
        return preferences
    
    def _extract_preferred_eras(self, year_counts):
        """
        Extract preferred eras from year counts.
        
        Args:
            year_counts (Counter): Counter of publication years
            
        Returns:
            list: Preferred eras
        """
        # Group years into eras
        eras = {
            'Ancient': 0,        # Before 1500
            'Renaissance': 0,    # 1500-1700
            'Enlightenment': 0,  # 1700-1800
            'Victorian': 0,      # 1800-1900
            'Modern': 0,         # 1900-2000
            'Contemporary': 0    # 2000-present
        }
        
        for year, count in year_counts.items():
            if year < 1500:
                eras['Ancient'] += count
            elif year < 1700:
                eras['Renaissance'] += count
            elif year < 1800:
                eras['Enlightenment'] += count
            elif year < 1900:
                eras['Victorian'] += count
            elif year < 2000:
                eras['Modern'] += count
            else:
                eras['Contemporary'] += count
        
        # Sort eras by count
        sorted_eras = sorted(eras.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 2 eras
        return [era for era, count in sorted_eras[:2] if count > 0]
    
    def get_recommendations(self, user_id, max_results=10):
        """
        Get book recommendations for a user.
        
        Args:
            user_id (str): ID of the user
            max_results (int): Maximum number of recommendations to return
            
        Returns:
            list: Recommended books
        """
        # Get user preferences
        preferences = self._user_preferences.get(user_id, {})
        
        # If no preferences, analyze reading history
        if not preferences:
            preferences = self.analyze_reading_history(user_id)
        
        # If still no preferences, return popular books
        if not preferences:
            return self.get_popular_books(max_results)
        
        # Get all books from the catalog
        all_books = list(self._catalog._books.values())
        
        # Score each book based on user preferences
        scored_books = []
        
        for book in all_books:
            score = 0
            
            # Check if the user has already read this book
            user = self._catalog.get_user(user_id)
            if user:
                book_ids = [record.get('book_id') for record in user.reading_history]
                if book.book_id in book_ids:
                    continue  # Skip books the user has already read
            
            # Score based on genre
            if hasattr(book, 'genre') and book.genre:
                if book.genre in preferences.get('favorite_genres', []):
                    score += 3
            
            # Score based on author
            if book.author in preferences.get('favorite_authors', []):
                score += 4
            
            # Score based on era
            era = self._get_era(book.year_published)
            if era in preferences.get('preferred_eras', []):
                score += 2
            
            # Score based on book type
            from models.book import GeneralBook, RareBook, AncientScript
            
            if isinstance(book, GeneralBook):
                score += 1  # General books are more accessible
            elif isinstance(book, RareBook):
                # Check if the user is a scholar or librarian
                user = self._catalog.get_user(user_id)
                if user and user.get_role().name in ['SCHOLAR', 'LIBRARIAN']:
                    score += 2  # Scholars and librarians might prefer rare books
            
            # Add the book with its score
            scored_books.append((book, score))
        
        # Sort books by score (highest first)
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top recommendations
        return [book for book, score in scored_books[:max_results]]
    
    def _get_era(self, year):
        """
        Get the era for a year.
        
        Args:
            year (int): Publication year
            
        Returns:
            str: Era name
        """
        if year < 1500:
            return 'Ancient'
        elif year < 1700:
            return 'Renaissance'
        elif year < 1800:
            return 'Enlightenment'
        elif year < 1900:
            return 'Victorian'
        elif year < 2000:
            return 'Modern'
        else:
            return 'Contemporary'
    
    def get_popular_books(self, max_results=10):
        """
        Get popular books based on borrowing history.
        
        Args:
            max_results (int): Maximum number of books to return
            
        Returns:
            list: Popular books
        """
        # Count the number of times each book has been borrowed
        book_borrow_counts = {}
        
        for record in self._catalog._lending_records.values():
            book_id = record.book_id
            if book_id in book_borrow_counts:
                book_borrow_counts[book_id] += 1
            else:
                book_borrow_counts[book_id] = 1
        
        # Sort books by borrow count
        sorted_books = sorted(book_borrow_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Get the top books
        popular_books = []
        for book_id, count in sorted_books[:max_results]:
            book = self._catalog.get_book(book_id)
            if book:
                popular_books.append(book)
        
        return popular_books
    
    def get_similar_books(self, book_id, max_results=5):
        """
        Get books similar to a given book.
        
        Args:
            book_id (str): ID of the reference book
            max_results (int): Maximum number of similar books to return
            
        Returns:
            list: Similar books
        """
        reference_book = self._catalog.get_book(book_id)
        
        if not reference_book:
            return []
        
        # Get all books from the catalog
        all_books = list(self._catalog._books.values())
        
        # Score each book based on similarity to the reference book
        scored_books = []
        
        for book in all_books:
            # Skip the reference book itself
            if book.book_id == book_id:
                continue
            
            score = 0
            
            # Same author
            if book.author == reference_book.author:
                score += 5
            
            # Same genre
            if hasattr(book, 'genre') and hasattr(reference_book, 'genre'):
                if book.genre == reference_book.genre:
                    score += 4
            
            # Similar publication year (within 20 years)
            if abs(book.year_published - reference_book.year_published) <= 20:
                score += 3
            
            # Same book type
            if type(book) == type(reference_book):
                score += 2
            
            # Add the book with its score
            scored_books.append((book, score))
        
        # Sort books by score (highest first)
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top similar books
        return [book for book, score in scored_books[:max_results]]
    
    def get_recommendations_by_topic(self, topic, max_results=10):
        """
        Get book recommendations for a specific topic.
        
        Args:
            topic (str): The topic to find books for
            max_results (int): Maximum number of books to return
            
        Returns:
            list: Books related to the topic
        """
        # Get all books from the catalog
        all_books = list(self._catalog._books.values())
        
        # Score each book based on relevance to the topic
        scored_books = []
        
        for book in all_books:
            score = 0
            
            # Check if the topic appears in the title
            if topic.lower() in book.title.lower():
                score += 5
            
            # Check if the book has a genre matching the topic
            if hasattr(book, 'genre') and book.genre and topic.lower() in book.genre.lower():
                score += 4
            
            # For scholars, check if the topic is in their research topics
            if hasattr(book, '_research_topics'):
                for research_topic in book._research_topics:
                    if topic.lower() in research_topic.lower():
                        score += 3
            
            # Add the book with its score if it's relevant
            if score > 0:
                scored_books.append((book, score))
        
        # Sort books by score (highest first)
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top recommendations
        return [book for book, score in scored_books[:max_results]]
