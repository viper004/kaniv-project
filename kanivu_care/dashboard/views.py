from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect,JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import datetime

from dashboard.models import NotifyModel


# Create your views here.

@login_required(login_url="users:login")
def Dashboard(req):
    if (req.user.userprofile.role=="public_user"):
        HttpResponseRedirect("/")

    return render(req,"dashboard/index.html")


@login_required(login_url="/users/login/")
def Notification(req):
    if (req.method=="POST"):
        if not req.user.userprofile.role in ["convenier","coordinator"]:
            return HttpResponseRedirect("/")
        title=req.POST.get("title")
        description=req.POST.get("description")
        programDate=req.POST.get("program_date")
        today=timezone.localdate()


        try:
            if not title or not description:
                return JsonResponse({
                    "status":"error",
                    "title":"Both fields are required",
                    "message":"Title and description are required"
                })
            
            if not programDate:
                return JsonResponse({
                    "status":"error",
                    "title":"Program Date required",
                    "message":"Program date is required.It cannot be blank"
                })
            
            programDateStripped=datetime.strptime(programDate,"%Y-%m-%d").date()
            

            if programDateStripped<today:
                return JsonResponse({
                    "status":"error",
                    "title":"Invalid Program Date",
                    "message":"Program date cannot be set as past"
                })
            NotifyModel.objects.create(
                user=req.user,
                title=title,
                description=description,
                program_date=programDateStripped
            )
            return JsonResponse({
                "status":"success",
                "title":"Notification Uploaded",
                "message":"Your notification is successfully submitted!"
            })
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "title":"Unexpected error occured",
                "message":str(e)
            })
    else:
        pendingNotifications=NotifyModel.objects.filter(is_completed=False)
        today=timezone.localdate()
        for i in pendingNotifications:
            if (i.program_date<today):
                i.is_completed=True
                i.save()
        
        completedNotification=NotifyModel.objects.filter(is_completed=True)
    return render(req,"dashboard/notification.html",context={"pending_notifications":pendingNotifications,"completed_notifications":completedNotification,"today":today.isoformat()})


def deleteNotification(req,id):
    notification=NotifyModel.objects.filter(id=id)

    if notification.exists():
        if (req.user==notification.first().user):
            notification.first().delete()
            return JsonResponse({
                "status":"success",
                "title":"Notification Deleted.",
                "message":"Your notification is successfully deleted!"
            })
        else:
            return JsonResponse({
                "status":"error",
                "title":"Not the same user",
                "message":"You can only delete notification of yours."
            })
    else:
        return JsonResponse({
            "status":"error",
            "title":"This notification doesn't exist",
            "message":"This notification is no longer available on our database"
        })


def endNotify(req,id):
    notification=NotifyModel.objects.filter(id=id)

    if notification.exists():
        instance=notification.first()
        if (req.user==instance.user):
            instance.is_completed=True
            instance.save()
            return JsonResponse({
                "status":"success",
                "title":"Notification is completed.",
                "message":"Your notification is successfully completed (By Force)!"
            })
        else:
            return JsonResponse({
                "status":"error",
                "title":"Not the same user",
                "message":"You can only completed notification of yours."
            })
    else:
        return JsonResponse({
            "status":"error",
            "title":"This notification doesn't exist",
            "message":"This notification is no longer available on our database"
        })