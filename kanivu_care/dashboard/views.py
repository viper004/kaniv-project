from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect,JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import datetime
import requests
import re

from dashboard.models import NotifyModel,FinanceModel,KitReceiverModel,AnnouncementModel
from dashboard.forms import financeModelForm,kitReceiverForm,announcementForm

from users.functions import form_errors
from users.models import UserProfile

from members.models import memberRegistration

from coordinator.models import coordinateRegistration

from convenier.models import pendingMemberAddRequest



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
        today=timezone.localdate()
        NotifyModel.objects.filter(is_completed=False,program_date__lt=today).update(is_completed=True)
        AnnouncementModel.objects.filter(is_completed=False,event_date__lt=today).update(is_completed=True)
        
        pendingNotifications=NotifyModel.objects.filter(is_completed=False).order_by("-program_date")
        completedNotification=NotifyModel.objects.filter(is_completed=True).order_by("-program_date")

        annnouncements=AnnouncementModel.objects.filter(is_completed=False).order_by('-event_date')
        previous_announcements=AnnouncementModel.objects.filter(is_completed=True).order_by('-event_date')

        cntx={
            "pending_notifications":pendingNotifications,
            "completed_notifications":completedNotification,
            "announcements":annnouncements,
            "previous_announcements":previous_announcements,
            "today":today.isoformat()
        }
    return render(req,"dashboard/notification.html",context=cntx)


def deleteNotification(req,id):
    notification=NotifyModel.objects.filter(id=id)

    if notification.exists():
        if (req.user==notification.first().user or req.user.userprofile.role == "convenier"):
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
        if (req.user==instance.user or req.user.userprofile.role == "convenier"):
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
    
def getThumbnail(url):
    

    patterns = [
        r"(?:v=|vi=)([a-zA-Z0-9_-]{11})",        # watch?v=VIDEOID
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",    # youtu.be/VIDEOID
        r"(?:shorts/)([a-zA-Z0-9_-]{11})",       # shorts/VIDEOID
        r"(?:embed/)([a-zA-Z0-9_-]{11})"         # embed/VIDEOID
    ]

    video_id = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break

    if not video_id:
        response=requests.get(f"https://www.youtube.com/oembed?url={url}&format=json")
        if "application/json" in response.headers.get("Content-Type",""):
            data=response.json()

            if (data["thumbnail_url"]):
                return data["thumbnail_url"]
            else:
                return False
        else:
            return False
    
    print(f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg")

    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

def Announcement(req):
    if (req.method=="POST"):
        try:
            if not req.user.is_authenticated:
                return JsonResponse({
                    "status":"error",
                    "title":"Login required",
                    "message":"You need to login for create the announcements"
                })
            form=announcementForm(req.POST,req.FILES)
            if form.is_valid():
                announce=form.save(commit=False)
                announce.user=req.user
                if (req.POST.get("video_url")):
                    videoUrl=req.POST.get("video_url")
                    thumbnail=req.FILES.get("thumbnail")
                    if (thumbnail):
                        announce.thumbnail=thumbnail
                        announce.save()
                        return JsonResponse({
                            "status":"success",
                            "title":"Announcement added",
                            "message":"Public announcement is added successfully"
                        })
                    else:
                        get_thumbnail=getThumbnail(videoUrl)
                        if get_thumbnail is not False:
                            announce.thumbnail_url=get_thumbnail
                            announce.save()
                            return JsonResponse({
                                "status":"success",
                                "title":"Successfully updated",
                                "message":"This announcement is updated successfully"
                            })
                        else:
                            return JsonResponse({
                                "status":"error",
                                "title":"Thumbnail is required",
                                "message":"Cannot find thumbnail of the video.So add the thumbnail"
                            })
                        
                announce.save()
                return JsonResponse({
                    "status":"success",
                    "title":"Announcement added",
                    "message":"Public announcement is added successfully"
                })
            else:
                error=form_errors(form)
                return JsonResponse({
                    "status":"error",
                    "title":"Failed to add announcement",
                    "message":error
                })
        
        except Exception:
            return JsonResponse({
                "status":"error",
                "title":"Thumbnail is required",
                "message":"Cannot find thumbnail of the video.So add the thumbnail"
            })

    else:
        unhided_announcements=AnnouncementModel.objects.filter(is_hidden=False)
        ongoing_announcements=unhided_announcements.filter(is_completed=False)
        previous_announcements=unhided_announcements.filter(is_completed=True)

        cntx={
            "ongoing_announcements":ongoing_announcements,
            "previous_announcements":previous_announcements
        }


        return render(req,"announcements.html",context=cntx)
    

    

def updateAnnouncement(req):
    if (req.method=="POST"):
        if not req.user.is_authenticated:
            return JsonResponse({
                "status":"error",
                "title":"Login required",
                "message":"You need to login for create the announcements"
            })
        
        
        announcement=AnnouncementModel.objects.filter(id=req.POST.get("data_id"))
        if not announcement.exists():
            return JsonResponse({
                "status":"error",
                "title":"Not found",
                "message":"This announcement is not founded.Refresh and try again"
            })
        
        form=announcementForm(req.POST,req.FILES,instance=announcement.first())
        thumbnail_clear=req.POST.get("thumbnail_clear")
        if form.is_valid():
            announce=form.save(commit=False)
            announce.is_completed=announcement.first().is_completed
            if (req.POST.get("video_url")):
                videoUrl=req.POST.get("video_url")
                thumbnail=req.FILES.get("thumbnail")
                if (thumbnail):
                    announce.thumbnail=thumbnail
                    announce.save()
                    return JsonResponse({
                        "status":"success",
                        "title":"Successfully updated",
                        "message":"This announcement is updated successfully"
                    })
                else:
                    get_thumbnail=getThumbnail(videoUrl)
                    if thumbnail_clear is not None:
                        announce.thumbnail.delete(save=False)
                        announce.thumbnail=None
                        if get_thumbnail is not False:
                            announce.thumbnail_url=get_thumbnail
                            announce.save()
                            return JsonResponse({
                                "status":"success",
                                "title":"Successfully updated",
                                "message":"This announcement is updated successfully"
                            })
                        else:
                            return JsonResponse({
                                "status":"error",
                                "title":"Thumbnail is required",
                                "message":"Cannot find thumbnail of the video.So add the thumbnail"
                            })
                    if get_thumbnail is not False:
                        announce.thumbnail_url=get_thumbnail
                        announce.save()
                        return JsonResponse({
                            "status":"success",
                            "title":"Successfully updated",
                            "message":"This announcement is updated successfully"
                        })
                    else:
                        return JsonResponse({
                            "status":"error",
                            "title":"Thumbnail is required",
                            "message":"Cannot find thumbnail of the video.So add the thumbnail"
                        })
                    
            announce.save()
            return JsonResponse({
                "status":"success",
                "title":"Successfully updated",
                "message":"This announcement is updated successfully"
            })
        else:
            error=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"Failed to update announcement",
                "message":error
            })
    else:
        try:
            id=req.GET.get("id")
            method=req.GET.get("method")


            announcement=AnnouncementModel.objects.get(id=id)
            if method=="end":
                announcement.is_completed=True
                announcement.save()
                
                return JsonResponse({
                    "status":"success",
                    "title":"Announcement is setted as previous.",
                    "message":"Your announcement is successfully moved to previous announcement (By Force)!"
                })
            elif method=="toggle_hide":
                announcement.is_hidden=not announcement.is_hidden
                announcement.save()
                if announcement.is_hidden:
                    is_hidden="Hided"
                else:
                    is_hidden="Unhided"
                return JsonResponse({
                    "status":"success",
                    "title":f"Announcement is {is_hidden}.",
                    "message":f"Your announcement is {is_hidden} successfully"
                })
            elif method=="delete":
                announcement.delete()
                return JsonResponse({
                    "status":"success",
                    "title":"Announcement is deleted.",
                    "message":"Your announcement is successfully deleted!"
                })
            else:
                return JsonResponse({
                    "status":"error",
                    "title":"Invalid method",
                    "message":"Only accepts end,toggle_hide and delete."
                })

        except AnnouncementModel.DoesNotExist:
            return JsonResponse({
                "status":"error",
                "title":"Announcement is not exists",
                "message":"This announcement is doesn't exists.Refresh and try again"
            })
        
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "title":"An error occured!",
                "message":str(e)
            })

    
@login_required(login_url="users:login")
def Finance(req):
    if (req.method=="POST"):
        form=financeModelForm(req.POST,req.FILES)
        if form.is_valid():
            finance=form.save(commit=False)
            finance.user=req.user
            finance.save()
            ft=form.cleaned_data.get("collection_type")
            return JsonResponse({
                "status":"success",
                "title":"Finance updated.",
                "message":f"Your {ft} collection is successfully submitted"
            })
        else:
            errors=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"An error occured",
                "message":errors
            })
    else:
        form=financeModelForm()
        finance=FinanceModel.objects.all()

        cntx={
            "form":form,
            "finance":finance
        }
    
        return render(req,"dashboard/finance.html",context=cntx)




def deleteFinance(req,id):
    finance=FinanceModel.objects.filter(id=id)

    if finance.exists():
        if (req.user==finance.first().user or req.user.userprofile.role == "convenier"):
            finance.first().delete()
            return JsonResponse({
                "status":"success",
                "title":"Finance record Deleted.",
                "message":"Your finance record is successfully deleted!"
            })
        else:
            return JsonResponse({
                "status":"error",
                "title":"Not the same user",
                "message":"You can only delete finance record of yours."
            })
    else:
        return JsonResponse({
            "status":"error",
            "title":"This finance is does not exist",
            "message":"This finance record is no longer available on our database"
        })
    
@login_required(login_url="users:login")
def kitReceivers(req):
    if (req.user.userprofile.role not in ["convenier","coordinator"]):
        return HttpResponseRedirect("/dashboard/")
    if (req.method=="POST"):
        form=kitReceiverForm(req.POST,req.FILES)
        if form.is_valid():
            kit=form.save(commit=False)
            kit.user=req.user
            kit.save()
            return JsonResponse({
                "status":"success",
                "title":"New entry uploaded",
                "message":"The new entry for kit receivers is successfully submitted."
            })
        else:
            error=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"Entry submission failed",
                "message":error
            })
    else:
        form=kitReceiverForm()
    
    cntx={
        "form":form,
        "kit":KitReceiverModel.objects.all()
    }
    return render(req,"dashboard/kit.html",context=cntx)


@login_required(login_url="users:login")
def updateKit(req):
    if (req.method=="POST"):
        kitid=req.POST.get("kitid")
        if not kitid:
            return JsonResponse({
                "status":"error",
                "title":"Kit id is not found!",
                "message":"Reload your webpage then try again."
            })
        kit=KitReceiverModel.objects.filter(id=kitid)
        if kit.exists():
            if (kit.first().user==req.user or req.user.userprofile.role == "convenier"):
                form=kitReceiverForm(req.POST,req.FILES,instance=kit.first())
                if form.is_valid():
                    form.save()
                    return JsonResponse({
                        "status":"success",
                        "title":"Updated Successfully",
                        "message":"Your updation for this kit is successfully updated."
                    })
                else:
                    errors=form_errors(form)
                    return JsonResponse({
                        "status":"error",
                        "title":"Entry submission failed",
                        "message":errors
                    })
            else:
                return JsonResponse({
                "status":"error",
                "title":"Not authorized!",
                "message":"Only the kit's informations are can be edit or delete for the created users."
            })
        else:
            return JsonResponse({
                "status":"error",
                "title":"Not found!",
                "message":"This record is not exists."
            })
        

@login_required(login_url="users:login")
def deleteKit(req,id):
    finance=KitReceiverModel.objects.filter(id=id)

    if finance.exists():
        if (req.user==finance.first().user or req.user.userprofile.role == "convenier"):
            finance.first().delete()
            return JsonResponse({
                "status":"success",
                "title":"Kit receiver record Deleted.",
                "message":"Your kit receiver record is successfully deleted!"
            })
        else:
            return JsonResponse({
                "status":"error",
                "title":"Not the same user",
                "message":"You can only delete kit receiver record of yours."
            })
    else:
        return JsonResponse({
            "status":"error",
            "title":"This kit receiver is does not exist",
            "message":"This kit receiver record is no longer available on our database"
        })
    
@login_required(login_url="users:login")
def changeDuty(req):
    if req.user.userprofile.role not in ["convenier","coordinator"]:
        return HttpResponseRedirect("/")
    if (req.method=="POST"):
        id=req.POST.get("id")
        duty=req.POST.get("duty")
        if not duty:
            return JsonResponse({
                "status":"error",
                "title":"Duty Change Failed",
                "message":"Duty is not found!"
            })
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



    
@login_required(login_url="users:login")
def manageMembers(req):
    if (req.user.userprofile.role == "public_user"):
        return HttpResponseRedirect("/")


    pending_users = pendingMemberAddRequest.objects.filter(isApproved=False).values_list('user', flat=True)

    members = memberRegistration.objects.exclude(user__in=pending_users)
    coordinators=UserProfile.objects.filter(role="coordinator")
    pending_requests=pendingMemberAddRequest.objects.filter(isPending=True)



    cntx={
        "members":members,
        "coordinators":coordinators,
        "pending_requests":pending_requests,
    }
    return render(req,"dashboard/manage_members.html",context=cntx)


@login_required(login_url="/users/login")
def promoteUser(req,id):
    if not (req.user.userprofile.role in ["convenier","coordinator"]):
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

