from rest_framework import serializers
from .models import *

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'password', 'email_address', 'trainer_id'
        )


class CreateTrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = (
            'first_name', 'last_name', 'username', 'password', 'email_address'
        )



class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'password'
        )

