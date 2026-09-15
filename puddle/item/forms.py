from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
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
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
            }),
            'condition': forms.Select(attrs={'class': INPUT_CLASSES}),
            'stock_count': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': '1',
                'min': '0',
            }),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
            'sale_price': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Flash sale price (optional)',
                'min': '0',
                'step': '0.01',
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

    # ✅ original_price validation
    def clean_original_price(self):
        price = self.cleaned_data.get('original_price')
        if price is None:
            raise ValidationError("Price is required.")
        if price < Decimal('0'):
            raise ValidationError("Price cannot be negative.")
        if price > Decimal('999999.99'):
            raise ValidationError("Price is too high.")
        return price

    # ✅ stock_count validation
    def clean_stock_count(self):
        stock = self.cleaned_data.get('stock_count')
        if stock is None:
            raise ValidationError("Stock count is required.")
        if stock < 0:
            raise ValidationError("Stock cannot be negative.")
        if stock > 10000:
            raise ValidationError("Stock count is too high (max 10,000).")
        return stock

    # ✅ sale_price validation
    def clean_sale_price(self):
        sale_price = self.cleaned_data.get('sale_price')
        if sale_price is None:
            return sale_price
        if sale_price < Decimal('0'):
            raise ValidationError("Sale price cannot be negative.")
        return sale_price

    # ✅ Cross-field validation
    def clean(self):
        cleaned = super().clean()
        original_price = cleaned.get('original_price')
        sale_price = cleaned.get('sale_price')
        sale_start = cleaned.get('sale_start')
        sale_end = cleaned.get('sale_end')

        # Sale price must be less than original price
        if sale_price and original_price:
            if sale_price >= original_price:
                self.add_error('sale_price', "Sale price must be less than original price.")

        # Sale dates must be provided together
        if sale_price and not (sale_start and sale_end):
            self.add_error('sale_start', "Please set sale start and end dates.")

        # Sale end must be after sale start
        if sale_start and sale_end and sale_end <= sale_start:
            self.add_error('sale_end', "Sale end date must be after start date.")

        return cleaned


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
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
            }),
            'condition': forms.Select(attrs={'class': INPUT_CLASSES}),
            'stock_count': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'min': '0',
            }),
            'image': forms.FileInput(attrs={'class': INPUT_CLASSES}),
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
            'sale_price': forms.NumberInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Flash sale price (optional)',
                'min': '0',
                'step': '0.01',
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

    # ✅ Same validations as NewItemForm
    def clean_original_price(self):
        price = self.cleaned_data.get('original_price')
        if price is None:
            raise ValidationError("Price is required.")
        if price < Decimal('0'):
            raise ValidationError("Price cannot be negative.")
        if price > Decimal('999999.99'):
            raise ValidationError("Price is too high.")
        return price

    def clean_stock_count(self):
        stock = self.cleaned_data.get('stock_count')
        if stock is None:
            raise ValidationError("Stock count is required.")
        if stock < 0:
            raise ValidationError("Stock cannot be negative.")
        if stock > 10000:
            raise ValidationError("Stock count is too high (max 10,000).")
        return stock

    def clean_sale_price(self):
        sale_price = self.cleaned_data.get('sale_price')
        if sale_price is None:
            return sale_price
        if sale_price < Decimal('0'):
            raise ValidationError("Sale price cannot be negative.")
        return sale_price

    def clean(self):
        cleaned = super().clean()
        original_price = cleaned.get('original_price')
        sale_price = cleaned.get('sale_price')
        sale_start = cleaned.get('sale_start')
        sale_end = cleaned.get('sale_end')

        if sale_price and original_price:
            if sale_price >= original_price:
                self.add_error('sale_price', "Sale price must be less than original price.")

        if sale_price and not (sale_start and sale_end):
            self.add_error('sale_start', "Please set sale start and end dates.")

        if sale_start and sale_end and sale_end <= sale_start:
            self.add_error('sale_end', "Sale end date must be after start date.")

        return cleaned