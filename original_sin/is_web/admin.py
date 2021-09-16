from django.contrib import admin

from . import models
from .forms import NewsForm, CatalogItemForm


class NewsAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, change=False, **kwargs):
        return NewsForm


class CatalogItemAdmin(admin.ModelAdmin):
    form = CatalogItemForm


admin.site.register(models.News, NewsAdmin)
admin.site.register(models.CatalogItem, CatalogItemAdmin)
