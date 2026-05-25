from item.models import Category
from .models import Notification


def categories(request):
    return {
        'all_categories': Category.objects.all()
    }


def is_seller(request):
    if request.user.is_authenticated:
        return {
            'is_seller': request.user.user_type == 'Seller'
        }
    return {'is_seller': False}


def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}