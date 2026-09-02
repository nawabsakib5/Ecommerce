from allauth.socialaccount.signals import social_account_added, pre_social_login
from django.dispatch import receiver
from allauth.socialaccount.models import SocialLogin


@receiver(pre_social_login)
def set_user_type_on_social_login(sender, request, sociallogin, **kwargs):
    """Google দিয়ে নতুন user signup হলে Buyer set করো"""
    if sociallogin.is_new:
        user = sociallogin.user
        if not user.pk:
            user.user_type = 'Buyer'
        else:
            if not user.user_type:
                user.user_type = 'Buyer'
                user.save(update_fields=['user_type'])