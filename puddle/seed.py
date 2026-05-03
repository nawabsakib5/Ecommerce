import os
import django
from django.core.files import File

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from item.models import Category, Item
from django.contrib.auth.models import User

def reset_and_seed():
    print("পুরানো অসম্পূর্ণ ডেটা ডিলিট করা হচ্ছে...")
    Item.objects.all().delete()
    Category.objects.all().delete()

    target_user = User.objects.first()
    
    # আপনার ফোল্ডার অনুযায়ী ক্যাটাগরি এবং প্রিফিক্স
    data_map = [
        {"name": "Air Plane", "prefix": "airplane"},
        {"name": "Arms", "prefix": "arms"},
        {"name": "Bike", "prefix": "bike"},
        {"name": "Car", "prefix": "car"},
        {"name": "Helicopter", "prefix": "helicopter"},
        {"name": "Ship", "prefix": "ship"},
    ]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_folder = os.path.join(base_dir, 'item_images')

    # সম্ভাব্য সব ফরম্যাট চেক করবে
    extensions = ['.jpg', '.jpeg', '.png', '.webp']

    for entry in data_map:
        category = Category.objects.create(name=entry["name"])
        print(f"ক্যাটাগরি: {entry['name']}")
        
        for i in range(1, 6):
            item_name = f"{entry['name']} Edition {i}"
            item = Item(
                category=category,
                name=item_name,
                description=f"Premium {entry['name']} model {i}.",
                price=5000 + (i * 1000),
                user=target_user,
                is_sold=False
            )

            found_image = False
            for ext in extensions:
                # স্ক্রিনশট অনুযায়ী airplane1.jpg বা airplane2.webp ইত্যাদি চেক করবে
                image_filename = f"{entry['prefix']}{i}{ext}"
                image_path = os.path.join(image_folder, image_filename)

                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        item.image.save(image_filename, File(f), save=True)
                    print(f"   [OK] {item_name} -> {image_filename} যোগ হয়েছে")
                    found_image = True
                    break
            
            if not found_image:
                # যদি কোনো ইমেজই না পাওয়া যায়, তবে এটি সেভ হবে না যাতে পরে এরর না দেয়
                print(f"   [!] {item_name} এর জন্য কোনো ছবি পাওয়া যায়নি, তাই স্কিপ করা হলো")

    print("\nরিসেট এবং সিডিং সম্পন্ন হয়েছে।")

if __name__ == "__main__":
    reset_and_seed()