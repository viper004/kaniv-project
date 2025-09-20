from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse

from web.forms import donationModelForm
from users.functions import form_errors

# Create your views here.

def Home(req):
    return render(req,"index.html")

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