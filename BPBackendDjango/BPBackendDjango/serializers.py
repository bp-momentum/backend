from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'password', 'trainer'
        )



class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'password'
        )


class CreateTrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = (
            'first_name', 'last_name', 'username', 'password'
        )



class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'password'
        )

