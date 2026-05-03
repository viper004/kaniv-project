from django.http import HttpResponse


def index(request):
    return HttpResponse("Officials app is ready.")

