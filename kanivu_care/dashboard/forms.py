from django import forms

from dashboard.models import FinanceModel,KitReceiverModel,AnnouncementModel,CollectionModel




class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    



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
        exclude=["user","announced_date"]
        

class CollectionModelForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "id": "description"
        })
    )

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

    collection_type = forms.ChoiceField(
        choices=CollectionModel.COLLECTION_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            "id": "select"
        })
    )

    total = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "id": "total"
        })
    )

    # Use the custom MultipleFileField instead of regular FileField
    images = MultipleFileField(
        required=True,
        widget=MultipleFileInput(attrs={
            "id": "image",
            "multiple": True
        })
    )

    class Meta:
        model = CollectionModel
        exclude = ["user", "announced_date", "is_completed"]


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
