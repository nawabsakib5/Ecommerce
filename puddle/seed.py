import os
import django
import random
import requests
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from faker import Faker
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from item.models import Item, Category

fake = Faker()
User = get_user_model()

CATEGORY_NAMES = [
    'Electronics', 'Clothing', 'Books', 'Furniture', 'Sports',
    'Toys', 'Vehicles', 'Food', 'Beauty', 'Music',
    'Gaming', 'Jewelry', 'Tools', 'Garden', 'Pets',
    'Baby', 'Office', 'Art', 'Travel', 'Fitness',
    'Kitchen', 'Shoes', 'Bags', 'Watches', 'Cameras',
    'Phones', 'Laptops', 'Tablets', 'TVs', 'Audio',
    'Lighting', 'Bedding', 'Cleaning', 'Stationery', 'Crafts',
    'Outdoors', 'Fishing', 'Cycling', 'Swimming', 'Yoga',
    'Cooking', 'Baking', 'Coffee', 'Tea', 'Wine',
    'Comics', 'Movies', 'Anime', 'Collectibles', 'Vintage',
]


def get_or_create_categories():
    categories = []
    for name in CATEGORY_NAMES:
        cat, _ = Category.objects.get_or_create(name=name)
        categories.append(cat)
    print(f"[CATEGORIES] {len(categories)} categories ready!")
    return categories


def download_image(item_name):
    """Picsum থেকে random real image download করে"""
    try:
        seed_id = random.randint(1, 1000)
        url = f"https://picsum.photos/seed/{seed_id}/400/400"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filename = f"item_{item_name.replace(' ', '_').lower()[:20]}_{seed_id}.jpg"
            return ContentFile(response.content, name=filename)
    except Exception:
        pass
    return None


def seed_for_user(user, categories, count):
    existing = Item.objects.filter(user=user).count()
    if existing >= count:
        print(f"[SKIP] {user.username} — already has {existing} items")
        return

    needed = count - existing
    print(f"[START] {user.username} — creating {needed} items...")

    for i in range(needed):
        category = random.choice(categories)
        name = fake.word().capitalize() + " " + fake.word().capitalize()
        description = fake.paragraph(nb_sentences=3)
        price = round(random.uniform(10, 1000), 2)

        # ✅ Model follow করে item create
        item = Item(
            category=category,
            user=user,
            name=name,
            description=description,
            price=price,
            is_sold=False,
        )

        # ✅ Real image download করে save
        image_file = download_image(name)
        if image_file:
            item.image.save(image_file.name, image_file, save=False)

        item.save()

        if (i + 1) % 25 == 0:
            print(f"  → {i + 1}/{needed} done...")

    print(f"[SUCCESS] {user.username} — {needed} items created!")


def run():
    categories = get_or_create_categories()
    users = User.objects.all()

    if not users.exists():
        print("কোনো ইউজার নেই!")
        return

    for user in users:
        count = 2000 if (user.is_superuser or user.is_staff) else 200
        seed_for_user(user, categories, count)

    print("\n✅ All done!")


if __name__ == '__main__':
    run()