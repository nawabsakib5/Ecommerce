from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUserModel(AbstractUser):
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    USER_TYPE_CHOICES = [
        ('Admin', 'Admin'),
        ('Seller', 'Seller'),
        ('Buyer', 'Buyer'),
    ]
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('sale', 'Item Sold'),
        ('admin', 'Admin Notice'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='general'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='wishlist',
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        'item.Item',
        related_name='wishlisted_by',
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ('-added_at',)

    def __str__(self):
        return f"{self.user.username} → {self.item.name}"


class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        'item.Item',
        related_name='reviews',
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.username} — {self.item.name} ({self.rating}★)"




class Shop(models.Model):
    SHOP_TYPE_CHOICES = [
        ('individual', 'Individual Seller'),
        ('cod_seller', 'COD Seller'),
        ('verified', 'Verified Shop'),
        ('b2b', 'B2B Seller'),
    ]

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='shop',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='shop_banners/', blank=True, null=True)
    shop_type = models.CharField(
        max_length=20,
        choices=SHOP_TYPE_CHOICES,
        default='individual'
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name



class Banner(models.Model):
    BANNER_TYPES = [
        ('hero', 'Hero Slider'),
        ('side', 'Side Banner'),
        ('flash', 'Flash Sale Banner'),
        ('category', 'Category Banner'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    link = models.CharField(max_length=500, blank=True, null=True)
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='hero')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('order', '-created_at')

    def __str__(self):
        return f"{self.title} ({self.get_banner_type_display()})"