import functools
import logging
from typing import Type, Callable, Dict, Union

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model
from django.http import HttpRequest
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SafeWrapper:
    schema = None

    def __init__(self, _schema: Type[BaseModel] = None):
        self.schema = _schema

    def __call__(self, func: Callable[[object], Dict[str, str]]):
        if self.schema:
            decorated = self._schema(func)
        else:
            decorated = self._default(func)
        # decorated.__name__ = func.__name__
        return functools.wraps(func)(decorated)

    @staticmethod
    def safe_wrapper(func, *args, **kwargs):
        result = dict()
        try:
            result['status'] = 'ok'
            result.update(func(*args, **kwargs))
        except Exception as e:
            logger.error(e, exc_info=True)
            result['status'] = 'error'
            if settings.DEBUG:
                import traceback
                result['stacktrace'] = traceback.format_exc()
        return result

    def _schema(self, func: Callable[[object], Dict[str, str]]):
        _type = self.schema

        def decorated(request: Union[HttpRequest, WSGIRequest], obj: _type):
            def _f():
                return func(obj)
            return self.safe_wrapper(_f)
        return decorated

    def _default(self, func: Callable[[], Dict[str, str]]):
        def decorated(request: Union[HttpRequest, WSGIRequest]):
            return self.safe_wrapper(func)
        return decorated


class LoginWrapper(SafeWrapper):
    def __init__(self, user_model, *args, **kwargs):
        super(LoginWrapper, self).__init__(*args, **kwargs)
        self.user_model = user_model

    def _get_user(self, uid):
        return self.user_model.objects.get(uid=uid)

    def _schema(self, func: Callable[[Model, object], Dict[str, str]]):
        _type = self.schema

        def decorated(request: Union[HttpRequest, WSGIRequest], obj: _type):
            def _f():
                user = self._get_user(request.headers.get('uid'))
                return func(user, obj)
            return self.safe_wrapper(_f)
        return decorated

    def _default(self, func: Callable[[Model], Dict[str, str]]):
        def decorated(request: Union[HttpRequest, WSGIRequest]):
            def _f():
                user = self._get_user(request.headers.get('uid'))
                return func(user)
            return self.safe_wrapper(_f)
        return decorated
