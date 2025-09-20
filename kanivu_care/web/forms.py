from django import forms

from web.models import DonationModel

class donationModelForm(forms.ModelForm):
    

    full_name=forms.CharField(required=True,error_messages={"required":"Full name is required"},widget=forms.TextInput(attrs={
        "id":"full_name"
    }))
    email=forms.EmailField(required=True,error_messages={"required":"Email is required"},widget=forms.EmailInput(attrs={
        "id":"email"
    }))
    phone_number=forms.CharField(required=True,error_messages={"required":"Phone number is required"},widget=forms.NumberInput(attrs={
        "id":"phone_number"
    }))
    amount=forms.CharField(required=True,error_messages={"required":"Amount is required"},widget=forms.NumberInput(attrs={
        "id":"amount"
    }))
    card_no=forms.CharField(required=True,max_length=16,error_messages={"required":"Card number is required"},widget=forms.NumberInput(attrs={
        "id":"card_no"
    }))
    name_on_card=forms.CharField(required=True,error_messages={"required":"Name on card is required"},widget=forms.TextInput(attrs={
        "id":"name_on_card"
    }))
    expiry_date=forms.CharField(required=True,error_messages={"required":"Expiry Date is required"},widget=forms.TextInput(attrs={
        "id":"expiry_date"
    }))
    cvv=forms.CharField(required=True,max_length=3,error_messages={"required":"CVV is required"},widget=forms.NumberInput(attrs={
        "id":"cvv"
    }))


    class Meta:
        model=DonationModel
        exclude=["user"]