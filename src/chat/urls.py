from django.urls import path

from . import views


app_name = "chat"

urlpatterns = [
    path('', views.index, name='index'),    # remember to start with 127.0.0.1:port/chat/
    path('<str:room_name>/', views.room, name='room'),
]