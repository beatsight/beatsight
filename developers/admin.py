from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Developer


class DeveloperAdmin(ModelAdmin):
    pass


admin.site.register(Developer, DeveloperAdmin)
