from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
import json

# Create your views here.

def index(request):
    return render(request, 'chat/index.html', {})


# @login_required             # to take care of situations of anonymous users eg incognito
def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),         # marks room_name server-side as opposed to doing it client-side
        'username': mark_safe(json.dumps(request.user.username))    # marks username server-side as opposed to doing it client-side
    })