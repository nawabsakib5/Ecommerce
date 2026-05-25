from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from item.seed_helpers import (
    create_items_per_category,
    ensure_categories,
    get_admin_user,
    seed_admin_items,
)

class Command(BaseCommand):
    help = 'Admin: ১০০০ আইটেম। --user দিলে ক্যাটাগরি প্রতি ২টি।'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='ইউজারনেম')

    def handle(self, *args, **options):
        ensure_categories()
        added = seed_admin_items()
        admin = get_admin_user()

        if admin:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Admin ({admin.username}): +{added}, মোট {admin.items.count()}'
                )
            )
        else:
            self.stdout.write(self.style.WARNING('Admin পাওয়া যায়নি।'))

        username = options.get('user')
        if username:
            User = get_user_model()
            user = User.objects.filter(username=username).first()
            if not user:
                self.stdout.write(self.style.ERROR(f'"{username}" নেই।'))
                return
            n = create_items_per_category(user)
            self.stdout.write(self.style.SUCCESS(f'{username}: +{n} আইটেম।'))