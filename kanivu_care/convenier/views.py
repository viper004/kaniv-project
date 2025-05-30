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


    pending_users = pendingMemberAddRequest.objects.filter(isApproved=False).values_list('user', flat=True)

    members = memberRegistration.objects.exclude(user__in=pending_users)
    coordinators=UserProfile.objects.filter(role="coordinator")


    cntx={
        "members":members,
        "coordinators":coordinators
    }
    return render(req,"convenier/change_role.html",context=cntx)


@login_required(login_url="/users/login")
def promoteUser(req,id):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    user=User.objects.get(id=id)
    userp=UserProfile.objects.get(user=user)
    userp.role="coordinator"
    userp.save()

    memberRegistration.objects.get(user=user).delete()

    coordinateRegistration.objects.get_or_create(user=user)
    
    return JsonResponse({
        "status":"success",
        "title":"Promoted",
        "message":"Member is promoted as coordinator!",
    })


@login_required(login_url="/users/login")
def demoteUser(req,id):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    user=User.objects.get(id=id)
    userp=UserProfile.objects.get(user=user)
    userp.role="member"
    userp.save()

    coordinateRegistration.objects.get(user=user).delete()

    memberRegistration.objects.get_or_create(user=user)
    return JsonResponse({
        "status":"success",
        "title":"Demoted",
        "message":"Coordinator is demoted as member!",
    })


@login_required(login_url="/users/login")
def pendingRequests(req):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    r=pendingMemberAddRequest.objects.filter(isPending=True)
    cntx={
        "pending_requests":r
    }
    return render(req,"convenier/pending_requests.html",context=cntx)


@login_required(login_url="/users/login")
def requestApproved(req,id):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    user=User.objects.get(id=id)
    muser=pendingMemberAddRequest.objects.get(user=user)
    if not muser:
        return JsonResponse({
            "status":"error",
            "title":"Request submitted failed",
            "message":"This user is not available"
        })
    muser.isApproved=True
    muser.isPending=False
    muser.save()

    return JsonResponse({
        "status":"success",
        "title":"Request is approved",
        "message":f"The requested member {user.username} can login and update their member account"
    })

    




@login_required(login_url="/users/login")
def requestRejected(req,id):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    reason=req.GET.get("reason")

    if not reason:
        return JsonResponse({
            "status":"success",
            "title":"No Reason Found!",
            "message":"Reason is required for rejection"
        })

    user=User.objects.get(id=id)
    muser=pendingMemberAddRequest.objects.get(user=user)
    if not muser:
        return JsonResponse({
            "status":"error",
            "title":"Request submitted failed",
            "message":"This user is not available"
        })
    
    muser.isApproved=False
    muser.isPending=False
    muser.reason=reason
    muser.save()

    return JsonResponse({
        "status":"success",
        "title":"Request is rejected",
        "message":f"The requested member {user.username}'s Request permission was rejected due to {reason}"
    })
    

@login_required(login_url="users:login")
def changeDuty(req):
    if not req.user.userprofile.role == "convenier" or not req.user.userprofile.role == "coordinator" :
        return HttpResponseRedirect("/")
    if (req.method=="POST"):
        id=req.POST.get("id")
        duty=req.POST.get("duty")
        try:
            user=User.objects.get(id=id)
            member=memberRegistration.objects.get(user=user)
            currentDuty=member.duty
            member.duty=duty
            member.save()
            return JsonResponse({
                "status":"success",
                "title":"Duty Changed Successfully",
                "message":f"{user.username}'s Duty has been changed from {currentDuty} to {member.duty}"
            })
        except User.DoesNotExist:
            return JsonResponse({
                "status":"error",
                "title":"Duty Change Failed",
                "message":"This user is not available"
            })
        except memberRegistration.DoesNotExist:
            return JsonResponse({
                "status":"error",
                "title":"Duty Change Failed",
                "message":"This user is not a member"
            })
        
        except Exception as e:
            return JsonResponse({
                    "status":"error",
                    "title":"Unexpected Error!",
                    "message":str(e)
                })

    return render(req,"convenier/change_duty.html")

@login_required(login_url="users:login")
def kickMember(req):
    print("User:", req.user.userprofile)

    if req.user.userprofile.role not in ["coordinator", "convenier"]:
        return JsonResponse({
            "status": "error",
            "title": "Permission Denied",
            "message": "You are not authorized to perform this action!"
        })

    try:
        entered_id = req.GET.get("id")

        if not entered_id:
            return JsonResponse({
                "status": "error",
                "title": "Missing ID",
                "message": "No user ID was provided."
            })
        user = User.objects.get(id=entered_id)
        member = memberRegistration.objects.get(user=user)
        user_profile=UserProfile.objects.get(user=user)

        member.delete()
        user_profile.role="public_user"
        user_profile.save()

        return JsonResponse({
            "status": "success",
            "title": "Kicked Successfully",
            "message": f"{user.username} has been kicked from members,from now {user.username} is a public user!"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "User Not Found",
            "message": "This user does not exist."
        })

    except memberRegistration.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "Not a Member",
            "message": "This user is not a registered member."
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "title": "Unexpected Error",
            "message": str(e)
        })

