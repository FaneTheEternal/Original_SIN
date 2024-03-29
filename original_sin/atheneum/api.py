import logging
from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from ninja import NinjaAPI

from core.decor import SafeWrapper
from .models import SimpleUser, Book
from .schemas import BookSchema

api = NinjaAPI(urls_namespace='atheneum')

logger = logging.getLogger(__name__)


@api.post('/login')
def login(request: Union[HttpRequest, WSGIRequest]):
    uid = request.headers.get('uid', None)
    result = dict()
    if uid:
        kw = dict(uid=uid)
        user, created = SimpleUser.objects.get_or_create(kw, **kw)
    else:
        user = SimpleUser.objects.create()
        created = bool(user)
    result['status'] = 'ok'
    result['uid'] = user.uid
    result['created'] = created
    return result


@api.post('/all_books')
@SafeWrapper()
def all_books():
    """
    list of all books
    """
    books = Book.objects.all()
    serialise = [dict(name=book.name, author=book.author, cover=book.cover_url, uid=book.uid) for book in books]
    return dict(books=serialise)


@api.post('/get_pages_urls')
@SafeWrapper(BookSchema)
def get_pages(obj: BookSchema):
    """
    list of urls of pages images
    """
    assert obj.uid, 'stub'
    book = Book.objects.get(uid=obj.uid)
    pages = [dict(url=p.file.url, order=p.order, name=p.name) for p in book.pages.all()]
    return dict(pages=pages)
