import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puddle.settings')
django.setup()

from item.seed_helpers import ensure_categories, get_admin_user, seed_admin_catalog  # noqa: E402

def run_seed():
    ensure_categories()
    admin = get_admin_user()
    if not admin:
        print('কোনো admin/superuser পাওয়া যায়নি।')
        sys.exit(1)

    added = seed_admin_catalog(admin)
    print(f'Admin ({admin.username}): +{added}, মোট {admin.items.count()} ক্যাটালগ আইটেম।')

if __name__ == '__main__':
    run_seed()