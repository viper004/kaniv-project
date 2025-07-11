from django import forms

from dashboard.models import FinanceModel,KitReceiverModel


class financeModelForm(forms.ModelForm):
    description=forms.CharField(required=False,widget=forms.Textarea(attrs={
        "id":"description"
    }))

    collection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "id": "date",
                "type": "date"  # important for date picker
            },
            format='%Y-%m-%d'  # format for display
        ),
        input_formats=['%Y-%m-%d']  # format for parsing
    )

    collection_type=forms.ChoiceField(choices=FinanceModel.COLLECTION_TYPE_CHOICES,required=True,widget=forms.Select(attrs={
        "id":"select"
    }))

    image=forms.ImageField(required=True,widget=forms.FileInput(attrs={
        "id":"image"
    }))

    class Meta:
        model=FinanceModel
        exclude=["user"]


class kitReceiverForm(forms.ModelForm):
    photo=forms.ImageField(required=False,widget=forms.FileInput(attrs={
        "id":"photo"
    }))
    class Meta:
        model=KitReceiverModel
        exclude=("user","announced_date")
        
