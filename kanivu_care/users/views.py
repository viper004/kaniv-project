from operator import truediv
import secrets
import base64

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import  redirect, render
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from members.models import memberRegistration


from convenier.models import pendingMemberAddRequest


from users.functions import form_errors
from users.forms import *
from users.models import UserProfile


# Create your views here.

def Register(req):
    if req.user.is_authenticated:
        return HttpResponseRedirect("/")
    if (req.method=="POST"):

        form=UserRegistrationForm(req.POST)
        
        if form.is_valid():
            otp="".join(str(secrets.randbelow(10)) for _ in range(4))

            req.session["otp"]=otp
            print("Your otp is ",otp)

            

            req.session["user"]={
                "username": form.cleaned_data.get('username'),
                "password": form.cleaned_data.get('password'),
                "email":form.cleaned_data.get('email'),
                "role":"public_user"

            }

            return JsonResponse({
                "status":"success",
                "role":"student",
                "title":"Verification code sent successfully",
                "message":"registration successful, please verify your email with OTP"
            })

        else:
            errors=form_errors(form)
            return JsonResponse({
                "status": "error",
                "title":"Errors occured",
                "message":errors
            })
        
    else:
        req.session.flush()
        form=UserRegistrationForm()
        return render(req,'users/login.html',{'form':form})


def resendOTP(req):
    otp="".join(str(secrets.randbelow(10)) for _ in range(4))
    print("Your New Otp is ",otp)
    req.session["otp"]=otp
    return JsonResponse({
        "status":"success",
        "title":"New OTP Sended successfully",
        "message":"New OTP is sended to your number.now this is a valid otp"
    })


def numVerify(req):
    if (req.method=="POST"):
        enteredOtp=req.POST.get('num-otp')
        storedUser=req.session.get("user")
        storedOtp=req.session.get("otp")
        

        if not storedUser:
            return redirect('users:signup')
        
        email=storedUser["email"]

        if len(enteredOtp)!=4 or not enteredOtp.isdigit():
            return JsonResponse({
                "status": "error",
                "title":"Invalid OTP",
                "message":"Otp must be 4 digit"
            })
        
        

        if (enteredOtp==storedOtp):
            username=storedUser["username"]
            password=storedUser["password"]
            email=storedUser["email"]
            user=User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            user.save()

            userp,_=UserProfile.objects.get_or_create(user=user)

            userp.role="public_user"
            req.session.flush()
            loginUser=authenticate(req,username=username,password=password)
            print("login user ",loginUser)
            if loginUser is not None:
                login(req,loginUser)
                return JsonResponse({
                    "status":"success",
                    "title":"User created successfully",
                    "message":"Your account is created successfully"
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "title":"Failed to login user",
                    "message":"May be you can login after some time."
                })
        
        else:
            return JsonResponse({
                "status": "error",
                "title":"Incorrect OTP",
                "message":"This OTP is incorrect.Please recheck the OTP"
            })
    else:
        storedUser=req.session.get("user")
        

        if not storedUser:
            return redirect('users:signup')
        
        email=storedUser["email"]

    return render(req,"users/num_verify.html",context={"email":email})







def Login(req):
    if req.user.is_authenticated:
        return HttpResponseRedirect("/")
    if (req.method=="POST"):
        username=str(req.POST.get('username')).lower()
        password=req.POST.get('password')
        
        user=authenticate(req,username=username,password=password)

        try:
            isUserNameExist=User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "title":"Invalid username",
                "message":"Make sure that your username are correct."
            })


            
        
        if not isUserNameExist.check_password(password):
            return JsonResponse({
                "status": "error",
                "title":"Invalid password",
                "message":"Make sure that your password is correct.if you couldn't find it you can forgot your password by username"
            })
        
        if user is not None:
            print(user.userprofile.role)
            
            if user.userprofile.role == "member":
                member=pendingMemberAddRequest.objects.filter(user=user)
                if (member.exists() and member.first().isApproved==False):
                    return JsonResponse({
                        "status":"error",
                        "title":"Login failed",
                        "message":"Your login request is pending.wait or inform your coordinator"
                    })
        

            login(req,user)
            return JsonResponse({
                "status": "success",
                "title":"Login successful",
                "message":"Redirecting to your dashboard"
            })
        else:
            return JsonResponse({
                "status": "error",
                "title":"Invalid username or password",
                "message":"Make sure that your username and password are correct.if you couldn't find it you can forgot your password by username"
            })
    
    return render(req,'users/login.html')


def Logout(req):
    logout(req)
    return redirect("web:home")

@login_required(login_url="/users/login")
def deleteAccount(req):
    if (req.method=="POST"):
        password=req.POST.get("password")
        SmsEnteredOTP=req.POST.get("sms_otp")
        emailEnteredOTP=req.POST.get("email_otp")
        SmsStoredOTP=req.session.get("account_deletion_otp_for_sms")
        emailStoredOTP=req.session.get("account_deletion_otp_for_email")

        if not(SmsStoredOTP) or not(emailStoredOTP):
            return JsonResponse({
                "status":"error",
                "title":"Cannot get OTP",
                "message":"You can only verify and delete your account from account deletion page.So first visit account deletion page,then resubmit."
            })


        if not (req.user.check_password(password)) or not password:
            return JsonResponse({
                "status":"error",
                "title":"Invalid Password",
                "message":"The entered password is incorrect.Recheck your password and try again"
            })
        
        if emailEnteredOTP and (emailEnteredOTP==emailStoredOTP):
            if req.user.userprofile.phone_number:
                if SmsEnteredOTP and (SmsEnteredOTP==SmsStoredOTP):
                    req.user.delete()
                    req.session.flush()
                    return JsonResponse({
                        "status":"success",
                        "title":"Account deleted successfully",
                        "message":"Your account is deleted successfully.Now you can't recover your account"
                    })
                else:
                    return JsonResponse({
                        "status":"error",
                        "title":"Invalid OTP",
                        "message":"The entered OTP of phone number was incorrect.Try again!"
                    })
            else:
                req.user.delete()
                req.session.flush()
                return JsonResponse({
                    "status":"success",
                    "title":"Account deleted successfully",
                    "message":"Your account is deleted successfully.Now you can't recover your account"
                })
                
        else:
            return JsonResponse({
                "status":"error",
                "title":"Invalid OTP",
                "message":"The entered OTP of email was incorrect.Try again!"
            })
        
    else:
        if req.user.userprofile.phone_number:
            smsotp="".join(str(secrets.randbelow(10)) for i in range(6))
            print("Account deletion otp for sms is ",smsotp)
            req.session["account_deletion_otp_for_sms"]=smsotp

            phno=req.user.userprofile.phone_number
            print("current user phone number is ",phno)

        emailotp="".join(str(secrets.randbelow(10)) for i in range(6))
        print("Account deletion otp for email is ",emailotp)
        req.session["account_deletion_otp_for_email"]=emailotp

        
    return render(req,"users/delete_account.html")


@login_required(login_url="/users/login/")
def Profile(req):
    
    if req.user.is_superuser:
        return redirect("/admin/")
    
    members=UserProfile.objects.filter(role="member")[:2]
    coordinators=UserProfile.objects.filter(role="coordinator")

    cntx={
        "members":members,
        "coordinators":coordinators
    }
    return render(req,'users/profile.html',context=cntx)



@login_required(login_url="/users/login/")
def UpdateProfile(req):
    
    if req.method=="POST":
        if req.user.is_authenticated:
            user_form=userUpdateForm(req.POST or None,instance=req.user)
            profile, created = UserProfile.objects.get_or_create(user=req.user)
            profile_form = userProfileUpdateForm(req.POST or None, instance=profile)

            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                

                req.session.flush()

                login(req,req.user)

                return JsonResponse({
                    "status": "success",
                    "title":"Updated.",
                    "message":"Profile updated successfully",
                })
            else:
                errors=form_errors(user_form) + form_errors(profile_form)
                return JsonResponse({
                    "status": "error",
                    "title":"Errors occured.",
                    "message":errors
                })
        else:
            return JsonResponse({
                    "status": "error",
                    "title":"You are not authenticated",
                    "message":"Seems like you tried to manipulate the code.Refresh (Force refresh (ctrl+shift+r)) the page and get into this page after you login"
                })
    else:
        user_form=userUpdateForm(instance=req.user)
        profile, created = UserProfile.objects.get_or_create(user=req.user)
        profile_form = userProfileUpdateForm(req.POST or None, instance=profile)

    cntx={
        "user_form":user_form,
        "profile_form":profile_form
    }
    
    return render(req,"users/updation.html",context=cntx)



@login_required(login_url="/users/login/")
def verifyPhoneNumber(req):
    phno=req.GET.get("phno")

    if not phno.isdigit() or len(phno)!=10:
        return JsonResponse({
            "status": "error",
            "title":"Invalid phone number",
            "message":"Your phone number must be in digit formst and it required 10 digits only.(Only for indian numbers)"
        })
    otp="".join(str(secrets.randbelow(10)) for _ in range(4))
    req.session["entered_number"]=phno
    req.session["update_num_otp"]=otp
    print("Your otp is ",otp)
    print(phno)
    if (otp):
        return JsonResponse({
            "status":"success",
            "title":"Verification code sent successfully",
            "message":f"Otp is sended to your phone number +91{phno}"
        })
    else:
        return JsonResponse({
            "status": "error",
            "title":"Failed to send verification code",
            "message":f"Unknown error on sending otp to your number +91{phno}"
        })


@login_required(login_url="/users/login/")
def updatePhoneNumber(req):
    if (req.method=="POST"):
        enteredOTP=req.POST.get("otp_collection")
        storedOTP=req.session.get("update_num_otp")

        if not storedOTP:
            return JsonResponse({
                "status": "error",
                "title":"Verification code not found",
                "message":"Redirect to verify number."
            })
        
        if not enteredOTP.isdigit() or len(enteredOTP)!=4:
            return JsonResponse({
                "status": "error",
                "title":"Invalid verification code",
                "message":"Your OTP must be 4 digit and only allowed digits."
            })
        
        if (enteredOTP==storedOTP):
            entered_number=req.session.get("entered_number")
            if entered_number:
                UserProfile.objects.filter(user=req.user).update(phone_number=entered_number)
                return JsonResponse({
                    "status":"success",
                    "title":"Phone number updated successfully",
                    "message":"Your new phone number is updated successfully"
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "title":"Failed to update phone number",
                    "message":"Failed to get phone number"
                })
        else:
            return JsonResponse({
                "status": "error",
                "title":"Incorrect verification code",
                "message":"Incorrect OTP.recheck your otp or resend the new otp"
            })
    
    return render(req,"users/updation.html")
        


def verifyEmail(req):
    email=req.GET.get("email","")

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({
            "status": "error",
            "title": "Invalid Email",
            "message": "Please enter a valid email address (e.g. name@example.com)."
        })
    otp="".join(str(secrets.randbelow(10)) for _ in range(4))
    req.session["entered_email"]=email
    req.session["update_email_otp"]=otp
    print("Your otp is ",otp)
    print(email)
    if (otp):
        return JsonResponse({
            "status":"success",
            "title":"Verification code sent successfully",
            "message":f"Otp is sended to your email {email}"
        })
    else:
        return JsonResponse({
            "status": "error",
            "title":"Failed to send verification code",
            "message":f"Unknown error on sending otp to your email {email}"
        })


@login_required(login_url="/users/login/")
def updateEmail(req):
    if (req.method=="POST"):
        enteredOTP=req.POST.get("email_otp_collection")
        storedOTP=req.session.get("update_email_otp")

        if not storedOTP:
            return JsonResponse({
                "status": "error",
                "title":"Verification code not found",
                "message":"Redirect to verify number."
            })
        
        if len(enteredOTP)!=4:
            return JsonResponse({
                "status": "error",
                "title":"Invalid verification code",
                "message":"Your OTP must be 4 digits."
            })
        
        if (enteredOTP==storedOTP):
            entered_email=req.session.get("entered_email")
            if entered_email:
                User.objects.filter(id=req.user.id).update(email=entered_email)
                return JsonResponse({
                    "status":"success",
                    "title":"Email updated successfully",
                    "message":"Your new email is updated successfully"
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "title":"Failed to update email",
                    "message":"Failed to get email"
                })
        else:
            return JsonResponse({
                "status": "error",
                "title":"Incorrect verification code",
                "message":"Incorrect OTP.recheck your otp or resend the new otp"
            })
    
    return render(req,"users/updation.html")
        


@login_required(login_url="/users/login/")
def updatePassword(req):
    if (req.method=="POST"):
        form=userPasswordChangeForm(req.user,req.POST)
        if form.is_valid():
            form.save()
            login(req,req.user)
            return JsonResponse({
                "status": "success",
                "title":"Password updated successfully",
                "message":"New password is updated successfully"
            })
        else:
            errors=form_errors(form)
            return JsonResponse({
                "status": "error",
                "title":"Errors occured",
                "message":errors
            })
    else:
        form=userPasswordChangeForm(req.user)
    return render(req,"users/update_password.html",context={"form":form})


def forgotPassworSendCode(req):
    req.session["is_forogot_num_verified"]=False
    username=req.GET.get("username","")
    if not username:
        return JsonResponse({
            "status":"success",
            "title":"Username cannot be blank",
            "message":"Username field is required.because only recognize the account by this"
        })
    currentUser=User.objects.filter(username=username).first()
    if currentUser:
        req.session["current_user"]=username
        currentUserNumber=currentUser.userprofile.phone_number
        print("Current user number",currentUserNumber)
        otp="".join(str(secrets.randbelow(10)) for _ in range(4))
        print("Your otp is ",otp)
        req.session["reset_password_otp"]=otp
        stringfiedNumber=str(currentUserNumber)
        staredNumbers="*" * (len(stringfiedNumber)-3)
        lastThreeNumbers=currentUserNumber[-3:]
        maskedNumber=staredNumbers+lastThreeNumbers
        print(maskedNumber)
        return JsonResponse({
            "status":"success",
            "title":"OTP Sened Successfully",
            "message":f"Your OTP is sended to {maskedNumber}"
        })
    else:
        return JsonResponse({
            "status":"error",
            "title":"No user found!",
            "message":"This user is not found in our database.Recheck the username"
        })
    

def forgotPasswordVerify(req):
    if (req.method=="POST"):
        req.session["is_forogot_num_verified"]=False
        enteredOTP=req.POST.get("entered_otp")
        storedOTP=req.session.get("reset_password_otp")

        print(len(enteredOTP))

        if len(enteredOTP)!=4 or not enteredOTP.isdigit():
            return JsonResponse({
                "status":"error",
                "title":"Invalid OTP.Try again",
                "message":"Your OTP must be 4 digit and only allowed numbers."
            })
        
        if not storedOTP:
            return JsonResponse({
                "status":"error",
                "title":"First submit the username",
                "message":"You can only proceed with this by submit your username."
            })
        
        

        if (enteredOTP==storedOTP):
            req.session["is_forogot_num_verified"]=True
            return JsonResponse({
                "status":"success",
                "title":"OTP Verified.Now Reset your password",
                "message":"Your OTP is successfully verified.Now you can reset your password by click OK button."
            })
        else:
            req.session["is_forogot_num_verified"]=False
            return JsonResponse({
                "status":"error",
                "title":"Incorrect OTP,Try again!",
                "message":"Entered OTP is incorrect.recheck your OTP"
            })

    return render(req,"users/forgot_password_verify.html")



def forgotPassword(req):
    is_forogot_num_verified=req.session.get("is_forogot_num_verified")
    if not is_forogot_num_verified==True:
        return redirect("users:forgot_password_verify")
    if (req.method=="POST"):
        username=req.session.get("current_user")
        if not username:
            return JsonResponse({
                "status":"error",
                "title":"Invalid username",
                "message":"Username not found! Recheck it."
            })
        currentUser=User.objects.filter(username=username).first()
        if not currentUser:
            return JsonResponse({
                "status":"error",
                "title":"Username was not found!",
                "message":"Account is not founded by this username.Recheck your username and enter correctly"
            })
        form=resetPasswordForm(currentUser,req.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "status":"success",
                "title":"Password resetted successfully",
                "message":"Your account's password is resetted successfully.Now you can login with this password"
            })
        else:
            error=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"Errors occured",
                "message":error
            })
    else:
        dummyUser=User(username="",password=make_password("temp"))
        form=resetPasswordForm(dummyUser)
    return render(req,"users/forgot_password.html",context={"form":form})

@login_required(login_url="/users/login/")
def editAcademic(req):
    if not (req.user.userprofile.role == "member" or req.user.userprofile.role == "coordinator"):
        return HttpResponseRedirect("/")
    if (req.method=="POST"):
        member,state=memberRegistration.objects.get_or_create(user=req.user)
        form=MCUpdateForm(req.POST,instance=member)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "status":"success",
                "title":"Profile updated",
                "message":"Your academic details are updated."
            })
        else:
            error=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"Errors occured",
                "message":error
            })
    else:
        form=MCUpdateForm(instance=req.user)

    cntx={
        "form":form
    }
        
    return render(req,"users/academic_edit.html",context=cntx)



     

