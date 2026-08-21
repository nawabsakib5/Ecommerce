from django.contrib import *

from django.contrib.auth.admin import UserAdmin
from .models import *


admin.site.register(CustomUserModel, UserAdmin)

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'is_active', 'order')
    list_filter = ('banner_type', 'is_active')
    list_editable = ('is_active', 'order')