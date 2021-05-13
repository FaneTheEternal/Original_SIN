from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from . import models

admin.site.register(models.Book)
# admin.site.register(models.Page)


class PageAdmin(OrderedModelAdmin):
    list_display = ('book', 'name', 'file', 'move_up_down_links')


admin.site.register(models.Page, PageAdmin)
