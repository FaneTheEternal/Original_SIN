from django.contrib import admin

# Register your models here.
from .models import VkUser, QuestProfile, ChatStep, ProxyStep

admin.site.register(VkUser)
admin.site.register(QuestProfile)

admin.site.register(ChatStep)
admin.site.register(ProxyStep)
