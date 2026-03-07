from django.shortcuts import render,redirect
from users.models import UserProfile
from .models import Volunteer
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def join_volunteer(request):

    user_profile = UserProfile.objects.get(user=request.user)

    volunteer = Volunteer.objects.filter(user=request.user).first()

    if volunteer:

        if volunteer.is_approved:
            return render(request, "volunteer/volunteer_join_form.html", {
                "profile": user_profile,
                "status": "approved"
            })

        elif volunteer.rejection_reason:
            return render(request, "volunteer/volunteer_join_form.html", {
                "profile": user_profile,
                "status": "rejected",
                "reason": volunteer.rejection_reason
            })

        else:
            return render(request, "volunteer/volunteer_join_form.html", {
                "profile": user_profile,
                "status": "pending"
            })


    if request.method == "POST":

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

        return redirect("dashboard")

    return render(request, "volunteer/volunteer_join_form.html", {
        "profile": user_profile
    })