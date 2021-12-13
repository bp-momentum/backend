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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/createuser', CreateUserView.as_view(), name='createNewUser'),
    path('api/register', RegisterView.as_view(), name='register'),
    path('api/login', LoginView.as_view(), name='login'),
    path('api/auth', AuthView.as_view(), name='authenticateWithToken'),
    path('api/logoutdevices', LogoutAllDevicesView.as_view(), name='logoutAllDevices'),
<<<<<<< HEAD
    path('api/deleteuser', DeleteAccountView.as_view(), name='deleteUser')
=======
    path('api/getexercise', GetExerciseView.as_view(), name='getExercise'),
    path('api/getexerciselist', GetExerciseListView.as_view(), name='getExerciseList')
>>>>>>> main
]
