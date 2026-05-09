from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Donor


from django.shortcuts import render
from .models import Donor


import logging
from datetime import date
from django.shortcuts import render
from users.models import UserProfile
from members.models import Donor, memberRegistration
from volunteer.models import Volunteer

logger = logging.getLogger(__name__)

def blood_donors(request):
    donor_dict = {}

    def calculate_age(dob):
        """Calculate age from date of birth"""
        if not dob:
            return None
        today = date.today()
        try:
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except Exception:
            return None

    def get_donor_entry(user):
        if user.id not in donor_dict:
            profile = getattr(user, 'userprofile', None)
            donor_dict[user.id] = {
                "name": user.get_full_name() or user.username,
                "phone": profile.phone_number if profile else None,
                "blood_type": profile.blood if profile else None,
                "date_of_birth": profile.date_of_birth if profile else None,
                "age": profile.age if profile else None,
                "roles": set()
            }
        return donor_dict[user.id]

    # 1. Process EVERY UserProfile marked as is_donor=True
    # This includes Coordinators, Conveners, Office Staff, and Public Users
    profiles = UserProfile.objects.filter(is_donor=True).select_related("user")
    for p in profiles:
        entry = get_donor_entry(p.user)
        role_map = {
            "coordinator": "Coordinator",
            "convenier": "Convener",
            "public_user": "User",
            "office_staff": "Office Staff",
            "principal": "Principal",
            "chairman": "Chairman",
            "member": "Member"
        }
        role_display = role_map.get(p.role, p.role.capitalize() if p.role else "User")
        entry["roles"].add(role_display)

    # 2. Process the Donor model (Member-specific donor records)
    member_donors = Donor.objects.filter(is_a_donor=True).select_related(
        "user", "user__user", "user__user__userprofile"
    )
    for d in member_donors:
        member = d.user
        if not member.user: continue
        entry = get_donor_entry(member.user)
        entry["roles"].add("Member")
        
        # Fill in missing data from member registration if UserProfile is incomplete
        if not entry["blood_type"] or entry["blood_type"] == "":
            entry["blood_type"] = member.blood_group
        if not entry["date_of_birth"]:
            entry["date_of_birth"] = member.date_of_birth
        if not entry["age"]:
            entry["age"] = member.age or calculate_age(member.date_of_birth)

    # 3. Process Approved Volunteers (considered donors if they have blood group set)
    volunteers = Volunteer.objects.filter(
        is_approved=True, 
        declined=False
    ).exclude(blood_group__isnull=True).exclude(blood_group="").select_related("user", "user__userprofile")
    
    for v in volunteers:
        entry = get_donor_entry(v.user)
        entry["roles"].add("Volunteer")
        
        # Fill in missing data
        if not entry["phone"]: entry["phone"] = v.phone
        if not entry["blood_type"] or entry["blood_type"] == "":
            entry["blood_type"] = v.blood_group
        if not entry["date_of_birth"]:
            entry["date_of_birth"] = v.date_of_birth
        if not entry["age"]:
            entry["age"] = v.age or calculate_age(v.date_of_birth)

    # Finalize list
    donor_list = []
    for donor in donor_dict.values():
        # Include even if blood type is missing for now (helps debug)
        if not donor["blood_type"] or donor["blood_type"] == "":
            donor["blood_type"] = "Not set"
            
        # Refine roles: If they have multiple specific roles, remove the generic "User" role
        if len(donor["roles"]) > 1:
            donor["roles"].discard("User")
            
        donor["type"] = ", ".join(sorted(list(donor["roles"])))
        donor_list.append(donor)

    return render(request, "dashboard/blood_donors.html", {"donors": donor_list})