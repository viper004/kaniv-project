import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect,JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum

from datetime import datetime
import requests
import re

from web.models import DonationModel
from dashboard.models import NotifyModel,FinanceModel,KitReceiverModel,AnnouncementModel,NotifyModelPriority,CollectionModel,CollectionGalleryModel
from dashboard.forms import financeModelForm,kitReceiverForm,announcementForm,CollectionModelForm

from users.functions import form_errors
from users.models import UserProfile

from members.models import memberRegistration

from coordinator.models import coordinateRegistration

from convenier.models import pendingMemberAddRequest

from volunteer.models import *



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
        department=req.POST.get("department")
        priorityDuty=req.POST.get("selected_section")
        

        


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
            if priorityDuty:
                if not any(choice[0] == priorityDuty for choice in NotifyModelPriority.PRIORITY_DUTY):
                    return JsonResponse({
                        "status":"error",
                        "title":"Invalid section",
                        "message":"Only accepts Collection,Finance,No option"
                    })
                if department:
                    if any(choice[0] == department for choice in memberRegistration.DEPARTMENT_CHOICES):
                        notify=NotifyModel.objects.create(
                            user=req.user,
                            title=title,
                            description=description,
                            program_date=programDateStripped,
                        )
                        NotifyModelPriority.objects.create(
                            notify=notify,
                            department=department,
                            priority_duty=priorityDuty
                        )
                        return JsonResponse({
                            "status":"success",
                            "title":"Notification Uploaded",
                            "message":"Your notification is successfully submitted!"
                        })
                else:
                    notify=NotifyModel.objects.create(
                        user=req.user,
                        title=title,
                        description=description,
                        program_date=programDateStripped,
                    )
                    NotifyModelPriority.objects.create(
                        notify=notify,
                        priority_duty=priorityDuty
                    )
                    return JsonResponse({
                        "status":"success",
                        "title":"Notification Uploaded",
                        "message":"Your notification is successfully submitted!"
                    })
                    
            else:
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
            "today":today.isoformat(),
            "departments":memberRegistration.DEPARTMENT_CHOICES,
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
            
            if req.user.userprofile.role not in ["convenier","coordinator"]:
                return JsonResponse({
                    "status":"error",
                    "title":"Request rejected",
                    "message":"Announcement only can be created by convenier or coordinator"
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


        return render(req,"dashboard/announcements.html",context=cntx)
    

    
@login_required(login_url="users:login")
def updateAnnouncement(req):
    if (req.method=="POST"):
        announcements=AnnouncementModel.objects.filter(id=req.POST.get("data_id"))
        if not announcements.exists():
            return JsonResponse({
                "status":"error",
                "title":"Not found",
                "message":"This announcement is not founded.Refresh and try again"
            })
        announcement=announcements.first()
        
        form=announcementForm(req.POST,req.FILES,instance=announcement)

        if not (req.user==announcement.user or req.user.userprofile.role == "convenier"):
            return JsonResponse({
                "status":"error",
                "title":"Request rejected",
                "message":"Only convenier or the owner of announcement can be update"
            })
        thumbnail_clear=req.POST.get("thumbnail_clear")
        if form.is_valid():
            announce=form.save(commit=False)
            announce.is_completed=announcement.is_completed
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
            print(not req.user==announcement.user or not req.user.userprofile.role == "convenier")
            if not (req.user==announcement.user or req.user.userprofile.role == "convenier"):
                return JsonResponse({
                    "status":"error",
                    "title":"Request rejected",
                    "message":"Only convenier or the owner of announcement can be update"
                })
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
    if not (req.user.userprofile.role == "convenier" or req.user.userprofile.role == "coordinator" or req.user.memberregistration.duty == "Finance" or req.user.memberregistration.duty == "Team Controller"):
        return JsonResponse({
            "status":"error",
            "title":"Request rejected",
            "message":"Only convenier or coordinator or finance duty or team controller duty can access finance"
        })
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


def financeNotification(req):
    notifications=NotifyModelPriority.objects.filter(priority_duty="Finance")
    print(notifications)
    cntx={
        "notifications":notifications
    }
    return render(req,"dashboard/finance_notification.html",context=cntx)



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


@login_required(login_url="users:login")
def collectionTeam(req):
    if req.user.userprofile.role not in ["convenier","coordinator"] and req.user.memberregistration.duty not in ["Collection Team","Team Controller"]:
        return JsonResponse({
            "status":"error",
            "title":"Request rejected",
            "message":"You are not allowed to access this page"
        })
    
    if (req.method == "POST"):
        form = CollectionModelForm(req.POST, req.FILES)
        images = req.FILES.getlist("images")  # Get all uploaded files
        
        if form.is_valid():
            collection_form = form.save(commit=False)
            collection_form.user = req.user
            
            # Check if any images were uploaded
            if not images:
                return JsonResponse({
                    "status": "error",
                    "title": "No images uploaded",
                    "message": "Please upload at least one image."
                })
            
            collection_form.save()
            
            # Process each uploaded image
            for f in images:
                img = CollectionGalleryModel.objects.create(image=f)
                collection_form.images.add(img)
                
            return JsonResponse({
                "status": "success",
                "title": "Collection saved successfully",
                "message": "Your new collection is added successfully."
            })
        else:
            error = form_errors(form)
            return JsonResponse({
                "status": "error",
                "title": "Form submission failed",
                "message": error
            })
    else:
        cntx = {
            "pending_collections": CollectionModel.objects.filter(is_completed=False),
            "completed_collections": CollectionModel.objects.filter(is_completed=True),
            "form": CollectionModelForm()
        }
        
    return render(req, "dashboard/collection_team.html", context=cntx)


@login_required(login_url="users:login")
def updateCollectionTeam(req):
    try:
        if (req.method=="POST"):
            collection_id=req.POST.get("collection_id")
            collection=CollectionModel.objects.get(id=collection_id)
            if not( collection.user==req.user or req.user.userprofile.role not in ["convenier","coordinator"]):
                return JsonResponse({
                    "status":"error",
                    "title":"Request rejected",
                    "message":"Only the created user or convenier or coordinator can update the collection record"
                })
            form=CollectionModelForm(req.POST,req.FILES,instance=collection)
            if form.is_valid():
                f=form.save()
                f.images.clear()
                for file in req.FILES.getlist("images"):
                    gallery_obj = CollectionGalleryModel.objects.create(image=file)
                    f.images.add(gallery_obj)
                
                return JsonResponse({
                    "status":"success",
                    "title":"Collection updated",
                    "message":"This collection is updated successfully."
                })
            else:
                error=form_errors(form)
                return JsonResponse({
                    "status":"error",
                    "title":"Form submission failed",
                    "message":error
                })
            
        else:
            collection_id=req.GET.get("collection_id")
            collection=CollectionModel.objects.get(id=collection_id)

            if not (collection.user==req.user or req.user.userprofile.role in ["convenier","coordinator"]):
                return JsonResponse({
                    "status":"error",
                    "title":"Request rejected",
                    "message":"Only the created user or convenier or coordinator can update the collection record"
                })

            method=req.GET.get("method")
            
            if method=="end":
                collection.is_completed=True
                collection.save()
                return JsonResponse({
                    "status":"success",
                    "title":"Collection is set as completed",
                    "message":"This collection is successfully setted as completed (By FORCE)!"
                })
            elif method=="delete":
                collection.delete()
                return JsonResponse({
                    "status":"success",
                    "title":"Successfully deleted",
                    "message":"This notification is successfully deleted."
                })
            else:
                return JsonResponse({
                    "status":"error",
                    "title":"Invalid method",
                    "message":"Only accepts end and delete"
                })
    except CollectionModel.DoesNotExist:
        return JsonResponse({
            "status":"error",
            "title":"Collection is not exists",
            "message":"This collection is doesn't exists.Refresh and try again"
        })
    
    except Exception as e:
        return JsonResponse({
            "status":"error",
            "title":"An error occured",
            "message":str(e)
        })
            


@login_required(login_url="users:login")
def collectionTeamNotification(req):
    if req.user.userprofile.role not in ["convenier","coordinator"] and req.user.memberregistration.duty not in ["Collection Team","Team Controller"]:
        return JsonResponse({
            "status":"error",
            "title":"Request rejected",
            "message":"You are not allowed to access this page"
        })
    try:
        readed_collection_id=req.GET.get("readed_collection_id")
        if readed_collection_id:
            if req.user.userprofile.role not in "member":
                return JsonResponse({
                    "status":"error",
                    "title":"Request rejected",
                    "message":"Only members can set as read the notification"
                })
            collection=NotifyModelPriority.objects.get(id=readed_collection_id)
            if not req.user.memberregistration.department == collection.department:
                return JsonResponse({
                    "status":"error",
                    "title":"Request rejected",
                    "message":f"Only ${collection.department} students can set as readed"
                })
            collection.is_readed=True
            collection.readed_by=req.user
            collection.save()
            return JsonResponse({
                "status":"success",
                "title":"Readed successfully",
                "message":"This notification is setted as readed"
            })

        notifications=NotifyModelPriority.objects.filter(priority_duty="Collection Team")
        print(notifications)
        cntx={
            "notifications":notifications
        }
    except NotifyModelPriority.DoesNotExist:
        return JsonResponse({
            "status":"error",
            "title":"Not found",
            "message":"This notfication section is not founded"
        })
    except Exception as e:
        return JsonResponse({
            "status":"error",
            "title":"An error occured",
            "message":str(e)
        })
    return render(req,"dashboard/collection_team_notification.html",context=cntx)


@login_required(login_url="users:login")
def donations(req):
    if req.user.userprofile.role not in ["convenier","coordinator"]:
        return HttpResponseRedirect("/")
    
    donotors=DonationModel.objects.all()
    total_amt=DonationModel.objects.aggregate(total_amount=Sum("amount"))
    total_donation_amount=total_amt["total_amount"]
    total_donors=donotors.count()
    cntx={
        "donations":donotors,
        "total_donation_amount":total_donation_amount,
        "total_donors":total_donors
    }
    return render(req,"dashboard/donations.html",context=cntx)


def viewDonation(req,id):
    try:
        donation=DonationModel.objects.get(transaction_id=id)
    except Exception as e:
        return HttpResponseRedirect("/")
    
    return render(req,"dashboard/view_donation.html",context={"donation":donation})

@login_required
def approve_volunteers(request):
    data = Volunteer.objects.filter(is_approved=False, declined=False).order_by("created_at")
    print(data)
    return render(request,"dashboard/approve_volunteers.html",{"data":data})

from django.shortcuts import redirect, get_object_or_404

def approve_volunteer(request):

    if request.method == "POST":
        volunteer_id = request.POST.get("volunteer_id")

        volunteer = get_object_or_404(Volunteer, id=volunteer_id)

        volunteer.is_approved = True
        volunteer.save()

    return redirect("dashboard:approve_volunteers")


def reject_volunteer(request):
    if request.method == "POST":

        volunteer_id = request.POST.get("volunteer_id")
        reason = request.POST.get("reason")

        volunteer = get_object_or_404(Volunteer, id=volunteer_id)

        volunteer.declined = True
        volunteer.rejection_reason = reason
        volunteer.save()

    return redirect("dashboard:approve_volunteers")

@login_required
def manage_volunteers(request):
    user = Volunteer.objects.filter(is_approved=True,is_student=False)
    student = Volunteer.objects.filter(is_approved = True, is_student=True)
    return render(request, "dashboard/manage_volunteers.html", {"members": user,"students":student})

@login_required
def remove_volunteer(request):
    if request.user.userprofile.role not in ["convenier", "coordinator"]:
        return JsonResponse({
            "status": "error",
            "title": "Permission denied",
            "message": "You are not authorized to remove volunteers."
        }, status=403)

    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "title": "Invalid request",
            "message": "Only POST requests are allowed for volunteer removal."
        }, status=405)

    volunteer_id = request.POST.get("volunteer_id")

    if not volunteer_id:
        try:
            payload = json.loads(request.body or "{}")
            volunteer_id = payload.get("volunteer_id")
        except (json.JSONDecodeError, TypeError):
            volunteer_id = None

    if not volunteer_id:
        return JsonResponse({
            "status": "error",
            "title": "Volunteer not found",
            "message": "Volunteer id is required to remove a volunteer."
        }, status=400)

    try:
        volunteer = Volunteer.objects.get(id=volunteer_id, is_approved=True)
    except Volunteer.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "Volunteer not found",
            "message": "This volunteer is no longer available."
        }, status=404)

    volunteer_name = volunteer.name or volunteer.user.username
    volunteer.delete()

    return JsonResponse({
        "status": "success",
        "title": "Volunteer removed",
        "message": f"{volunteer_name} has been removed successfully."
    })

@login_required
def volunteer_dashboard(request):
    return redirect("volunteer:volunteer_dashboard")
