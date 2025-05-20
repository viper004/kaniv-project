from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect

# Create your views here.

@login_required(login_url="users:login")
def Dashboard(req):
    if (req.user.userprofile.role=="public_user"):
        HttpResponseRedirect("/")

    return render(req,"dashboard/index.html")