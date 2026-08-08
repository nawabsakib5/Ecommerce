from django import forms
from .models import Item

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl border border-gray-200 focus:outline-none focus:border-teal-500'
CHECKBOX_CLASSES = 'w-5 h-5 text-teal-600 border-gray-300 rounded focus:ring-teal-500'

class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            'category', 'name', 'description',
            'original_price', 'condition', 'stock_count',
            'image',
            'sale_price', 'sale_start', 'sale_end',
        )
        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Item name'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 4,
                'placeholder': 'Describe your item...'
            }),
            'original_price': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': '0.00'
            }),
            'condition': forms.Select(attrs={'class': INPUT_CLASSES}),
            'stock_count': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': '1'
            }),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
            'sale_price': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Flash sale price (optional)'
            }),
            'sale_start': forms.DateTimeInput(attrs={
                'class': INPUT_CLASSES,
                'type': 'datetime-local'
            }),
            'sale_end': forms.DateTimeInput(attrs={
                'class': INPUT_CLASSES,
                'type': 'datetime-local'
            }),
        }


class EditItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            'name', 'description',
            'original_price', 'condition', 'stock_count',
            'image', 'status',
            'sale_price', 'sale_start', 'sale_end',
        )
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
            'original_price': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': '0.00'
            }),
            'condition': forms.Select(attrs={'class': INPUT_CLASSES}),
            'stock_count': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
            'sale_price': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Flash sale price (optional)'
            }),
            'sale_start': forms.DateTimeInput(attrs={
                'class': INPUT_CLASSES,
                'type': 'datetime-local'
            }),
            'sale_end': forms.DateTimeInput(attrs={
                'class': INPUT_CLASSES,
                'type': 'datetime-local'
            }),
        }