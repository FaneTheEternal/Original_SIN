from django.urls import path

from hr_analytics.api import api

urlpatterns = [
    path("api/", api.urls),
]
