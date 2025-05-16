from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from users.models import UserProfile
from members.models import memberRegistration

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
    
    
    
    role=forms.ChoiceField(choices=ROLE_CHOICE,required=True,error_messages={'required':"Only can be select coordinator and member"},
        widget=forms.Select(attrs={"id":"role"}))
    
    class Meta:
        model=memberRegistration
        fields=("username","password","role")

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