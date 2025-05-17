from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import User

from users.models import UserProfile

from members.models import memberRegistration


from convenier.forms import convenierMemberLoginForm
from convenier.functions import form_errors

# Create your views here.
@login_required(login_url="/users/login")
def Convenier(req):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    return render(req,"convenier/index.html")


@login_required(login_url="/users/login")
def createCoordinator(req):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    
    if (req.method=="POST"):
        form=convenierMemberLoginForm(req.POST)
        if form.is_valid():
            username=form.cleaned_data.get("username")
            password=form.cleaned_data.get("password")
            role=form.cleaned_data.get("role")

            new_user=User.objects.create_user(username=username,password=password)
            UserProfile.objects.create(user=new_user,role=role)

            fr=form.save(commit=False)
            fr.user=new_user
            fr.save()
            return JsonResponse({
                "status":"success",
                "title":"User created",
                "message":"The member is created.now the member can login with the username and password.So kindly share him the username and password"
            })
        else:
            error=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"User creation failed.",
                "message":error
            })
    else:
        form=convenierMemberLoginForm()

    cntx={
        "form":form
    }
    

    return render(req,"convenier/create_coordinator.html",context=cntx)
    
@login_required(login_url="/users/login")
def changeRole(req):
    if not (req.user.userprofile.role == "convenier"):
        return HttpResponseRedirect("/")
    
    members=memberRegistration.objects.filter(user__userprofile__role="member")
    coordinators=memberRegistration.objects.filter(user__userprofile__role="coordinator")

    cntx={
        "members":members,
        "coordinators":coordinators
    }
    return render(req,"convenier/change_role.html",context=cntx)

def promoteUser(req,id):
    user=User.objects.get(id=id)
    userp=UserProfile.objects.get(user=user)
    userp.role="coordinator"
    userp.save()
    return JsonResponse({
        "status":"success",
        "title":"Promoted",
        "message":"Member is promoted as coordinator!",
    })


def demoteUser(req,id):
    user=User.objects.get(id=id)
    userp=UserProfile.objects.get(user=user)
    userp.role="member"
    userp.save()
    return JsonResponse({
        "status":"success",
        "title":"Demoted",
        "message":"Coordinator is demoted as member!",
    })