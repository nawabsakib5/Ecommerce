from django.contrib import admin
from .models import Category, Item, ItemImage


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 3
    fields = ('image', 'order')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user', 'original_price', 'status', 'condition', 'stock_count', 'created_at')
    list_filter = ('status', 'condition', 'category')
    search_fields = ('name', 'description', 'user__username')
    inlines = [ItemImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('item', 'order')