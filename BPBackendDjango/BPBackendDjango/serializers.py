from rest_framework import serializers
from .models import *

class UserSerializer(serialzers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'password', 'trainer'
        )