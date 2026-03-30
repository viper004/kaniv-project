from datetime import datetime

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.utils import timezone
from users.models import UserProfile
from .models import Volunteer, Campaign, CampaignEnrollment
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def join_volunteer(request):

    user_profile = UserProfile.objects.get(user=request.user)
    volunteer = Volunteer.objects.filter(user=request.user).first()

    # Detect reapply request
    reapply = request.GET.get("reapply")

    if volunteer and not reapply:

        if volunteer.is_approved:
            return render(request, "volunteer/volunteer_join_form.html", {
                "profile": user_profile,
                "status": "approved"
            })

        elif volunteer.rejection_reason:
            return render(request, "volunteer/volunteer_join_form.html", {
                "profile": user_profile,
                "status": "rejected",
                "reason": volunteer.rejection_reason,
                "age":volunteer.age
            })

        else:
            return render(request, "volunteer/volunteer_join_form.html", {
                "profile": user_profile,
                "status": "pending"
            })

    if request.method == "POST":

        # delete old rejected application
        Volunteer.objects.filter(user=request.user).delete()

        Volunteer.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            age=request.POST.get("age"),
            blood_group=request.POST.get("blood_group"),
            address=request.POST.get("address"),
            reason=request.POST.get("reason"),
            admission_no=request.POST.get("admission_no"),
            period=request.POST.get("period"),
            batch=request.POST.get("batch"),
            year=request.POST.get("year"),
            is_student=True if request.POST.get("admission_no") else False
        )

        return redirect("/")

    return render(request, "volunteer/volunteer_join_form.html", {
        "profile": user_profile
    })


@login_required
def new_campaign(request):
    campaign_type_choices = Campaign.type_choices

    if request.method == "POST":
        try:
            name = (request.POST.get("name") or "").strip()
            description = (request.POST.get("description") or "").strip()
            campaign_type = (request.POST.get("type") or "").strip()
            max_volunteers = request.POST.get("max_volunteers")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")

            if not all([name, description, campaign_type, max_volunteers, start_date, end_date]):
                return JsonResponse({
                    "status": "error",
                    "title": "Missing fields",
                    "message": "All campaign fields are required except current volunteers."
                })

            if campaign_type not in dict(campaign_type_choices):
                return JsonResponse({
                    "status": "error",
                    "title": "Invalid campaign type",
                    "message": "Please select a valid campaign type from the dropdown."
                })

            try:
                max_volunteers = int(max_volunteers)
            except (TypeError, ValueError):
                return JsonResponse({
                    "status": "error",
                    "title": "Invalid volunteer count",
                    "message": "Maximum volunteers must be a valid number."
                })

            if max_volunteers < 0:
                return JsonResponse({
                    "status": "error",
                    "title": "Invalid volunteer count",
                    "message": "Maximum volunteers cannot be negative."
                })

            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            if end_date_obj < start_date_obj:
                return JsonResponse({
                    "status": "error",
                    "title": "Invalid campaign dates",
                    "message": "End date cannot be earlier than start date."
                })

            Campaign.objects.create(
                name=name,
                description=description,
                type=campaign_type,
                max_volunteers=max_volunteers,
                current_volunteers=0,
                start_date=start_date_obj,
                end_date=end_date_obj,
            )

            return JsonResponse({
                "status": "success",
                "title": "Campaign created",
                "message": "The campaign was created successfully."
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "title": "Campaign creation failed",
                "message": str(e)
            })

    today = timezone.localdate()
    active_campaigns = Campaign.objects.filter(end_date__gte=today).order_by("start_date", "-created_on")
    completed_campaigns = Campaign.objects.filter(end_date__lt=today).order_by("-end_date", "-created_on")

    return render(request, "volunteer/new_campaign.html", {
        "today": today.isoformat(),
        "active_campaigns": active_campaigns,
        "completed_campaigns": completed_campaigns,
        "campaign_type_choices": campaign_type_choices,
    })


@login_required
def volunteer_dashboard(request):
    today = timezone.localdate()
    volunteer = Volunteer.objects.filter(user=request.user, is_approved=True, declined=False).first()

    if not volunteer:
        return redirect("volunteer:join_volunteer")

    active_campaigns = Campaign.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).order_by("end_date", "start_date", "-created_on")

    upcoming_campaigns = Campaign.objects.filter(
        start_date__gt=today
    ).order_by("start_date", "end_date", "-created_on")

    enrolled_campaign_ids = set(
        CampaignEnrollment.objects.filter(user=request.user).values_list("campaign_id", flat=True)
    )
    enrolled_campaigns = Campaign.objects.filter(
        id__in=enrolled_campaign_ids
    ).order_by("start_date", "end_date", "-created_on")

    return render(request, "dashboard/volunteer_dashboard.html", {
        "active_campaigns": active_campaigns,
        "upcoming_campaigns": upcoming_campaigns,
        "enrolled_campaigns": enrolled_campaigns,
        "enrolled_campaign_ids": enrolled_campaign_ids,
    })


@login_required
def enroll_campaign(request, id):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "title": "Invalid request",
            "message": "Only POST requests are allowed for enrollment."
        }, status=405)

    volunteer = Volunteer.objects.filter(user=request.user, is_approved=True, declined=False).first()
    if not volunteer:
        return JsonResponse({
            "status": "error",
            "title": "Volunteer access required",
            "message": "Only approved volunteers can enroll in campaigns."
        }, status=403)

    try:
        with transaction.atomic():
            campaign = Campaign.objects.select_for_update().get(id=id)

            if campaign.end_date < timezone.localdate():
                return JsonResponse({
                    "status": "error",
                    "title": "Campaign unavailable",
                    "message": "This campaign is no longer active."
                }, status=400)

            if CampaignEnrollment.objects.filter(user=request.user, campaign=campaign).exists():
                return JsonResponse({
                    "status": "error",
                    "title": "Already enrolled",
                    "message": "You have already enrolled in this campaign."
                }, status=400)

            if campaign.current_volunteers >= campaign.max_volunteers:
                return JsonResponse({
                    "status": "error",
                    "title": "Campaign full",
                    "message": "This campaign has already reached its volunteer limit."
                }, status=400)

            CampaignEnrollment.objects.create(user=request.user, campaign=campaign)
            Campaign.objects.filter(id=campaign.id).update(current_volunteers=F("current_volunteers") + 1)

        return JsonResponse({
            "status": "success",
            "title": "Enrollment successful",
            "message": f"You have successfully enrolled in {campaign.name}."
        })
    except Campaign.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "Campaign not found",
            "message": "This campaign is no longer available."
        }, status=404)


@login_required
def delete_campaign(request, id):
    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "title": "Invalid request",
            "message": "Only GET requests are allowed for deleting a campaign."
        }, status=405)

    try:
        campaign = Campaign.objects.get(id=id)
        campaign_name = campaign.name
        campaign.delete()
        return JsonResponse({
            "status": "success",
            "title": "Campaign deleted",
            "message": f"{campaign_name} was deleted successfully."
        })
    except Campaign.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "Campaign not found",
            "message": "This campaign is no longer available."
        }, status=404)
