import requests
from bs4 import BeautifulSoup
import time
import re
import json
from datetime import datetime
from typing import List, Optional, Dict
from .base_scraper import BaseScraper
from ..models import Book

class GoodreadsScraper(BaseScraper):
    BASE_URL = "https://www.goodreads.com"
    LIST_URL = "https://www.goodreads.com/list/show/89548.Best_Amharic_Books"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        if not date_str:
            return None
        
        formats = [
            "%B %d, %Y", # January 1, 1968
            "%b %d, %Y", # Jan 1, 1968
            "%Y",        # 1968
            "%B %Y",     # January 1968
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
        match = re.search(r"(\w+ \d+, \d{4})", date_str)
        if match:
            try:
                dt = datetime.strptime(match.group(1), "%B %d, %Y")
                return dt.strftime("%Y-%m-%d")
            except:
                pass
        return date_str

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return re.sub(r'\s+', ' ', text).strip()

    def _get_book_details(self, url: str) -> Dict:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return {}
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # JSON-LD
            script = soup.find("script", type="application/ld+json")
            json_data = {}
            if script:
                try:
                    json_data = json.loads(script.string)
                except:
                    pass

            title = json_data.get("name") or (soup.find("h1", {"data-testid": "bookTitle"}).text.strip() if soup.find("h1", {"data-testid": "bookTitle"}) else None)
            
            author = None
            if "author" in json_data:
                if isinstance(json_data["author"], list):
                    author = json_data["author"][0].get("name")
                else:
                    author = json_data["author"].get("name")
            if not author:
                author_tag = soup.find("span", {"data-testid": "name"})
                author = author_tag.text.strip() if author_tag else None

            description = json_data.get("description") or (soup.find("div", {"data-testid": "description"}).text.strip() if soup.find("div", {"data-testid": "description"}) else None)
            
            isbn = json_data.get("isbn")
            if not isbn:
                isbn_match = re.search(r'"isbn":"(\d+)"', response.text)
                if isbn_match:
                    isbn = isbn_match.group(1)
            
            publisher = json_data.get("publisher", {}).get("name") if isinstance(json_data.get("publisher"), dict) else None
            
            published_at_str = json_data.get("datePublished")
            if not published_at_str:
                details = soup.find("div", {"class": "FeaturedDetails"})
                if details:
                    text = details.get_text()
                    pub_match = re.search(r"(?:First published|Published) (.+)", text)
                    if pub_match:
                        published_at_str = pub_match.group(1).strip()
            
            cover_image = json_data.get("image") or (soup.find("img", {"class": "ResponsiveImage"})['src'] if soup.find("img", {"class": "ResponsiveImage"}) else None)
            
            # Genres/Categories
            genres = []
            genre_tags = soup.find_all("span", {"class": "BookPageMetadataSection__genreButton"})
            if not genre_tags:
                # Try newer/alternative selector
                genre_section = soup.find("div", {"data-testid": "genresList"})
                if genre_section:
                    genre_tags = genre_section.find_all("a")
            
            for tag in genre_tags:
                genre_text = tag.text.strip()
                if genre_text and genre_text not in ["...more", "Genres"]:
                    genres.append(genre_text)

            language = json_data.get("inLanguage") or "am"
            if language == "Amharic":
                language = "am"
            elif not language:
                language = "am"

            return {
                "title": title,
                "author": author,
                "description": self._clean_text(description),
                "published_at": self._parse_date(published_at_str),
                "language": language,
                "cover_image": cover_image,
                "publisher": publisher,
                "isbn": isbn,
                "category": genres
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {}

    def scrape(self, limit: int = 100) -> List[Book]:
        books = []
        page = 1
        
        while len(books) < limit:
            print(f"[Goodreads] Scraping page {page}...")
            response = requests.get(f"{self.LIST_URL}?page={page}", headers=self.headers)
            
            if response.status_code != 200:
                break
                
            soup = BeautifulSoup(response.content, "html.parser")
            book_rows = soup.find_all("tr", itemtype="http://schema.org/Book")
            
            if not book_rows:
                break
                
            for row in book_rows:
                if len(books) >= limit:
                    break
                    
                title_tag = row.find("a", class_="bookTitle")
                book_url = self.BASE_URL + title_tag['href']
                
                print(f"[Goodreads] Fetching details for: {title_tag.text.strip()}")
                details = self._get_book_details(book_url)
                
                if details and details.get("title"):
                    book = Book(
                        title=details.get("title"),
                        author=details.get("author"),
                        description=details.get("description"),
                        published_at=details.get("published_at"),
                        language=details.get("language"),
                        cover_image=details.get("cover_image"),
                        publisher=details.get("publisher"),
                        isbn=details.get("isbn"),
                        source="Goodreads",
                        url=book_url,
                        category=details.get("category", [])
                    )
                    books.append(book)
                
                time.sleep(1) # Be respectful
            
            page += 1
            if page > 10: break
            
        return books
