import requests
import time
import urllib.parse
from typing import Optional, Dict
from .models import Book

class GoogleBooksEnricher:
    API_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def _search(self, query: str) -> Optional[Dict]:
        params = {"q": query, "maxResults": 1, "printType": "books"}
        if self.api_key:
            params["key"] = self.api_key

        max_retries = 3
        retry_delay = 2 # seconds

        for attempt in range(max_retries):
            try:
                response = requests.get(self.API_URL, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data and len(data["items"]) > 0:
                        return data["items"][0]["volumeInfo"]
                    return None
                
                elif response.status_code == 429:
                    # Rate limit hit
                    print(f"[Enricher] Rate limit hit. Waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                    continue
                
                else:
                    # Other error
                    # print(f"[Enricher] API Error {response.status_code} for '{query}'")
                    return None

            except Exception as e:
                print(f"[Enricher] Exception for query '{query}': {e}")
                return None
            
            # Polite delay between requests
            time.sleep(1)
        
        return None

    def enrich(self, book: Book) -> Book:
        # Don't enrich if we already have ISBN, Page Count, and Description
        if book.isbn and book.page_count and book.description:
            return book

        info = None
        
        # 1. Search by ISBN if available
        if book.isbn:
            info = self._search(f"isbn:{book.isbn}")
        
        # 2. Search by English Title if available
        if not info and book.title_en:
            info = self._search(f"intitle:{book.title_en}")

        # 3. Search by Romanized Title + Author
        if not info and book.title_romanized and book.author_romanized:
             info = self._search(f"{book.title_romanized} {book.author_romanized}")

        # 4. Search by Original Title + Author
        if not info and book.title:
            # Clean title of extra parens usually found in these scrapers
            clean_title = book.title.split("(")[0].strip()
            # Try specific fields first
            info = self._search(f"intitle:{clean_title}")
            # Fallback to general keyword search which is more forgiving
            if not info:
                query = clean_title
                if book.author:
                    query += f" {book.author}"
                info = self._search(query)

        if info:
            print(f"[Enricher] Found match for: {book.title}")
            
            # Fill missing ISBN
            if not book.isbn and "industryIdentifiers" in info:
                for ident in info["industryIdentifiers"]:
                    if ident["type"] == "ISBN_13":
                        book.isbn = ident["identifier"]
                        break
                    if ident["type"] == "ISBN_10" and not book.isbn:
                        book.isbn = ident["identifier"]

            # Fill missing Page Count
            if not book.page_count and "pageCount" in info:
                book.page_count = info["pageCount"]

            # Fill missing Publisher
            if not book.publisher and "publisher" in info:
                book.publisher = info["publisher"]

            # Fill missing Published Date
            if not book.published_at and "publishedDate" in info:
                book.published_at = info["publishedDate"]

            # Fill missing Description
            if not book.description and "description" in info:
                book.description = info["description"]
            
            # Fill missing Categories
            if not book.category and "categories" in info:
                book.category = info["categories"]
                
            # Fill missing Cover Image (Only if we really don't have one)
            if not book.cover_image and "imageLinks" in info:
                if "thumbnail" in info["imageLinks"]:
                    book.cover_image = info["imageLinks"]["thumbnail"]

        else:
            print(f"[Enricher] No match found for: {book.title}")

        return book
