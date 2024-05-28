from django.contrib import admin

from .models import Developer


class DeveloperAdmin(admin.ModelAdmin):
    pass


admin.site.register(Developer, DeveloperAdmin)
