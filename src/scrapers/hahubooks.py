import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Optional
from urllib.parse import urljoin
from .base_scraper import BaseScraper
from ..models import Book

class HahuBooksScraper(BaseScraper):
    BASE_URL = "https://www.hahubooks.com"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return re.sub(r'\s+', ' ', text).strip()

    def scrape(self, limit: int = 100) -> List[Book]:
        books = []
        page = 1
        
        while len(books) < limit:
            print(f"[HahuBooks] Scraping page {page}...")
            url = f"{self.BASE_URL}/shop-grid.php?pn={page}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=120)
                if response.status_code != 200:
                    print(f"[HahuBooks] Failed to fetch page {page}: {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.content, "html.parser")
                product_items = soup.find_all("div", class_="product")
                
                if not product_items:
                    print(f"[HahuBooks] No products found on page {page}. Stopping.")
                    break

                for item in product_items:
                    if len(books) >= limit:
                        break

                    # Title and URL
                    content_div = item.find("div", class_="product__content")
                    if not content_div:
                        continue
                        
                    title_tag = content_div.find("h6").find("a")
                    if not title_tag:
                        continue

                    title = self._clean_text(title_tag.text)
                    relative_url = title_tag.get("href")
                    book_url = urljoin(self.BASE_URL, relative_url) if relative_url else None
                    
                    # Author
                    # Structure: <small> በ ደመወዝ  ጎሽሜ</small>
                    author_tag = content_div.find("small")
                    author = self._clean_text(author_tag.text) if author_tag else None
                    if author and "በ" in author:
                        # Split by "በ" and take the last part, just in case
                        parts = author.split("በ")
                        if len(parts) > 1:
                             author = parts[-1].strip()
                        
                    # Image
                    # Structure: <div class="product__thumb"> <a ...><img src="..."></a>
                    thumb_div = item.find("div", class_="product__thumb")
                    cover_image = None
                    if thumb_div:
                        img_tag = thumb_div.find("img")
                        if img_tag and img_tag.get("src"):
                            cover_image = urljoin(self.BASE_URL, img_tag.get("src"))

                    # Category
                    # <div class="hot__box color--2"><span class="hot-label">History</span></div>
                    categories = []
                    hot_box = thumb_div.find("div", class_="hot__box") if thumb_div else None
                    if hot_box:
                        label = hot_box.find("span", class_="hot-label")
                        if label:
                            categories.append(self._clean_text(label.text))

                    book = Book(
                        title=title,
                        author=author,
                        description=None,
                        published_at=None,
                        language="am",
                        cover_image=cover_image,
                        publisher=None,
                        isbn=None,
                        source="HahuBooks",
                        url=book_url,
                        category=categories
                    )
                    books.append(book)
                
                page += 1
                time.sleep(0.5)

            except Exception as e:
                print(f"[HahuBooks] Exception on page {page}: {e}")
                break
                
        return books
