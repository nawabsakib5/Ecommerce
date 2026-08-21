from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator




class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    banner = models.ImageField(upload_to='category_banners/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('order', 'name')

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def get_children(self):
        return self.children.all()


class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
        ('expired', 'Expired'),
    ]

    # existing fields
    category = models.ForeignKey(
        Category,
        related_name='items',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='items',
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        'core.Shop',
        related_name='items',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='item_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # নতুন fields
    original_price = models.FloatField()
    sale_price = models.FloatField(blank=True, null=True)
    sale_start = models.DateTimeField(blank=True, null=True)
    sale_end = models.DateTimeField(blank=True, null=True)

    stock_count = models.PositiveIntegerField(default=1)
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='used'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )

    # পুরানো is_sold এর জায়গায় status ব্যবহার করবো
    # কিন্তু backward compatibility এর জন্য রাখছি
    is_sold = models.BooleanField(default=False, db_index=True)

    @property
    def price(self):
        """Flash sale active থাকলে sale_price, নাহলে original_price"""
        if self.is_on_sale:
            return self.sale_price
        return self.original_price

    @property
    def is_on_sale(self):
        now = timezone.now()
        return (
            self.sale_price is not None and
            self.sale_start is not None and
            self.sale_end is not None and
            self.sale_start <= now <= self.sale_end
        )

    @property
    def discount_percent(self):
        if self.is_on_sale and self.original_price > 0:
            return int((1 - self.sale_price / self.original_price) * 100)
        return 0

    def __str__(self):
        return self.name


class ItemImage(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    item = models.ForeignKey(
        Item,
        related_name='images',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to='item_images/',
        blank=True, null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    video = models.FileField(
        upload_to='item_videos/',
        blank=True, null=True,
        validators=[FileExtensionValidator(['mp4', 'mov', 'webm'])]
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f"{self.item.name} — {self.media_type} {self.order}"



class ProductVariant(models.Model):
    item = models.ForeignKey(
        Item,
        related_name='variants',
        on_delete=models.CASCADE
    )
    size = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    color_code = models.CharField(max_length=10, blank=True, null=True)  # hex color #FF0000
    material = models.CharField(max_length=100, blank=True, null=True)
    additional_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Extra price on top of base price"
    )
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('size', 'color')

    def __str__(self):
        parts = []
        if self.size: parts.append(f"Size: {self.size}")
        if self.color: parts.append(f"Color: {self.color}")
        return f"{self.item.name} — {', '.join(parts) or 'Default'}"

    @property
    def final_price(self):
        base = self.item.sale_price if self.item.is_on_sale else self.item.original_price
        return float(base) + float(self.additional_price)

    @property
    def is_in_stock(self):
        return self.stock > 0