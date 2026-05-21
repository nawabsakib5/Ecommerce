import random
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from item.models import Item, Category

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_items(sender, instance, created, **kwargs):
    if created:
        categories = Category.objects.all()
        # প্রতিটি ক্যাটাগরি থেকে ৫টি করে আইটেম তৈরি
        for category in categories:
            items_to_create = []
            for i in range(5):
                item = Item(
                    category=category,
                    user=instance,
                    name=f"{category.name} Product {i+1}",
                    description="Auto-generated item for testing.",
                    price=round(random.uniform(10, 1000), 2),
                    is_sold=False,
                )
                
                # ইমেজ ডাউনলোডের চেষ্টা
                try:
                    response = requests.get("https://picsum.photos/400/400", timeout=3)
                    if response.status_code == 200:
                        item.image.save(f"item_{instance.id}_{category.id}_{i}.jpg", ContentFile(response.content), save=False)
                except:
                    pass # এরর হলে ইমেজ ছাড়াই সেভ হবে
                
                items_to_create.append(item)
            
            # ক্যাটাগরি অনুযায়ী বাল্ক সেভ
            Item.objects.bulk_create(items_to_create)