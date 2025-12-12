# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("api/chat/", views.chat_api, name="cattle_chat_api"),
    path("", views.chat_page, name="cattle_chat_page"),  # we'll define chat_page below
]
