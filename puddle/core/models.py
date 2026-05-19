from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUserModel(AbstractUser):
    
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    USER_TYPE_CHOICES = [
        ('Admin', 'Admin'),
        ('Seller', 'Seller'),
        ('Buyer', 'Buyer'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.username