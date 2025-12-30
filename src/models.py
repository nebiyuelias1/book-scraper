from dataclasses import dataclass
from typing import Optional

@dataclass
class Book:
    title: str
    title_en: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    published_at: Optional[str] = None # Keeping as string 'YYYY-MM-DD' for CSV simplicity
    language: str = "am"
    cover_image: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self):
        return {
            "title": self.title,
            "title_en": self.title_en,
            "author": self.author,
            "description": self.description,
            "published_at": self.published_at,
            "language": self.language,
            "cover_image": self.cover_image,
            "publisher": self.publisher,
            "isbn": self.isbn,
            "source": self.source,
            "url": self.url,
        }
