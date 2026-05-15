import os
import django
import random
from django.core.files import File

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from item.models import Category, Item
from django.contrib.auth.models import User

def reset_and_seed():
    print("পুরানো ডেটা ডিলিট করা হচ্ছে...")
    Item.objects.all().delete()
    Category.objects.all().delete()

    target_user = User.objects.first()
    if not target_user:
        print("ত্রুটি: ডাটাবেসে কোনো ইউজার পাওয়া যায়নি। আগে একটি সুপারইউজার তৈরি করুন।")
        return

    # ২০টি ক্যাটাগরির লিস্ট
    data_map = [
        {"name": "Air Plane", "prefix": "airplane"},
        {"name": "Arms", "prefix": "arms"},
        {"name": "Bike", "prefix": "bike"},
        {"name": "Car", "prefix": "car"},
        {"name": "Helicopter", "prefix": "helicopter"},
        {"name": "Ship", "prefix": "ship"},
        {"name": "Electronics", "prefix": "elec"},
        {"name": "Furniture", "prefix": "furn"},
        {"name": "Sports", "prefix": "sport"},
        {"name": "Watches", "prefix": "watch"},
        {"name": "Phones", "prefix": "phone"},
        {"name": "Laptops", "prefix": "laptop"},
        {"name": "Fashion", "prefix": "fashion"},
        {"name": "Gaming", "prefix": "game"},
        {"name": "Tools", "prefix": "tool"},
        {"name": "Cameras", "prefix": "camera"},
        {"name": "Drones", "prefix": "drone"},
        {"name": "Bicycles", "prefix": "cycle"},
        {"name": "Music", "prefix": "music"},
        {"name": "Toys", "prefix": "toy"},
    ]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_folder = os.path.join(base_dir, 'item_images')
    
    # ফোল্ডারে থাকা সব ছবির একটি লিস্ট তৈরি (র্যান্ডম ব্যবহারের জন্য)
    all_available_images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    extensions = ['.jpg', '.jpeg', '.png', '.webp']

    total_items_created = 0

    for entry in data_map:
        category = Category.objects.create(name=entry["name"])
        print(f"\nক্যাটাগরি তৈরি হচ্ছে: {entry['name']}")
        
        # প্রতি ক্যাটাগরিতে ১০০টি করে আইটেম (২০ * ১০০ = ২০০০)
        for i in range(1, 101):
            item_name = f"{entry['name']} Premium Edition {i}"
            item = Item(
                category=category,
                name=item_name,
                description=f"This is a high-quality {entry['name']} item. Serial No: {random.randint(1000, 9999)}",
                price=random.randint(50, 5000),
                user=target_user,
                is_sold=False
            )

            # ছবি খোঁজার লজিক
            found_image_path = None
            image_filename = None

            # ১. প্রথমে স্পেসিফিক ছবি খোঁজা (যেমন: airplane1.jpg)
            for ext in extensions:
                temp_filename = f"{entry['prefix']}{i}{ext}"
                temp_path = os.path.join(image_folder, temp_filename)
                if os.path.exists(temp_path):
                    found_image_path = temp_path
                    image_filename = temp_filename
                    break
            
            # ২. স্পেসিফিক ছবি না পেলে র্যান্ডম একটি ছবি ব্যবহার করা (যাতে ValueError না আসে)
            if not found_image_path and all_available_images:
                image_filename = random.choice(all_available_images)
                found_image_path = os.path.join(image_folder, image_filename)

            if found_image_path:
                with open(found_image_path, 'rb') as f:
                    item.image.save(image_filename, File(f), save=True)
                total_items_created += 1
                if total_items_created % 50 == 0:
                    print(f"--- {total_items_created} টি আইটেম যোগ হয়েছে ---")
            else:
                print(f"   [!] {item_name} এর জন্য কোনো ছবি পাওয়া যায়নি।")

    print(f"\nসফলভাবে {total_items_created} টি আইটেম এবং ২০টি ক্যাটাগরি যোগ করা হয়েছে।")

if __name__ == "__main__":
    reset_and_seed()