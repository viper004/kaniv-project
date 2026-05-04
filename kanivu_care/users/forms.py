from django import forms
from django.contrib.auth.forms import UserChangeForm,PasswordChangeForm,SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

from users.models import UserProfile
from members.models import memberRegistration
from django import forms
from django.contrib.auth.models import User



class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        error_messages={'required': 'Username is required'},
        required=True,
        widget=forms.TextInput(attrs={
            "id": "username",
            "placeholder": "Enter Username",
            "autocomplete": "off",
        }),
        help_text=""
    )

    email = forms.EmailField(
        label="Email",
        error_messages={'required': 'Email is required'},
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            "id": "email",
            "placeholder": "Enter Email",  # fixed typo
        })
    )

    password = forms.CharField(
        label="Password",
        error_messages={'required': 'Password is required'},
        max_length=20,
        required=True,
        widget=forms.PasswordInput(attrs={
            "id": "password",
            "placeholder": "Enter Password",
            "autocomplete": "off",
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)  # ✅ Apply built-in validators
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash password
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                role="public_user",
            )
        return user




class userUpdateForm(UserChangeForm):
    username=forms.CharField(max_length=150,error_messages={'required':'Username is required'},required=True,widget=forms.TextInput(attrs={
        "id":"username"
    }))

    first_name=forms.CharField(label="Name",error_messages={'required':'Name is required'},max_length=15,widget=forms.TextInput(attrs={
        "id":"fname"
    }))

    
    
    password=None

    class Meta:
        model=User
        fields=('first_name','username')


class userProfileUpdateForm(forms.ModelForm):
    GENDER = (
        ("", "Select a gender"),
        ("male", "male"),
        ("female", "female"),
    )

    gender=forms.ChoiceField(choices=GENDER,error_messages={'required':'Gender is required'},widget=forms.Select(attrs={
        "id":"gender"
    }))

    photo=forms.ImageField(required=False,widget=forms.FileInput(attrs={
        "id":"photo"
    }))

    address=forms.TextInput()

    blood=forms.ChoiceField(
        label="Blood Group",
        choices=UserProfile.BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            "id":"blood_group"
        })
    )

    is_donor=forms.BooleanField(
        label="I am a blood donor",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "id":"is_donor",
            "class":"toggle-checkbox"
        })
    )

    class Meta:
        model=UserProfile
        fields=["gender","photo","address","blood","is_donor"]


class userPasswordChangeForm(PasswordChangeForm):
    old_password=forms.CharField(label="Old Password",error_messages={"required":"Old Password is required"},max_length=20,required=True,widget=forms.PasswordInput(attrs={
        "id":"oldpwd",
        "placeholder":"Enter Old Password",
        "autocomplete":"off",
    })
    )
    new_password1=forms.CharField(label="New Password",error_messages={"required":"New Password is required"},max_length=20,required=True,widget=forms.PasswordInput(attrs={
        "id":"newpwd1",
        "placeholder":"Enter New Password",
        "autocomplete":"off",
    }))
    new_password2=forms.CharField(label="Confirm New Password",error_messages={"required":"Confirm New Password is required"},max_length=20,required=True,widget=forms.PasswordInput(attrs={
        "id":"newpwd2",
        "placeholder":"Confirm New Password",
        "autocomplete":"off",
    }))
    class Meta:
        model=User
        fields=('old_password','new_password1','new_password2')



class resetPasswordForm(SetPasswordForm):
    new_password1=forms.CharField(label="New Password",max_length=20,required=True,widget=forms.PasswordInput(attrs={
        "id":"newpwd1",
        "placeholder":"Enter New Password",
        "autocomplete":"off",
    }))
    new_password2=forms.CharField(label="Confirm New Password",max_length=20,required=True,widget=forms.PasswordInput(attrs={
        "id":"newpwd2",
        "placeholder":"Confirm New Password",
        "autocomplete":"off",
    }))                                                                       

    class Meta:
        model=User
        fields=("new_password1","new_password2")


class MCUpdateForm(forms.ModelForm):
    adno = forms.CharField(label="Admission Number", max_length=255, widget=forms.TextInput(attrs={
        "id": "adno"
    }))

    department = forms.ChoiceField(label="Department", choices=memberRegistration.DEPARTMENT_CHOICES, widget=forms.Select(attrs={
        "id": "department"
    }))

    start_year = forms.CharField(label="Start Year", max_length=5, widget=forms.TextInput(attrs={
        "id": "start_year",
        "maxlength": "4",
        "inputmode": "numeric",
        "placeholder": "e.g., 2022",
    }))

    end_year = forms.CharField(label="End Year", max_length=5, widget=forms.TextInput(attrs={
        "id": "end_year",
        "maxlength": "4",
        "inputmode": "numeric",
        "placeholder": "e.g., 2025",
    }))

    class Meta:
        model = memberRegistration
        fields = ("adno", "department", "start_year", "end_year")
