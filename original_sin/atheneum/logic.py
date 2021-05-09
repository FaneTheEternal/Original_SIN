from typing import List, Tuple, Dict

from atheneum.models import Book, Page


def get_books() -> List[Tuple[str, str]]:
    return Book.objects.all().values_list('name', 'author')


def get_books_review() -> List[Dict[str, str]]:
    books = Book.objects.all()
    books = [dict(name=book.name, author=book.author, cover=book.cover_url, uid=book.uid) for book in books]
    print(books)
    return books


def get_pages(book):
    return book.pages.all()


def get_pages_urls(book) -> List[str]:
    pages: List[Page] = list(get_pages(book))
    return [page.file.url for page in pages]
