import os
import django
from django.core.files import File

# ১. Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from item.models import Category, Item
from django.contrib.auth.models import User

def clean_and_seed():
    # ২. পুরনো সব ডেটা ডিলিট করা
    print("বসের নির্দেশে পুরনো সব ডেটা ডিলিট করা হচ্ছে...")
    Item.objects.all().delete()
    Category.objects.all().delete()
    print("ডাটাবেস এখন একদম ফ্রেশ।\n")

    # ৩. অ্যাডমিন ইউজার চেক
    target_user = User.objects.first()
    if not target_user:
        print("Error: কোনো ইউজার পাওয়া যায়নি! আগে একটি সুপারইউজার তৈরি করুন।")
        return

    # ৪. আপনার ইমেজ ফোল্ডার অনুযায়ী ক্যাটাগরি ম্যাপিং
    # এখানে ক্যাটাগরির নাম এবং আপনার ফাইলের নামের প্রিফিক্স দেওয়া হয়েছে
    data_map = [
        {"name": "Air Plane", "file_prefix": "airplane"},
        {"name": "Arms", "file_prefix": "arms"},
        {"name": "Bike", "file_prefix": "bike"},
        {"name": "Car", "file_prefix": "car"},
        {"name": "Helicopter", "file_prefix": "helicopter"},
        {"name": "Ship", "file_prefix": "ship"},
        # আপনার স্ক্রিনশটে এই ৬টি ক্যাটাগরির ৩০টি ছবি দেখা যাচ্ছে
    ]

    # ৫. ইমেজের পাথ (রুট ডিরেক্টরির item_images ফোল্ডার)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_source_folder = os.path.join(base_dir, 'item_images')

    print("নতুন ফেক ডেটা এবং আপনার দেওয়া ইমেজগুলো ইনসার্ট করা হচ্ছে...")

    for entry in data_map:
        # ক্যাটাগরি তৈরি
        category = Category.objects.create(name=entry["name"])
        
        # প্রতি ক্যাটাগরিতে ৫টি করে আইটেম (যেহেতু আপনার ৫টি করে ছবি আছে)
        for i in range(1, 6):
            item_name = f"Premium {entry['name']} {i}"
            
            item = Item(
                category=category,
                name=item_name,
                description=f"এটি একটি অরিজিনাল {entry['name']}। আপনার শখের সংগ্রহের জন্য সেরা পছন্দ। কন্ডিশন একদম নতুনের মতো।",
                price=5000 + (i * 1200), # জাস্ট একটা রেন্ডম প্রাইস
                user=target_user,
                is_sold=False
            )

            # আপনার ফাইলের নাম অনুযায়ী ছবি খোঁজা (যেমন: airplane1.jpg)
            # নোট: যদি আপনার ফাইলগুলো .jpg না হয়ে .png হয়, তবে নিচে পরিবর্তন করে নিন
            image_filename = f"{entry['file_prefix']}{i}.jpg" 
            image_path = os.path.join(image_source_folder, image_filename)

            # যদি .jpg নামে না পায়, তবে .png ট্রাই করবে
            if not os.path.exists(image_path):
                image_filename = f"{entry['file_prefix']}{i}.png"
                image_path = os.path.join(image_source_folder, image_filename)

            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    item.image.save(image_filename, File(f), save=True)
                print(f"   [সফল] {item_name} ছবিসহ যোগ করা হয়েছে।")
            else:
                item.save()
                print(f"   [!] {item_name} (ছবি '{image_filename}' খুঁজে পাওয়া যায়নি)")

    print("\nঅভিনন্দন! আপনার সাইট এখন আপনার দেওয়া ইমেজগুলো দিয়ে সাজানো।")

if __name__ == "__main__":
    clean_and_seed()