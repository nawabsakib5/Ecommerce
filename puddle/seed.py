import os
import django
import random
import requests
from faker import Faker
from django.core.files.base import ContentFile

# ১. Django এনভায়রনমেন্ট সেটআপ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from item.models import Category, Item
from django.contrib.auth.models import User

fake = Faker()

def seed_production_ready_data():
    # প্রথম ইউজারকে খুঁজে নেওয়া (মডেল অনুযায়ী 'user' ফিল্ডের জন্য)
    target_user = User.objects.first()
    
    if not target_user:
        print("Error: No user found! Railway-তে আগে একটি superuser তৈরি করে নিন।")
        return

    # আপনার ১৩টি ক্যাটাগরি
    categories_list = [
        'Computing', 'Electronics', 'Skincare & Wellness', 
        'Camping & Hiking', 'Photography', 'Bike Gear', 'Tactical Gear',
        'Rifle', 'Pistol', 'Bike', 'Air Plane', 'Helicopter', 'Ship'
    ]

    print("--- Cloudinary Data Seeding Process Started ---")

    for cat_name in categories_list:
        category, created = Category.objects.get_or_create(name=cat_name)
        
        # প্রতি ক্যাটাগরিতে ৩টি করে আইটেম (Cloudinary কোটা সাশ্রয়ের জন্য)
        for i in range(3):
            adjective = random.choice(['Premium', 'Advanced', 'Professional', 'Modern', 'Elite'])
            item_name = f"{adjective} {fake.word().capitalize()}"
            
            # রেন্ডম ইমেজের জন্য Picsum URL
            image_url = f"https://picsum.photos/seed/{random.randint(1, 9999)}/800/800"
            
            try:
                # ইমেজ ডাউনলোড করে মেমরিতে রাখা
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    image_content = ContentFile(response.content)
                    
                    # আইটেম অবজেক্ট তৈরি
                    item = Item(
                        category=category,
                        name=item_name,
                        description=fake.paragraph(nb_sentences=5),
                        price=random.uniform(1500.0, 75000.0),
                        is_sold=False,
                        user=target_user
                    )
                    
                    # ইমেজের নাম দিয়ে সেভ করা (এটি অটোমেটিক Cloudinary-তে আপলোড হবে)
                    file_name = f"{item_name.replace(' ', '_')}_{random.randint(1, 100)}.jpg"
                    item.image.save(file_name, image_content, save=True)
                    
                    print(f"Success: {item_name} uploaded to Cloudinary in {cat_name}")
                else:
                    print(f"Skipped: Could not fetch image for {item_name}")
            except Exception as e:
                print(f"Error for {item_name}: {str(e)}")

    print("\n--- Mission Accomplished! Check your Railway site now. ---")

if __name__ == '__main__':
    seed_production_ready_data()