from django.conf.urls import url
from django.urls import path

from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(
        r'^$',
        RedirectView.as_view(pattern_name='news', permanent=True),
    ),
    url(
        r'^news$',
        views.NewsView.as_view(),
        name='news',
    ),
    url(
        r'^catalog$',
        views.CatalogView.as_view(),
        name='catalog',
    ),
    url(
        r'^contacts$',
        views.ContactsView.as_view(),
        name='contacts',
    ),
    url(
        r'^info$',
        views.InfoView.as_view(),
        name='info',
    ),
    path('api/', views.api.urls),
]
