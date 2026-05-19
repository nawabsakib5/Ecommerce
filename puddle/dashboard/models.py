from django.db import models
from django.conf import settings 

class Profile(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'