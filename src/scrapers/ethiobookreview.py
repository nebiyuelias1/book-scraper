import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Optional
from .base_scraper import BaseScraper
from ..models import Book

class EthioBookReviewScraper(BaseScraper):
    BASE_URL = "https://www.ethiobookreview.com"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

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
            
            page_title = soup.title.string.strip() if soup.title else ""
            title = page_title
            
            clean_match = re.search(r"^(.*?)(?: Amharic book by| \| Ethio Book Review)", page_title, re.IGNORECASE)
            if clean_match:
                title = clean_match.group(1).strip()
                
            description = None
            details_div = soup.find("div", class_="product-details")
            if details_div:
                paragraphs = details_div.find_all("p")
                if paragraphs:
                    longest_p = max(paragraphs, key=lambda p: len(p.get_text()))
                    if len(longest_p.get_text()) > 50:
                        description = longest_p.get_text().strip()
            
            if not description:
                meta_desc = soup.find("meta", {"name": "description"})
                if meta_desc:
                    description = meta_desc['content'].strip()

            category = []
            # Look for "Category: Fiction" or similar in the text
            details_text = soup.get_text()
            cat_match = re.search(r"Category:\s*(.+)", details_text)
            if cat_match:
                cat_name = cat_match.group(1).split('\n')[0].strip()
                if cat_name:
                    category.append(cat_name)

            return {
                "title": title,
                "description": self._clean_text(description),
                "publisher": None,
                "published_at": None,
                "isbn": None,
                "category": category
            }
        except Exception as e:
            print(f"Error getting details for {url}: {e}")
            return {}

    def scrape(self, limit: int = 100) -> List[Book]:
        books = []
        page = 1
        
        # Estimate pages based on limit (approx 24 books per page)
        max_pages = (limit // 24) + 2 
        
        while page <= max_pages and len(books) < limit:
            print(f"[EthioBookReview] Scraping page {page}...")
            url = f"{self.BASE_URL}/amharic/pages/{page}"
            
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.content, "html.parser")
                book_items = soup.find_all("div", class_="product")
                
                if not book_items:
                    break

                for item in book_items:
                    if len(books) >= limit:
                        break

                    author = item.find("h5").text.strip() if item.find("h5") else None
                    
                    img_tag = item.find("img")
                    cover_image = None
                    if img_tag and img_tag.get('src'):
                        src = img_tag['src']
                        cover_image = src if src.startswith("http") else self.BASE_URL + src
                    
                    detail_url = None
                    link_tag = item.find("a")
                    if link_tag and link_tag.get('href'):
                        href = link_tag['href']
                        detail_url = href if href.startswith("http") else self.BASE_URL + href
                    
                    print(f"[EthioBookReview] Fetching details for author: {author}...")
                    
                    details = {}
                    if detail_url:
                        details = self._get_book_details(detail_url)
                    
                    # Create Book object
                    book = Book(
                        title=details.get("title", "Unknown"),
                        author=author,
                        description=details.get("description"),
                        published_at=details.get("published_at"),
                        language="am",
                        cover_image=cover_image,
                        publisher=details.get("publisher"),
                        isbn=details.get("isbn"),
                        source="EthioBookReview",
                        url=detail_url if detail_url else url, # Fallback to page url if no detail url
                        category=details.get("category", [])
                    )
                    books.append(book)
                    time.sleep(0.5)
                
                page += 1
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
                
        return books
