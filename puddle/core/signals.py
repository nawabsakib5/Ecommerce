from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver


@receiver(pre_social_login)
def set_user_type_on_social_login(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    if not user.pk:
        # নতুন user — Buyer set করো
        user.user_type = 'Buyer'
    else:
        # আগে থেকে আছে কিন্তু user_type নেই
        if not user.user_type:
            user.user_type = 'Buyer'
            user.save(update_fields=['user_type'])