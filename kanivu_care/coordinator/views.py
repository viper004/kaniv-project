from django.shortcuts import render
from django.http.response import JsonResponse

from coordinator.forms import coordinatorMemberRequestForm

from users.functions import form_errors

# Create your views here.

def requestMember(req):
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