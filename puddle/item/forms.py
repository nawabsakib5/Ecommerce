from django import forms
from .models import Item

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl border'
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
                'class': INPUT_CLASSES 
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES 
            }),
            'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES 
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
                'class': INPUT_CLASSES 
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES 
            }),
            'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES 
            }),
            'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES 
            }),
            # 'is_sold' চেকবক্সের জন্য সুন্দর স্টাইলিং উইজেট যোগ করা হলো
            'is_sold': forms.CheckboxInput(attrs={
                'class': CHECKBOX_CLASSES
            }),
        }