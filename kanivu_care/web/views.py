from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.db.models import Sum

from web.forms import donationModelForm
from web.models import DonationModel
from dashboard.models import AnnouncementModel, SosMessages
from volunteer.models import Volunteer

from users.functions import form_errors

# Create your views here.

def Home(req):
    volunteer = None
    is_active_volunteer = False
    show_volunteer_cta = False

    if req.user.is_authenticated:
        volunteer = Volunteer.objects.filter(user=req.user).first()
        is_active_volunteer = bool(volunteer and volunteer.is_approved and not volunteer.declined)
        show_volunteer_cta = req.user.userprofile.role not in ["member", "convenier", "coordinator"]
        sos_messages = SosMessages.objects.select_related("user").order_by("-created_at")[:20]
    else:
        sos_messages = []

    return render(req, "index.html", {
        "volunteer": volunteer,
        "is_active_volunteer": is_active_volunteer,
        "show_volunteer_cta": show_volunteer_cta,
        "sos_messages": sos_messages,
    })


def viewAnnouncement(req):
    unhided_announcements=AnnouncementModel.objects.filter(is_hidden=False)
    ongoing_announcements=unhided_announcements.filter(is_completed=False)
    previous_announcements=unhided_announcements.filter(is_completed=True)

    cntx={
        "ongoing_announcements":ongoing_announcements,
        "previous_announcements":previous_announcements
    }

    return render(req,"announcement.html",context=cntx)

@login_required(login_url="users:login")
def donation(req):
    if (req.method=="POST"):
        form=donationModelForm(req.POST)
        if form.is_valid():
            dn=form.save(commit=False)
            dn.user=req.user
            dn.save()
            return JsonResponse({
                "status":"success",
                "title":"Donated successfully",
                "message":"Your donation is recieved successfully.Thank you for your contribution"
            })
        else:
            error=form_errors(form)
            return JsonResponse({
                "status":"error",
                "title":"Contribution submission failed!",
                "message":error
            })
    else:
        cntx={
            "form":donationModelForm()
        }
    return render(req,"donation.html",context=cntx)

@login_required(login_url="users:login")
def myDonations(req):
    my_donations=DonationModel.objects.filter(user=req.user)

    total_amt=DonationModel.objects.filter(user=req.user).aggregate(total_amount=Sum("amount"))
    total_donation_amount=total_amt["total_amount"]
    total_donors=my_donations.count()

    
    cntx={
        "my_donations":my_donations,
        "total_donation_amount":total_donation_amount if total_donation_amount else 0,
        "total_donors":total_donors
    }
    return render(req,"my_donations.html",context=cntx)

@login_required(login_url="users:login")
def viewMyDonation(req,transaction_id):
    try:
        donation=DonationModel.objects.get(user=req.user,transaction_id=transaction_id)
        cntx={
            "donation":donation
        }
        return render(req,"view_my_donation.html",context=cntx)
    except Exception:
        return HttpResponseRedirect("/")
