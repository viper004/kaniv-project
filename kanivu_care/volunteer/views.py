from datetime import datetime

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.utils import timezone
from django.utils.dateformat import format as date_format
from users.models import UserProfile
from .models import Volunteer, Campaign, CampaignEnrollment, Volunteer_Notifications
from django.contrib.auth.decorators import login_required


def _validate_campaign_payload(request, campaign_type_choices):
    name = (request.POST.get("name") or "").strip()
    description = (request.POST.get("description") or "").strip()
    campaign_type = (request.POST.get("type") or "").strip()
    max_volunteers = request.POST.get("max_volunteers")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    if not all([name, description, campaign_type, max_volunteers, start_date, end_date]):
        return None, {
            "status": "error",
            "title": "Missing fields",
            "message": "All campaign fields are required except current volunteers."
        }

    if campaign_type not in dict(campaign_type_choices):
        return None, {
            "status": "error",
            "title": "Invalid campaign type",
            "message": "Please select a valid campaign type from the dropdown."
        }

    try:
        max_volunteers = int(max_volunteers)
    except (TypeError, ValueError):
        return None, {
            "status": "error",
            "title": "Invalid volunteer count",
            "message": "Maximum volunteers must be a valid number."
        }

    if max_volunteers < 0:
        return None, {
            "status": "error",
            "title": "Invalid volunteer count",
            "message": "Maximum volunteers cannot be negative."
        }

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    if end_date_obj < start_date_obj:
        return None, {
            "status": "error",
            "title": "Invalid campaign dates",
            "message": "End date cannot be earlier than start date."
        }

    return {
        "name": name,
        "description": description,
        "type": campaign_type,
        "max_volunteers": max_volunteers,
        "start_date": start_date_obj,
        "end_date": end_date_obj,
    }, None

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
            campaign_data, error_response = _validate_campaign_payload(request, campaign_type_choices)
            if error_response:
                return JsonResponse(error_response)

            Campaign.objects.create(
                name=campaign_data["name"],
                description=campaign_data["description"],
                type=campaign_data["type"],
                max_volunteers=campaign_data["max_volunteers"],
                current_volunteers=0,
                start_date=campaign_data["start_date"],
                end_date=campaign_data["end_date"],
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
    campaign_details = {}

    all_campaigns = list(active_campaigns) + list(completed_campaigns)
    campaign_ids = [campaign.id for campaign in all_campaigns]

    enrollments = CampaignEnrollment.objects.filter(campaign_id__in=campaign_ids).select_related("user")
    volunteer_map = {
        volunteer.user_id: volunteer
        for volunteer in Volunteer.objects.filter(user_id__in=[enrollment.user_id for enrollment in enrollments])
    }

    enrollments_by_campaign = {campaign_id: [] for campaign_id in campaign_ids}
    for enrollment in enrollments:
        volunteer = volunteer_map.get(enrollment.user_id)
        enrollments_by_campaign.setdefault(enrollment.campaign_id, []).append({
            "name": volunteer.name if volunteer else enrollment.user.get_full_name() or enrollment.user.username,
            "email": volunteer.email if volunteer else enrollment.user.email,
            "phone": volunteer.phone if volunteer else "",
            "blood_group": volunteer.blood_group if volunteer and volunteer.blood_group else "N/A",
            "is_student": bool(volunteer and volunteer.is_student),
            "batch": volunteer.batch if volunteer and volunteer.batch else "N/A",
            "year": volunteer.year if volunteer and volunteer.year else "N/A",
            "joined_on": date_format(timezone.localtime(enrollment.joined_on), "M j, Y, P"),
        })

    for campaign in all_campaigns:
        campaign_details[campaign.id] = {
            "id": campaign.id,
            "name": campaign.name,
            "type": campaign.get_type_display(),
            "type_key": campaign.type,
            "description": campaign.description,
            "start_date": campaign.start_date.isoformat(),
            "end_date": campaign.end_date.isoformat(),
            "max_volunteers": campaign.max_volunteers,
            "current_volunteers": campaign.current_volunteers,
            "created_on": date_format(timezone.localtime(campaign.created_on), "M j, Y, P"),
            "enrolled_candidates": enrollments_by_campaign.get(campaign.id, []),
        }

    return render(request, "volunteer/new_campaign.html", {
        "today": today.isoformat(),
        "active_campaigns": active_campaigns,
        "completed_campaigns": completed_campaigns,
        "campaign_type_choices": campaign_type_choices,
        "campaign_details": campaign_details,
    })


@login_required
def update_campaign(request, id):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "title": "Invalid request",
            "message": "Only POST requests are allowed for updating a campaign."
        }, status=405)

    campaign_type_choices = Campaign.type_choices

    try:
        campaign = Campaign.objects.get(id=id)
        campaign_data, error_response = _validate_campaign_payload(request, campaign_type_choices)
        if error_response:
            return JsonResponse(error_response)

        if campaign_data["max_volunteers"] < campaign.current_volunteers:
            return JsonResponse({
                "status": "error",
                "title": "Invalid volunteer limit",
                "message": "Maximum volunteers cannot be less than the current enrolled volunteers."
            })

        campaign.name = campaign_data["name"]
        campaign.description = campaign_data["description"]
        campaign.type = campaign_data["type"]
        campaign.max_volunteers = campaign_data["max_volunteers"]
        campaign.start_date = campaign_data["start_date"]
        campaign.end_date = campaign_data["end_date"]
        campaign.save()

        return JsonResponse({
            "status": "success",
            "title": "Campaign updated",
            "message": "The campaign was updated successfully."
        })
    except Campaign.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "Campaign not found",
            "message": "This campaign is no longer available."
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "title": "Campaign update failed",
            "message": str(e)
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
    volunteer_notifications = Volunteer_Notifications.objects.order_by("-date", "-send_date")

    return render(request, "dashboard/volunteer_dashboard.html", {
        "active_campaigns": active_campaigns,
        "upcoming_campaigns": upcoming_campaigns,
        "enrolled_campaigns": enrolled_campaigns,
        "enrolled_campaign_ids": enrolled_campaign_ids,
        "volunteer_notifications": volunteer_notifications,
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


@login_required
def unenroll_campaign(request, id):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "title": "Invalid request",
            "message": "Only POST requests are allowed for unenrollment."
        }, status=405)

    try:
        with transaction.atomic():
            campaign = Campaign.objects.select_for_update().get(id=id)
            enrollment = CampaignEnrollment.objects.select_for_update().get(
                user=request.user,
                campaign=campaign
            )

            # Check if campaign starts within 24 hours
            now = timezone.now()
            # Create timezone-aware datetime for campaign start at midnight in the configured timezone
            campaign_start_naive = datetime.combine(campaign.start_date, datetime.min.time())
            campaign_start = timezone.make_aware(campaign_start_naive, timezone.get_current_timezone())
            hours_until_start = (campaign_start - now).total_seconds() / 3600

            if hours_until_start < 24:
                return JsonResponse({
                    "status": "error",
                    "title": "Cannot unenroll",
                    "message": "You cannot unenroll from campaigns that start within 24 hours to avoid last-minute disruptions."
                }, status=400)

            # Delete enrollment and update volunteer count
            enrollment.delete()
            Campaign.objects.filter(id=campaign.id).update(current_volunteers=F("current_volunteers") - 1)

            return JsonResponse({
                "status": "success",
                "title": "Unenrollment successful",
                "message": f"You have successfully unenrolled from {campaign.name}."
            })

    except CampaignEnrollment.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "Not enrolled",
            "message": "You are not enrolled in this campaign."
        }, status=404)
    except Campaign.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "title": "Campaign not found",
            "message": "This campaign is no longer available."
        }, status=404)
