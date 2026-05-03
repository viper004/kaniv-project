from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Donor


from django.shortcuts import render
from .models import Donor


def blood_donors(request):

    donors = (
        Donor.objects
        .filter(is_a_donor=True)
        .select_related(
            "user",
            "user__user",
            "user__user__userprofile"
        )
    )


    donor_data = []

    for donor in donors:

        member = donor.user
        django_user = member.user

        donor_data.append({
            "name": django_user.get_full_name() if django_user.get_full_name() else django_user.username,

            "phone": django_user.userprofile.phone_number,

            "blood_type": member.blood_group,
        })

    context = {
        "donors": donor_data
    }

    return render(request, "dashboard/blood_donors.html", context)