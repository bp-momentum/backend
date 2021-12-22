"""BPBackendDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views111
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from .Views.exerciseviews import *
from .Views.userviews import *
from .Views.interfaceviews import *
from .Views.planviews import *
from .Views.friendviews import *

urlpatterns = [
    #user
    path('admin/', admin.site.urls),
    path('api/createuser', CreateUserView.as_view(), name='createNewUser'),
    path('api/register', RegisterView.as_view(), name='register'),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/auth', AuthView.as_view(), name='authenticateWithToken'),
    path('api/logoutdevices', LogoutAllDevicesView.as_view(), name='logoutAllDevices'),
    path('api/ai', APIView.as_view(), name='callAI'),
    path('api/deleteuser', DeleteAccountView.as_view(), name='deleteUser'),
    #exercises
    path('api/getlistofexercises', GetExerciseListView.as_view(), name='getListOfExercises'),
    path('api/getexercise', GetExerciseView.as_view(), name='getExercise'),
    path('api/getexerciselist', GetExerciseListView.as_view(), name='getExerciseList'),
    #plans
    path('api/createplan', CreatePlanView.as_view(), name='createPlan'),
    path('api/addplantouser', AddPlanToUserView.as_view(), name='addExistingPlanToUser'),
    path('api/getlistofplans', GetAllPlansView.as_view(), name='getListOfPlans'),
    path('api/getplan', ShowPlanView.as_view(), name='getPlan'),
    path('api/requestplanofuser', GetPlanOfUser.as_view(), name='getPlanOfUser'),
    path('api/deleteplan', DeletePlanView.as_view(), name='deletePlan'),
    #friends
    path('api/getfriends', GetMyFriendsView.as_view(), name='getMyFriends'),
    path('api/getpendingfriendrequests', GetPendingRequestView.as_view(), name='getPendingFriendRequests'),
    path('api/getFriendRequests', GetRequestView.as_view(), name='getFriendRequests'),
    path('api/addFriend', AddFriendView.as_view(), name='addFriend'),
    path('api/acceptfriendrequest', AcceptRequestView.as_view(), name='acceptFriendRequest'),
    path('api/declinefriendrequest', DeclineRequestView.as_view(), name='declineFriendRequest'),
    path('api/removefriend', DeleteFriendView.as_view(), name='removeFriend')
]
