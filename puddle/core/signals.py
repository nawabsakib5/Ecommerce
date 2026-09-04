from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import secrets
import string

User = get_user_model()

@receiver(pre_social_login)
def set_user_type_on_social_login(sender, request, sociallogin, **kwargs):
    user = sociallogin.user

    # Email দিয়ে existing user check করো
    if user.email:
        try:
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)
            return
        except User.DoesNotExist:
            pass

    # নতুন user হলে Buyer set করো এবং random password দাও
    if not user.pk:
        user.user_type = 'Buyer'
        # Random secure password generate করো
        alphabet = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(secrets.choice(alphabet) for i in range(16))
        user.set_password(random_password)