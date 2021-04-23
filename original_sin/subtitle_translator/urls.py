from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('api/', views.api.urls),
    url(r'^download$', views.download_view),
]
