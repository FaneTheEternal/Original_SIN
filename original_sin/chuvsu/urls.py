from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^$',
        views.index,
    ),
    url(
        r'^chuvsuguide_bot$',
        views.chuvsuguide_bot.index,
    )
]
