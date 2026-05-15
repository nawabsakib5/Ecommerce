from django.db import models
from django.contrib.auth.models import User

class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True) # ফিল্ডের নাম snake_case এ রাখা ভালো
    last_name = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(max_length=200)
    city = models.CharField(max_length=100, null=True, blank=True)
    post_code = models.CharField(max_length=25, null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s billing address"

    def is_fully_filled(self):
        # রিলেশনশিপ ফিল্ড বাদ দিয়ে শুধুমাত্র ডাটা ফিল্ডগুলো চেক করার জন্য
        fields_to_check = [
            self.first_name, self.last_name, self.country, 
            self.address, self.city, self.post_code, self.phone_number
        ]
        for field in fields_to_check:
            if field is None or field == '':
                return False
        return True


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('item.Item') 
    amount = models.FloatField() 
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # SSLCommerz এর জন্য প্রয়োজনীয় ফিল্ডসমূহ
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_status = models.BooleanField(default=False) 
    val_id = models.CharField(max_length=100, null=True, blank=True) 

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    class Meta:
        ordering = ['-ordered_date']