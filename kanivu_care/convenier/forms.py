from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from users.models import UserProfile
from members.models import memberRegistration

from convenier.models import pendingMemberAddRequest

from coordinator.models import coordinateRegistration

    
class convenierMemberLoginForm(UserCreationForm):
    
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
        user = super().save(commit=False)  # Don't create manually again

        duty = self.cleaned_data.get("duty")
        if commit:
            user.save()

            # Add related models
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = "member"
            profile.save()

            
            memberRegistration.objects.update_or_create(
                user=user,
                defaults={
                    "duty": duty,
                }
            )

            reqmember,_=pendingMemberAddRequest.objects.get_or_create(user=user)
            reqmember.isApproved=True
            reqmember.isPending=False
            reqmember.save()
              # Handle later when MCRegistration is created

        return user

