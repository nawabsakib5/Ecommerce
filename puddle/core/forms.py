from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUserModel # আপনার CustomUserModel ইমপোর্ট করুন

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
    # ফিল্ডগুলো সঠিকভাবে ডিফাইন করা
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

    user_type = forms.ChoiceField(choices=CustomUserModel.USER_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'w-full py-4 px-6 rounded-xl'
    }))

    class Meta:
        model = CustomUserModel
        fields = ('username', 'email', 'full_name', 'phone', 'user_type')