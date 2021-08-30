from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import chuvsuguide_bot


@csrf_exempt
def index(request):
    return HttpResponse('see you :)')
