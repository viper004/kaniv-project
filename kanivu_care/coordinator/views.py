from django.shortcuts import render
from django.http.response import JsonResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from coordinator.forms import coordinatorMemberRequestForm
from members.models import memberRegistration

from convenier.models import pendingMemberAddRequest

from users.functions import form_errors

# Create your views here.
@login_required(login_url="users:login")
def requestMember(req):
    if not req.user.userprofile.role == "coordinator":
        return HttpResponseRedirect("/")
    if (req.method=="POST"):
        form=coordinatorMemberRequestForm(req.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "status":"success",
                "title":"Request submitted successfully",
                "message":"Your request for creating member account is successfully sended to convenier.Waiting for his approval."
            })
        else:
            errors=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"Request submitted failed",
                "message":errors
            })
    else:
        form=coordinatorMemberRequestForm()
    
    cntx={
        "form":form
    }
    return render(req,"coordinator/request_member.html",context=cntx)

@login_required(login_url="users:login")
def resubmitRequestMember(req,id):
    if not req.user.userprofile.role == "coordinator":
        return HttpResponseRedirect("/")
    
    user=User.objects.get(id=id)
    pending_user=pendingMemberAddRequest.objects.get(user=user)
    print(pending_user)

    if (not pending_user.isApproved and not pending_user.isPending):
        pending_user.isPending=True
        pending_user.save()
        return JsonResponse({
                "status":"success",
                "title":"Request submitted successfully",
                "message":"Your request for resubmission for this account as member is successfully sended to convenier.Waiting for his approval."
            })
    else:
        return JsonResponse({
            "status":"error",
            "title":"Request resubmission failed",
            "message":"This request is already approved or it is pending."
        })

    


@login_required(login_url="users:login")
def trackMember(req):
    if not req.user.userprofile.role == "coordinator":
        return HttpResponseRedirect("/")
    pendingMembers=pendingMemberAddRequest.objects.all()
    
    cntx={
        "pending_members":pendingMembers
    }
    return render(req,"coordinator/track_member.html",context=cntx)
