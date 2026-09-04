from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import CustomUserModel, Banner, Notification, Wishlist, Shop


@admin.register(CustomUserModel)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_frozen', 'is_spam', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_frozen', 'is_spam', 'is_active')
    list_editable = ('is_frozen', 'is_spam', 'is_active')
    search_fields = ('username', 'email', 'full_name', 'phone')
    actions = ['freeze_users', 'unfreeze_users', 'mark_spam', 'unmark_spam', 'delete_selected_users']

    fieldsets = UserAdmin.fieldsets + (
        ('CADO Info', {'fields': ('full_name', 'phone', 'user_type', 'is_frozen', 'is_spam')}),
    )

    def freeze_users(self, request, queryset):
        queryset.update(is_frozen=True, is_active=False)
        self.message_user(request, f"{queryset.count()} user(s) frozen.", messages.SUCCESS)
    freeze_users.short_description = "🔒 Freeze selected users"

    def unfreeze_users(self, request, queryset):
        queryset.update(is_frozen=False, is_active=True)
        self.message_user(request, f"{queryset.count()} user(s) unfrozen.", messages.SUCCESS)
    unfreeze_users.short_description = "🔓 Unfreeze selected users"

    def mark_spam(self, request, queryset):
        queryset.update(is_spam=True, is_active=False, is_frozen=True)
        self.message_user(request, f"{queryset.count()} user(s) marked as spam.", messages.WARNING)
    mark_spam.short_description = "🚫 Mark as spam & freeze"

    def unmark_spam(self, request, queryset):
        queryset.update(is_spam=False, is_active=True, is_frozen=False)
        self.message_user(request, f"{queryset.count()} user(s) unmarked from spam.", messages.SUCCESS)
    unmark_spam.short_description = "✅ Remove spam mark"

    def delete_selected_users(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} user(s) permanently deleted.", messages.SUCCESS)
    delete_selected_users.short_description = "🗑️ Permanently delete selected users"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'is_active', 'order')
    list_filter = ('banner_type', 'is_active')
    list_editable = ('is_active', 'order')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'title')