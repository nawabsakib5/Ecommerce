from django import forms
from .models import Item

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl border border-gray-200 focus:outline-none focus:border-teal-500'
CHECKBOX_CLASSES = 'w-5 h-5 text-teal-600 border-gray-300 rounded focus:ring-teal-500'

class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('category', 'name', 'description', 'price', 'image')
        widgets = {
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Item name'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 4,
                'placeholder': 'Describe your item...'
            }),
            'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': '0.00'
            }),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            }),
        }


class EditItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'description', 'price', 'image', 'is_sold')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Item name'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 4,
                'placeholder': 'Describe your item...'
            }),
            'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': '0.00'
            }),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            }),
            'is_sold': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES
            }),
        }