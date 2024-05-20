from django.contrib import admin

from .models import SyncInfo


class SyncInfoAdmin(admin.ModelAdmin):
    pass


admin.site.register(SyncInfo, SyncInfoAdmin)
