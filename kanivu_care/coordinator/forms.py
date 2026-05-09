from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Event
from members.models import memberRegistration
from convenier.models import pendingMemberAddRequest
from users.models import UserProfile

class coordinatorMemberRequestForm(UserCreationForm):
    username=forms.CharField(max_length=20,required=True,
        error_messages={'required':"Username is required"},widget=forms.TextInput(attrs={
            "id":"username"
        }))
    
    password1=forms.CharField(label="Password",max_length=20,required=True,
        error_messages={'required':"Password is required"},widget=forms.PasswordInput(attrs={
            "id":"password1"
        }))
    
    password2=forms.CharField(label="Confirm Password",max_length=20,required=True,
        error_messages={'required':"Confirm Password is required"},widget=forms.PasswordInput(attrs={
            "id":"password2"
        }))
    
    duty=forms.ChoiceField(choices=memberRegistration.DUTY_CHOICES,required=True,error_messages={'required':"Only can be select the given duties"},
        widget=forms.Select(attrs={"id":"duty"}))
    
    class Meta:
        model=User
        fields=("username","password1","password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        duty = self.cleaned_data.get("duty")
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = "member"
            profile.save()

            request=pendingMemberAddRequest.objects.create(user=user)
            request.isApproved=False
            request.isPending=True
            request.save()
            
            member, _ = memberRegistration.objects.get_or_create(user=user)
            member.duty = duty
            member.save()

        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Event Description', 'rows': 4}),
        }
