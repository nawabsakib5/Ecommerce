from django.core.management.base import BaseCommand

from item.models import Item
from item.seed_helpers import ensure_categories, get_admin_user, seed_admin_catalog

class Command(BaseCommand):
    help = 'Admin ক্যাটালগ: ৫০টি আইটেম (ছবি সহ) — সব ইউজার দেখতে পারবে।'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-admin',
            action='store_true',
            help='Admin-এর পুরনো ক্যাটালগ আইটেম মুছে ৫০টি নতুন বানাবে',
        )

    def handle(self, *args, **options):
        ensure_categories()
        admin = get_admin_user()

        if not admin:
            self.stdout.write(self.style.WARNING('Admin/superuser পাওয়া যায়নি।'))
            return

        if options.get('reset_admin'):
            deleted, _ = Item.objects.filter(user=admin).delete()
            self.stdout.write(self.style.WARNING(f'Admin ক্যাটালগ মুছে ফেলা: {deleted}'))

        added = seed_admin_catalog(admin)
        total = admin.items.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Admin ({admin.username}): +{added} নতুন, মোট {total} ক্যাটালগ আইটেম।'
            )
        )