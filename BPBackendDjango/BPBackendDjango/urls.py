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
    path('api/changeusername', ChangeUsernameView.as_view(), name='changeUsername'),
    path('api/changeavatar', ChangeAvatarView.as_view(), name='changeAvatar'),
    #exercises
    path('api/getlistofexercises', GetExerciseListView.as_view(), name='getListOfExercises'),
    path('api/getexercise', GetExerciseView.as_view(), name='getExercise'),
    path('api/getexerciselist', GetExerciseListView.as_view(), name='getExerciseList'),
    path('api/doneexercise', DoneExerciseView.as_view(), name='doneExercise'),
    path('api/getdoneexercises', GetDoneExercisesView.as_view(), name='getdoneExercise'),
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
    path('api/getachievements', GetAchievementsView.as_view(), name='getAchievements')
]
