"""mnky_chat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.authtoken import views
from django.urls import path
from .views.signup import sign_up, update_profile_pic
from .views.groups import *

urlpatterns = [
    path('login/', views.obtain_auth_token),
    path('signup/', sign_up),
    path('active-chats/', active_chats),
    path('chat-info/', chat_info),
    path('chat/', create_chat),
    path('messages/', get_messages),
    path('files/', get_files),
    path('chat-log/', chat_log),
    path('direct-message/', direct_message),
    path('leave-chat/', leave_chat),
    path('upload-file/', upload_file),
    path('create-chat/', create_chat),
    path('user-info/', user_info),
    path('profile-pic/', update_profile_pic),
    path('chat-image/', chat_pic),
]
