
from collections import Counter

class RecommendationService:
    
    
    def __init__(self, catalog):
        
        self._catalog = catalog
        self._user_preferences = {}
    
    def update_user_preferences(self, user_id, preferences):
        
        if user_id not in self._user_preferences:
            self._user_preferences[user_id] = preferences
        else:
            self._user_preferences[user_id].update(preferences)
    
    def analyze_reading_history(self, user_id):
        
        user = self._catalog.get_user(user_id)
        
        if not user:
            return {}
        
        reading_history = user.reading_history
        
        if not reading_history:
            return {}
        
        genres = []
        authors = []
        years = []
        
        for record in reading_history:
            book_id = record.get('book_id')
            if book_id:
                book = self._catalog.get_book(book_id)
                if book:
                    if hasattr(book, 'genre') and book.genre:
                        genres.append(book.genre)
                    
                    authors.append(book.author)
                    
                    years.append(book.year_published)
        
        genre_counts = Counter(genres)
        author_counts = Counter(authors)
        year_counts = Counter(years)
        
        preferences = {
            'favorite_genres': [genre for genre, count in genre_counts.most_common(3)],
            'favorite_authors': [author for author, count in author_counts.most_common(3)],
            'preferred_eras': self._extract_preferred_eras(year_counts)
        }
        
        self.update_user_preferences(user_id, preferences)
        
        return preferences
    
    def _extract_preferred_eras(self, year_counts):
        
        eras = {
            'Ancient': 0,
            'Renaissance': 0,
            'Enlightenment': 0,
            'Victorian': 0,
            'Modern': 0,
            'Contemporary': 0
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
        
        sorted_eras = sorted(eras.items(), key=lambda x: x[1], reverse=True)
        
        return [era for era, count in sorted_eras[:2] if count > 0]
    
    def get_recommendations(self, user_id, max_results=10):
        
        preferences = self._user_preferences.get(user_id, {})
        
        if not preferences:
            preferences = self.analyze_reading_history(user_id)
        
        if not preferences:
            return self.get_popular_books(max_results)
        
        all_books = list(self._catalog._books.values())
        
        scored_books = []
        
        for book in all_books:
            score = 0
            
            user = self._catalog.get_user(user_id)
            if user:
                book_ids = [record.get('book_id') for record in user.reading_history]
                if book.book_id in book_ids:
                    continue
            
            if hasattr(book, 'genre') and book.genre:
                if book.genre in preferences.get('favorite_genres', []):
                    score += 3
            
            if book.author in preferences.get('favorite_authors', []):
                score += 4
            
            era = self._get_era(book.year_published)
            if era in preferences.get('preferred_eras', []):
                score += 2
            
            from models.book import GeneralBook, RareBook, AncientScript
            
            if isinstance(book, GeneralBook):
                score += 1
            elif isinstance(book, RareBook):
                user = self._catalog.get_user(user_id)
                if user and user.get_role().name in ['SCHOLAR', 'LIBRARIAN']:
                    score += 2
            
            scored_books.append((book, score))
        
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        return [book for book, score in scored_books[:max_results]]
    
    def _get_era(self, year):
        
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
        
        book_borrow_counts = {}
        
        for record in self._catalog._lending_records.values():
            book_id = record.book_id
            if book_id in book_borrow_counts:
                book_borrow_counts[book_id] += 1
            else:
                book_borrow_counts[book_id] = 1
        
        sorted_books = sorted(book_borrow_counts.items(), key=lambda x: x[1], reverse=True)
        
        popular_books = []
        for book_id, count in sorted_books[:max_results]:
            book = self._catalog.get_book(book_id)
            if book:
                popular_books.append(book)
        
        return popular_books
    
    def get_similar_books(self, book_id, max_results=5):
        
        reference_book = self._catalog.get_book(book_id)
        
        if not reference_book:
            return []
        
        all_books = list(self._catalog._books.values())
        
        scored_books = []
        
        for book in all_books:
            if book.book_id == book_id:
                continue
            
            score = 0
            
            if book.author == reference_book.author:
                score += 5
            
            if hasattr(book, 'genre') and hasattr(reference_book, 'genre'):
                if book.genre == reference_book.genre:
                    score += 4
            
            if abs(book.year_published - reference_book.year_published) <= 20:
                score += 3
            
            if type(book) == type(reference_book):
                score += 2
            
            scored_books.append((book, score))
        
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        return [book for book, score in scored_books[:max_results]]
    
    def get_recommendations_by_topic(self, topic, max_results=10):
        
        all_books = list(self._catalog._books.values())
        
        scored_books = []
        
        for book in all_books:
            score = 0
            
            if topic.lower() in book.title.lower():
                score += 5
            
            if hasattr(book, 'genre') and book.genre and topic.lower() in book.genre.lower():
                score += 4
            
            if hasattr(book, '_research_topics'):
                for research_topic in book._research_topics:
                    if topic.lower() in research_topic.lower():
                        score += 3
            
            if score > 0:
                scored_books.append((book, score))
        
        scored_books.sort(key=lambda x: x[1], reverse=True)
        
        return [book for book, score in scored_books[:max_results]]
