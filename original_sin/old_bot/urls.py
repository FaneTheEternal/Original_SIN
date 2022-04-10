from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^$',
        views.index,
    ),
    url(
        r'^fill$',
        views.fill,
        name='fill'
    ),
    url(
        r'raw',
        views.raw,
        name='raw',
    ),
    url(r'^extract$', views.extract)
]
