from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUserModel


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your Username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your Password',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))


class SignupForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your Username',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your Email Address',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your Full Name',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    phone = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your Phone Number',
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    # ✅ Admin বাদ দিয়ে শুধু Seller/Buyer choice
    USER_TYPE_CHOICES = [
        ('Seller', 'Seller — I want to sell products'),
        ('Buyer', 'Buyer — I want to buy products'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'mr-2'
        })
    )

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Your Password',
            'class': 'w-full py-4 px-6 rounded-xl'
        })
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Your Password',
            'class': 'w-full py-4 px-6 rounded-xl'
        })
    )

    class Meta:
        model = CustomUserModel
        fields = ('username', 'email', 'full_name', 'phone', 'user_type', 'password1', 'password2')