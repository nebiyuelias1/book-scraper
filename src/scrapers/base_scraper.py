from abc import ABC, abstractmethod
from typing import List
from ..models import Book

class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, limit: int = 100) -> List[Book]:
        """
        Scrapes books from the source.
        
        Args:
            limit: Maximum number of books to scrape.
            
        Returns:
            List[Book]: A list of scraped Book objects.
        """
        pass
