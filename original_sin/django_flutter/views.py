import logging
from pathlib import Path
from typing import Union

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpRequest, FileResponse
from django.template.response import SimpleTemplateResponse

from django_flutter.utility import get_flutter_apps

logger = logging.getLogger(__name__)


def flutter_view(request: Union[HttpRequest, WSGIRequest], path: str = None, *args, **kwargs):
    index = 'index.html'
    try:
        path = path.split('/')
        app_name = path.pop(0)
        path = '/'.join(path)
        if app_name not in get_flutter_apps():
            raise RuntimeError(f'{app_name} not in allowed apps')
        if not path or path == index:
            template = f'{app_name}/{index}'
            base_path = f'{request.scheme}://{request.META["HTTP_HOST"]}/flutter/{app_name}/'
            context = dict(base_path=base_path)
            return SimpleTemplateResponse(template, context=context)
        file = Path(settings.BASE_DIR, app_name, 'flutter', path)
        content_type = 'application/javascript' if path.endswith('.js') else None
        return FileResponse(open(file, 'rb'), content_type=content_type)
    except Exception as e:
        logger.error(e)
        # raise  # Professional debug instrument
        return HttpResponse(str(e))
