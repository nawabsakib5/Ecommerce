import os
import django
import random
from faker import Faker
from django.contrib.auth import get_user_model

# জ্যাঙ্গো এনভায়রনমেন্ট সেটআপ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from item.models import Item, Category

# ডায়নামিক্যালি ইউজার মডেল লোড করা
User = get_user_model()

def run_seeding():
    fake = Faker()
    # ক্যাটাগরি নিশ্চিত করা
    category, _ = Category.objects.get_or_create(name="General")
    
    users = User.objects.all()
    
    if not users:
        print("ডেটাবেজে কোনো ইউজার নেই! প্রথমে ইউজার তৈরি করুন।")
        return

    print(f"মোট {users.count()} জন ইউজারের জন্য ডাটা জেনারেশন শুরু হচ্ছে...")

    for user in users:
        print(f"-> {user.username} এর জন্য ১০০টি আইটেম তৈরি হচ্ছে...")
        
        items_to_create = []
        for _ in range(100):
            item = Item(
                category=category,
                user=user,
                name=fake.word().capitalize() + " " + fake.word().capitalize(),
                description=fake.paragraph(nb_sentences=3),
                price=random.randint(10, 1000),
                is_sold=False
            )
            items_to_create.append(item)
            
        # Bulk create ব্যবহার করছি যাতে দ্রুত হয়
        Item.objects.bulk_create(items_to_create)
            
    print("\n[SUCCESS] সব ইউজারের জন্য ১০০টি করে ফেক আইটেম সফলভাবে যোগ হয়েছে!")

if __name__ == '__main__':
    run_seeding()