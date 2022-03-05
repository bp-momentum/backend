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
from .Views.leaderboardviews import ListLeaderboardView
from .Views.userviews import *
from .Views.interfaceviews import *
from .Views.planviews import *
from .Views.friendviews import *
from .Views.achievementviews import *

urlpatterns = [
    #user
    path('admin/', admin.site.urls),
    path('api/createuser', CreateUserView.as_view(), name='createNewUser'),
    path('api/register', RegisterView.as_view(), name='register'),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/auth', AuthView.as_view(), name='authenticateWithToken'),
    path('api/logoutdevices', LogoutAllDevicesView.as_view(), name='logoutAllDevices'),
    path('api/changelanguage', ChangeLanguageView.as_view(), name='changeLanguage'),
    path('api/getlanguage', GetLanguageView.as_view(), name='getLanguage'),
    path('api/deleteaccount', DeleteAccountView.as_view(), name='deleteAccount'),
    path('api/gettrainersuser', GetUsersOfTrainerView.as_view(), name='getUsersOfTrainer'),
    path('api/gettrainers', GetTrainersView.as_view(), name='getTrainers'),
    path('api/deletetrainer', DeleteTrainerView.as_view(), name='deleteTrainer'),
    path('api/deleteuser', DeleteUserView.as_view(), name='deleteUser'),
    path('api/getuserlevel', GetUserLevelView.as_view(), name='GetUserLevel'),
    path('api/getinvited', GetInvitedView.as_view(), name='getInvited'),
    path('api/invalidateinvite', InvalidateInviteView.as_view(), name='invalidateInvite'),
    path('api/changeusername', ChangeUsernameView.as_view(), name='changeUsername'),
    path('api/changepassword', ChangePasswordView.as_view(), name='changePassword'),
    path('api/getresetpasswordemail', GetPasswordResetEmailView.as_view(), name='getResetEmail'),
    path('api/resetpassword', SetPasswordResetEmailView.as_view(), name='resetPassword'),
    path('api/changeavatar', ChangeAvatarView.as_view(), name='changeAvatar'),
    path('api/changemotivation', ChangeMotivationView.as_view(), name='changeMotivation'),
    path('api/getprofile', GetProfileView.as_view(), name='getProfile'),
    path('api/gettrainercontact', GetTrainerContactView.as_view(), name='getTrainerContact'),
    path('api/changelocation', SetTrainerLocationView.as_view(), name='setTrainerLocation'),
    path('api/changetelephone', ChangeTrainerTelephoneView.as_view(), name='setTrainerTelephoneNumber'),
    path('api/changeacademia', ChangeTrainerAcademiaView.as_view(), name='setTrainerAcademia'),
    path('api/searchuser', SearchUserView.as_view(), name='searchUser'),
    path('api/getlistofusers', GetListOfUsers.as_view(), name='getListOfUsers'),
    #exercises
    path('api/getlistofexercises', GetExerciseListView.as_view(), name='getListOfExercises'),
    path('api/getexercise', GetExerciseView.as_view(), name='getExercise'),
    path('api/getexerciselist', GetExerciseListView.as_view(), name='getExerciseList'),
    path('api/doneexercise', DoneExerciseView.as_view(), name='doneExercise'),
    path('api/getdoneexercises', GetDoneExercisesView.as_view(), name='getdoneExercise'),
    path('api/getdoneexercisesinmonth', GetDoneExercisesOfMonthView.as_view(), name='getDoneExercisesInMonth'),
    #plans
    path('api/createplan', CreatePlanView.as_view(), name='createPlan'),
    path('api/addplantouser', AddPlanToUserView.as_view(), name='addExistingPlanToUser'),
    path('api/getlistofplans', GetAllPlansView.as_view(), name='getListOfPlans'),
    path('api/getplan', ShowPlanView.as_view(), name='getPlan'),
    path('api/requestplanofuser', GetPlanOfUser.as_view(), name='getPlanOfUser'),
    path('api/deleteplan', DeletePlanView.as_view(), name='deletePlan'),
    #other
    path('api/ai', AIView.as_view(), name='callAI'),
    #leaderboard
    path('api/listleaderboard', ListLeaderboardView.as_view(), name='listLeaderboard'),
    #achievements
    path('api/getachievements', GetAchievementsView.as_view(), name='getAchievements'),
    #friends
    path('api/getfriends', GetMyFriendsView.as_view(), name='getMyFriends'),
    path('api/getpendingfriendrequests', GetPendingRequestView.as_view(), name='getPendingFriendRequests'),
    path('api/getFriendRequests', GetRequestView.as_view(), name='getFriendRequests'),
    path('api/addFriend', AddFriendView.as_view(), name='addFriend'),
    path('api/acceptfriendrequest', AcceptRequestView.as_view(), name='acceptFriendRequest'),
    path('api/declinefriendrequest', DeclineRequestView.as_view(), name='declineFriendRequest'),
    path('api/removefriend', DeleteFriendView.as_view(), name='removeFriend')
]
