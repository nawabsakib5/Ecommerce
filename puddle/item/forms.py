from django import forms

forms .models import Item

class NewItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('catergory', 'name' , 'description', 'price', 'image', )