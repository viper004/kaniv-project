from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import User


from convenier.models import pendingMemberAddRequest
from convenier.forms import convenierMemberLoginForm
from convenier.functions import form_errors

# Create your views here.

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
def pendingRequests(req):
    if not req.user.userprofile.role == "convenier":
        return HttpResponseRedirect("/")
    r=pendingMemberAddRequest.objects.filter(isPending=True)

    cntx={
        "pending_requests":r,
        "pending_request_count":r.count()
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
    
