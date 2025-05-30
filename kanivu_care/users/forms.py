from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,PasswordChangeForm,SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

from users.models import UserProfile
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
    username=forms.CharField(max_length=150,required=True,widget=forms.TextInput(attrs={
        "id":"username"
    }))

    first_name=forms.CharField(label="Name",max_length=15,widget=forms.TextInput(attrs={
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

    gender=forms.ChoiceField(choices=GENDER,widget=forms.Select(attrs={
        "id":"gender"
    }))

    address=forms.TextInput()

    class Meta:
        model=UserProfile
        fields=["gender","address"]


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


class MCUpdateForm(UserChangeForm):

    DEPARTMENT_CHOICES = (
        ("bba", "BBA"),
        ("bca", "BCA"),
        ("bsc_cs", "BSc CS"),
        ("bcom_tax", "BCom Tax"),
        ("ttm", "TTM"),
        ("bcom_ca_and_finance", "BCom CA and Finance"),
        ("bcom_co_operation", "BCom Co-operation"),
        ("ba_literature", "BA Literature"),
        ("ba_communicative_english", "BA Communicative English"),
        ("ba_journalism", "BA Journalism"),
        ("electronics", "Electronics"),
        ("bsw", "BSW"),
    )

    YEAR_CHOICES = (
        ("1", "First Year"),
        ("2", "Second Year"),
        ("3", "Third Year"),
        ("4", "Fourth Year"),
    )

    adno=forms.CharField(label="Admission number",max_length=150,widget=forms.NumberInput(attrs={
        "id":"adno"
    }))

    batch=forms.CharField(label="Name",max_length=15,widget=forms.TextInput(attrs={
        "id":"batch"
    }))

    department=forms.ChoiceField(label="Department",choices=DEPARTMENT_CHOICES,widget=forms.Select(attrs={
        "id":"department"
    }))

    current_year=forms.ChoiceField(label="Current Year",choices=YEAR_CHOICES,widget=forms.Select(attrs={
        "id":"year"
    }))
    
    
    password=None

    class Meta:
        model=User
        fields=('adno','batch',"department","current_year")