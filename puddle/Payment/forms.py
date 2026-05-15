from django import forms

from payment.models import BillingAddress

class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ['user', 'First_name','Last_name','Country','Address','City','Post_Code','Phone_Number']