from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Donor


from django.shortcuts import render
from .models import Donor


def blood_donors(request):
    from users.models import UserProfile
    from coordinator.models import coordinateRegistration
    from volunteer.models import Volunteer
    
    donor_data = []

    # 1. Get member donors from Donor model
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

    # 2. Get coordinator donors from UserProfile
    coordinator_donors = (
        UserProfile.objects
        .filter(role="coordinator", is_donor=True)
        .select_related("user")
    )

    for user_profile in coordinator_donors:
        donor_data.append({
            "name": user_profile.user.get_full_name() if user_profile.user.get_full_name() else user_profile.user.username,
            "phone": user_profile.phone_number,
            "blood_type": user_profile.blood,
            "type": "Coordinator",
        })

    # 3. Get convenier donors from UserProfile
    convenier_donors = (
        UserProfile.objects
        .filter(role="convenier", is_donor=True)
        .select_related("user")
    )

    for user_profile in convenier_donors:
        donor_data.append({
            "name": user_profile.user.get_full_name() if user_profile.user.get_full_name() else user_profile.user.username,
            "phone": user_profile.phone_number,
            "blood_type": user_profile.blood,
            "type": "Convenier",
        })

    # 4. Get volunteer donors (approved volunteers with blood_group set)
    approved_volunteers = (
        Volunteer.objects
        .filter(is_approved=True, declined=False, blood_group__isnull=False)
        .exclude(blood_group="")
        .select_related("user", "user__userprofile")
    )

    for volunteer in approved_volunteers:
        donor_data.append({
            "name": volunteer.name if volunteer.name else volunteer.user.username,
            "phone": volunteer.phone,
            "blood_type": volunteer.blood_group,
            "type": "Volunteer",
        })

    # 5. Get public user donors from UserProfile
    public_user_donors = (
        UserProfile.objects
        .filter(role="public_user", is_donor=True)
        .select_related("user")
    )

    for user_profile in public_user_donors:
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