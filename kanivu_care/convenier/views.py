from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import User

from users.models import UserProfile

from members.models import memberRegistration

from coordinator.models import coordinateRegistration

from convenier.models import pendingMemberAddRequest
from convenier.forms import convenierMemberLoginForm
from convenier.functions import form_errors

# Create your views here.
@login_required(login_url="/users/login")
def Convenier(req):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    return render(req,"convenier/index.html")

@login_required(login_url="/users/login")
def createMember(req):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")

    if req.method == "POST":
        form = convenierMemberLoginForm(req.POST)
        if form.is_valid():
            form.save()  # User + profile + memberRegistration created inside form
            return JsonResponse({
                "status": "success",
                "title": "User created",
                "message": "The member is created. Now the member can login with the username and password. Kindly share it with them."
            })
        else:
            error = form_errors(form)
            return JsonResponse({
                "status": "error",
                "title": "User creation failed.",
                "message": error
            })
    else:
        form = convenierMemberLoginForm()

    return render(req, "convenier/create_member.html", context={"member_form": form})

    
@login_required(login_url="/users/login")
def changeRole(req):
    if not (req.user.userprofile.role == "convenier"):
        return HttpResponseRedirect("/")
    
    members=UserProfile.objects.filter(user__userprofile__role="member")
    coordinators=UserProfile.objects.filter(role="coordinator")



    cntx={
        "members":members,
        "coordinators":coordinators
    }
    return render(req,"convenier/change_role.html",context=cntx)

def promoteUser(req,id):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    user=User.objects.get(id=id)
    userp=UserProfile.objects.get(user=user)
    userp.role="coordinator"
    userp.save()

    muser=memberRegistration.objects.get(user=user)
    muser.delete()
    muser.save()

    cuser=coordinateRegistration.objects.create(user=user)
    cuser.save()

    
    return JsonResponse({
        "status":"success",
        "title":"Promoted",
        "message":"Member is promoted as coordinator!",
    })


def demoteUser(req,id):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    user=User.objects.get(id=id)
    userp=UserProfile.objects.get(user=user)
    userp.role="member"
    userp.save()

    cuser=coordinateRegistration.objects.get(user=user)
    cuser.delete()
    cuser.save()

    muser=memberRegistration.objects.create(user=user)
    muser.save()

    return JsonResponse({
        "status":"success",
        "title":"Demoted",
        "message":"Coordinator is demoted as member!",
    })



def pendingRequests(req):
    r=pendingMemberAddRequest.objects.all()
    cntx={
        "pending_requests":r
    }
    return render(req,"convenier/pending_requests.html",context=cntx)