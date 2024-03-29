"""original_sin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('old_bot/', include('old_bot.urls')),

    path('flutter/', include('django_flutter.urls')),

    path('subtitle_translator/', include('subtitle_translator.urls')),

    path('atheneum/', include('atheneum.urls')),

    path('chuvsu/', include('chuvsu.urls')),

    path('is_web/', include('is_web.urls')),

    path('hr_analytics/', include('hr_analytics.urls')),
]

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns += [
    re_path(r'^favicon\.ico$', favicon_view)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
