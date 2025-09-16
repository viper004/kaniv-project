from django import forms

from dashboard.models import FinanceModel,KitReceiverModel,AnnouncementModel


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
        


class announcementForm(forms.ModelForm):
    title=forms.CharField(required=True,error_messages={"required":"Title is required"},widget=forms.TextInput(attrs={
        "id":"title"
    }))
    description=forms.CharField(required=True,error_messages={"required":"Description is required"},widget=forms.Textarea(attrs={
        "id":"description"
    }))
    event_date=forms.DateField(required=True,error_messages={"required":"Event Date is required"},widget=forms.TextInput(attrs={
        "id":"event_date"
    }))
    video_url=forms.URLField(required=False,widget=forms.URLInput(attrs={
        "id":"video_url"
    }))
    thumbnail=forms.ImageField(required=False,widget=forms.FileInput(attrs={
        "id":"thumbnail"
    }))
    photo1=forms.ImageField(required=False,widget=forms.FileInput(attrs={
        "id":"photo1"
    }))
    photo2=forms.ImageField(required=False,widget=forms.FileInput(attrs={
        "id":"photo2"
    }))

    
    class Meta:
        model=AnnouncementModel
        exclude=("user","announced_date")
