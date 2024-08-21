from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Project, Language


class ProjectAdmin(ModelAdmin):
    pass


class LanguageAdmin(ModelAdmin):
    pass

admin.site.register(Project, ProjectAdmin)
admin.site.register(Language, LanguageAdmin)
