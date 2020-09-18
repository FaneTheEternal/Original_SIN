from django.contrib import admin

# Register your models here.
from .models import Schedule, Subject, Teacher, Discipline, LectureHall, Institute

admin.site.register(Schedule)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Discipline)
admin.site.register(LectureHall)
admin.site.register(Institute)
