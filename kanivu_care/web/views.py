from django.shortcuts import render

# Create your views here.

def Home(req):
    return render(req,"index.html")