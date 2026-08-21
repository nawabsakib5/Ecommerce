from django.contrib import admin
from .models import *
from .models import Category, Item, ItemImage, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3
    fields = ('size', 'color', 'color_code', 'additional_price', 'stock', 'is_active')


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 3
    fields = ('image', 'order')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user', 'original_price', 'status', 'condition', 'stock_count', 'created_at')
    list_filter = ('status', 'condition', 'category')
    search_fields = ('name', 'description', 'user__username')
    inlines = [ItemImageInline, ProductVariantInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'icon', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('item', 'order')