from item.models import Category


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