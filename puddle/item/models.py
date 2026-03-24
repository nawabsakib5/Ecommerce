from django.db import models
from django.contrib.auth.models import*
# Create your models here.
class Category(models.Model):
    name =models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    

class Item (models.Model):
    category = models.ForeignKey(Category , related_name='items' , on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True , null=True)
    price = models.FloatField()
    image = models. ImageField(upload_to='item_images' , blank=True,null=True)
    is_sold = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name