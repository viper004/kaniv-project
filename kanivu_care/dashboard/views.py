from django.shortcuts import render

# Create your views here.

def Dashboard(req):
    return render(req,"dashboard/index.html")