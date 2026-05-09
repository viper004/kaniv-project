from django.shortcuts import render, get_object_or_404
from django.http.response import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from coordinator.forms import coordinatorMemberRequestForm, EventForm
from coordinator.models import Event
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
def resubmitRequestMember(req):
    if not req.user.userprofile.role == "coordinator":
        return HttpResponseRedirect("/")

    if (req.method=="POST"):
        username=req.POST.get("username")
        duty=req.POST.get("duty")
        userid=req.POST.get("userid")

        if not username:
            return JsonResponse({
                "status":"error",
                "title":"Request resubmission failed",
                "message":"Username cannot be blank!"
            })

        validDuties=[i for i,_ in memberRegistration.DUTY_CHOICES]
        if duty not in validDuties:
            return JsonResponse({
                "status":"error",
                "title":"Request resubmission failed",
                "message":"Only the given choices are allowed in duty!"
            })
    
        try:
            user=User.objects.get(id=userid)
            pending_user=pendingMemberAddRequest.objects.get(user=user)
            member=memberRegistration.objects.get(user=user)

            if User.objects.filter(username=username).exclude(username=pending_user.user.username).exists():
                return JsonResponse({
                    "status":"error",
                    "title":"Request resubmission failed",
                    "message":"This username is already taken.Try another!"
                })
            

            if (not pending_user.isApproved and not pending_user.isPending):
                user.username=username
                member.duty=duty
                
                pending_user.isPending=True
                user.save()
                member.save()
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
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "title":"Request resubmission failed",
                "message":str(e)
            })
    return render(req,"coordinator/track_member.html")

@login_required(login_url="users:login")
def trackMember(req):
    if not req.user.userprofile.role == "coordinator":
        return HttpResponseRedirect("/")
    pendingMembers=pendingMemberAddRequest.objects.all()
    
    cntx={
        "pending_members":pendingMembers
    }
    return render(req,"coordinator/track_member.html",context=cntx)

def deleteRecord(req,id):
    if not req.user.userprofile.role == "coordinator":
        return HttpResponseRedirect("/")

    try:
        user=User.objects.get(id=id)
        pending_user=pendingMemberAddRequest.objects.get(user=user)
        pending_user.delete()
        return JsonResponse({
            "status":"success",
            "title":"Record Deleted.",
            "message":"This record deletion is successfull."
        })


    except User.DoesNotExist:
        return JsonResponse({
            "status":"error",
            "title":"Invalid User.",
            "message":"This user is doesn't exist in our database.Refresh your page and try again."
        })
    
    except pendingMemberAddRequest.DoesNotExist:
        return JsonResponse({
            "status":"error",
            "title":"Invalid User.",
            "message":"This user has no pending requests."
        })
    
    except Exception as e:
        return JsonResponse({
            "status":"error",
            "title":"Unexpected Error Occured.",
            "message":str(e)
        })

@login_required(login_url="users:login")
def events_coordinator(req):
    if not req.user.userprofile.role == "coordinator":
        return HttpResponseRedirect("/")
    
    if req.method == "POST":
        form = EventForm(req.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.applied_by = req.user
            event.status = 'PENDING_CONVENER'
            event.save()
            return JsonResponse({
                "status": "success",
                "title": "Event submitted",
                "message": "Your event has been submitted for approval."
            })
        else:
            errors = form_errors(form)
            return JsonResponse({
                "status": "error",
                "title": "Submission failed",
                "message": errors
            })
            
    events = Event.objects.filter(applied_by=req.user).order_by('-applied_on')
    return render(req, "coordinator/events.html", {"form": EventForm(), "events": events})

@login_required(login_url="users:login")
def manage_events(req):
    role = req.user.userprofile.role
    if role not in ["convenier", "principal", "chairman"]:
        return HttpResponseRedirect("/")
    
    if role == "convenier":
        events = Event.objects.filter(status__in=['PENDING_CONVENER', 'REJECTED_TO_CONVENER']).order_by('-applied_on')
    elif role == "principal":
        events = Event.objects.filter(status='PENDING_PRINCIPAL').order_by('-applied_on')
    elif role == "chairman":
        events = Event.objects.filter(status='PENDING_CHAIRMAN').order_by('-applied_on')
    
    return render(req, "coordinator/manage_events.html", {"events": events, "role": role})

@login_required(login_url="users:login")
def approve_event(req, event_id):
    role = req.user.userprofile.role
    event = get_object_or_404(Event, id=event_id)
    
    if role == "convenier" and event.status in ['PENDING_CONVENER', 'REJECTED_TO_CONVENER']:
        event.status = 'PENDING_PRINCIPAL'
    elif role == "principal" and event.status == 'PENDING_PRINCIPAL':
        event.status = 'PENDING_CHAIRMAN'
    elif role == "chairman" and event.status == 'PENDING_CHAIRMAN':
        event.status = 'APPROVED'
    else:
        return JsonResponse({"status": "error", "message": "Unauthorized or invalid state"})
    
    event.save()
    return JsonResponse({"status": "success", "message": "Event approved successfully"})

@login_required(login_url="users:login")
def reject_event(req, event_id):
    role = req.user.userprofile.role
    event = get_object_or_404(Event, id=event_id)
    
    if role in ["principal", "chairman"]:
        event.status = 'REJECTED_TO_CONVENER'
    elif role == "convenier":
        event.status = 'PENDING_CONVENER' # Or some other rejection status
        # Instruction says: "when principal or chairman rejects, show it in conviener"
        # So Principal/Chairman rejection goes to Convener.
        # If Convener rejects... user didn't specify.
    
    event.save()
    return JsonResponse({"status": "success", "message": "Event rejected to Convener"})
