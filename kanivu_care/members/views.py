from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Donor


from django.shortcuts import render
from .models import Donor


def blood_donors(request):
    from users.models import UserProfile
    
    donor_data = []

    # Get member donors from Donor model
    member_donors = (
        Donor.objects
        .filter(is_a_donor=True)
        .select_related(
            "user",
            "user__user",
            "user__user__userprofile"
        )
    )

    for donor in member_donors:
        member = donor.user
        django_user = member.user

        donor_data.append({
            "name": django_user.get_full_name() if django_user.get_full_name() else django_user.username,
            "phone": django_user.userprofile.phone_number,
            "blood_type": member.blood_group,
            "type": "Member",
        })

    # Get user donors from UserProfile (exclude members and coordinators)
    user_donors = (
        UserProfile.objects
        .filter(is_donor=True)
        .exclude(role__in=["member", "coordinator"])
        .select_related("user")
    )

    for user_profile in user_donors:
        donor_data.append({
            "name": user_profile.user.get_full_name() if user_profile.user.get_full_name() else user_profile.user.username,
            "phone": user_profile.phone_number,
            "blood_type": user_profile.blood,
            "type": "User",
        })

    context = {
        "donors": donor_data
    }

    return render(request, "dashboard/blood_donors.html", context)