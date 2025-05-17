from django.shortcuts import render

# Create your views here.

def requestMember(req):
    return render(req,"coordinator/request_member.html")