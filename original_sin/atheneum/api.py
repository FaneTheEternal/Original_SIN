import functools
import logging
from typing import Callable, Dict, Union, Type

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from ninja import NinjaAPI, Schema

from core.decor import SafeWrapper
from .logic import get_pages_urls, get_books, get_books_review
from .models import SimpleUser, Book
from .schemas import TryLoginSchema, LoginSchema, BookSchema

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
    return dict(books=get_books_review())


@api.post('/get_pages_urls')
@SafeWrapper(BookSchema)
def get_pages(obj: BookSchema):
    """
    list of urls of pages images
    """
    assert obj.uid, 'stub'
    book = Book.objects.get(uid=obj.uid)
    pages = [dict(url=p.file.url, order=p.order) for p in book.pages.all()]
    return dict(pages=pages)
