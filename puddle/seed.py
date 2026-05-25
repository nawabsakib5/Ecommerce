import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from item.seed_helpers import ensure_categories, get_admin_user, seed_admin_items  # noqa: E402

def run_seed():
    ensure_categories()
    admin = get_admin_user()
    if not admin:
        print('কোনো admin/superuser পাওয়া যায়নি। আগে createsuperuser চালান।')
        sys.exit(1)

    added = seed_admin_items(admin)
    total = admin.items.count()
    print(f'Admin ({admin.username}): +{added} নতুন, মোট {total} আইটেম।')

if __name__ == '__main__':
    run_seed()