import requests
import json
import time
import re
from typing import List, Optional
from .base_scraper import BaseScraper
from ..models import Book

class MerebScraper(BaseScraper):
    APP_ID = "H5Z9SUEF7F"
    API_KEY = "c68b889d9f9672238b54929dfb035bc2"
    INDEX_NAME = "products"
    API_URL = f"https://{APP_ID}-dsn.algolia.net/1/indexes/*/queries"

    def __init__(self):
        self.headers = {
            "x-algolia-application-id": self.APP_ID,
            "x-algolia-api-key": self.API_KEY,
            "Content-Type": "application/json",
            "Referer": "https://www.mereb.shop/"
        }

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return re.sub(r'\s+', ' ', text).strip()

    def scrape(self, limit: int = 100) -> List[Book]:
        books = []
        page = 1
        hits_per_page = 50
        
        while len(books) < limit:
            print(f"[Mereb] Fetching page {page} from Algolia API...")
            
            # Construct params
            # We filter for categoryI=Books to ensure we only get books

            
            payload = {
                "requests": [
                    {
                        "indexName": self.INDEX_NAME,
                        "params": params
                    }
                ]
            }
            
            try:
                response = requests.post(self.API_URL, headers=self.headers, json=payload, timeout=15)
                if response.status_code != 200:
                    print(f"Mereb API Error: {response.text}")
                    break
                
                data = response.json()
                results = data.get("results", [])
                if not results:
                    break
                
                hits = results[0].get("hits", [])
                if not hits:
                    print(f"[Mereb] No more hits found at page {page}.")
                    break
                
                print(f"[Mereb] Found {len(hits)} hits on page {page}.")
                
                for hit in hits:
                    if len(books) >= limit:
                        break
                    
                    # Strict category check
                    if hit.get("categoryI") != "Books":
                        continue
                    
                    title_en = hit.get("title")
                    title_am = hit.get("titleAM")
                    
                    # Primary title is Amharic, secondary is English
                    title = title_am if title_am else title_en

                    book = Book(
                        title=title or "Unknown Title",
                        title_en=title_en,
                        author=hit.get("author"),
                        description=self._clean_text(hit.get("description")),
                        published_at=None, # Not directly in Algolia hit
                        language="am",
                        cover_image=hit.get("image"),
                        publisher=None, # Not directly in Algolia hit
                        isbn=None, # Not directly in Algolia hit
                        source="Mereb",
                        url=hit.get("url")
                    )
                    books.append(book)
                
                # Check if we've reached the last page
                nb_pages = results[0].get("nbPages", 0)
                if page >= nb_pages:
                    break
                    
                page += 1
                # Small delay to be nice, though it's an API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Mereb Scraper Exception: {e}")
                break
                
        return books
