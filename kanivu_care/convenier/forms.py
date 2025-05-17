from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from users.models import UserProfile
from members.models import MCRegistration,memberRegistration

class convenierCoordinatorLoginForm(forms.ModelForm):


    username=forms.CharField(max_length=20,required=True,
        error_messages={'required':"Username is required"},widget=forms.TextInput(attrs={
            "id":"username"
        }))
    
    password=forms.CharField(max_length=20,required=True,
        error_messages={'required':"Password is required"},widget=forms.PasswordInput(attrs={
            "id":"password"
        }))
    
    class Meta:
        model=MCRegistration
        fields=("username","password")

    def save(self,commit=True):
        username=self.cleaned_data.get("username")
        password=self.cleaned_data.get("password")
        user=User.objects.create_user(username=username,password=password)
        profile,created=UserProfile.objects.get_or_create(user=user)
        profile.role="coordinator"
        profile.save()

        instance=super().save(commit=False)
        instance.user=user
        if commit:
            instance.save()
        return instance

    def clean_username(self):
        username=self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.Try another!")
        
        return username
    
    def clean_password(self):
        password=self.cleaned_data.get("password")
        validate_password(password)
        return password
    
    
class convenierMemberLoginForm(forms.ModelForm):
    ROLE_CHOICE=(
        ("member","member"),
        ("coordinator","coordinator")
    )

    username=forms.CharField(max_length=20,required=True,
        error_messages={'required':"Username is required"},widget=forms.TextInput(attrs={
            "id":"username"
        }))
    
    password=forms.CharField(max_length=20,required=True,
        error_messages={'required':"Password is required"},widget=forms.PasswordInput(attrs={
            "id":"password"
        }))
    

    duty=forms.ChoiceField(choices=memberRegistration.DUTY_CHOICES,required=True,error_messages={'required':"Only can be select the given duties"},
        widget=forms.Select(attrs={"id":"duty"}))
    

    class Meta:
        model=memberRegistration
        fields=("username","password")

    def save(self,commit=True):
        username=self.cleaned_data.get("username")
        password=self.cleaned_data.get("password")
        user=User.objects.create_user(username=username,password=password)
        profile,created=UserProfile.objects.get_or_create(user=user)
        profile.role="member"
        profile.save()

        instance=super().save(commit=False)
        instance.user=user
        if commit:
            instance.save()
        return instance


    def clean_username(self):
        username=self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.Try another!")
        
        return username
    
    def clean_password(self):
        password=self.cleaned_data.get("password")
        validate_password(password)
        return password
    
    def clean_role(self):
        role=self.cleaned_data.get("role")
        allowed_roles=["member","coordinator"]

        if role not in allowed_roles:
            raise forms.ValidationError("Invalid Role selected")
        
        return role
    
    def clean_duty(self):
        duty=self.cleaned_data.get("duty")
        available_duties=["No Duty","Finance","Collection Team","Event Organizers","Mini Coordination"]

        if duty not in available_duties:
            raise forms.ValidationError("Invalid duty selected")
        
        return duty