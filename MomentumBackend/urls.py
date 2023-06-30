"""MomentumBackend URL Configuration

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

from .Views import userviews
from .Views import exerciseviews
from .Views import planviews
from .Views import ratingview

urlpatterns = [
    # user
    path("admin/", admin.site.urls),

    # account
    path("api/register", userviews.register, name="register"),
    path("api/createuser", userviews.createUser, name="createNewUser"),
    path("api/login", userviews.login, name="login"),
    path("api/checklogin", userviews.checklogin, name="checkLogin"),
    path("api/logout", userviews.logout, name="logout"),
    path("api/deleteaccount", userviews.deleteAccount, name="deleteAccount"),
    path("api/changelanguage", userviews.changeLanguage, name="changeLanguage"),
    path("api/getlanguage", userviews.getLanguage, name="getLanguage"),
    path("api/gettrainersuser", userviews.getTrainersUsers,
         name="getUsersOfTrainer"),
    path("api/gettrainers", userviews.getTrainers, name="getTrainers"),
    path("api/deletetrainer", userviews.deleteTrainer, name="deleteTrainer"),
    path("api/deleteuser", userviews.deleteUser, name="deleteUser"),
    path("api/getinvited", userviews.getInvited, name="getInvited"),
    path("api/cancelinvite", userviews.cancelInvite, name="cancelInvite"),
    path("api/changeusername", userviews.changeUsername, name="changeUsername"),
    path("api/changepassword", userviews.changePassword, name="changePassword"),
    path("api/changeavatar", userviews.changeAvatar, name="changeAvatar"),
    path("api/getprofile", userviews.getProfile, name="getProfile"),
    path("api/changemotivation", userviews.changeMotivation,
         name="changeMotivation"),
    path("api/getresetpasswordemail", userviews.sendPasswordResetEmail,
         name="sendPasswordResetEmail"),
    path("api/resetpassword", userviews.resetPassword, name="resetPassword"),

    # exercises
    path("api/getexercise/<int:exercise_id>/",
         exerciseviews.get_exercise, name="getExercise"),
    path("api/setexercisepreferences/<int:exercise_id>/",
         exerciseviews.set_exercise_preferences,
         name="setExercisePreferences"),
    path("api/getexercisepreferences/<int:exercise_id>/",
         exerciseviews.get_exercise_preferences, name="getExercisePreferences"),
    path("api/getexerciselist", exerciseviews.get_all_exercises,
         name="getExerciseList"),
    path("api/getdoneexercises", exerciseviews.get_done_exercises,
         name="getdoneExercise"),
    path("api/getdoneexercisesinmonth", exerciseviews.get_done_exercises_in_month,
         name="getDoneExercisesInMonth"),

    # plans
    path("api/createplan", planviews.save_plan, name="createPlan"),
    path("api/addplantouser", planviews.add_plan_to_user,
         name="addExistingPlanToUser"),
    path("api/getplan/<int:plan_id>/", planviews.get_plan, name="getPlan"),
    path("api/getlistofplans", planviews.get_all_plans,
         name="getListOfPlans"),
    path("api/requestplanofuser", planviews.get_plan_of_user,
         name="getPlanOfUser"),
    path("api/deleteplan/<int:plan_id>",
         planviews.delete_plan, name="deletePlan"),

    # rating
    path("api/internal/rate", ratingview.rate, name="sendFeedback"),
]
