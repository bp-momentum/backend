from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken
import hashlib

from ..serializers import *
from ..models import *

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            #check if username already exists
            if not User.objects.filter(username=request.data['username']).exists():
                #hashing password
                serializer.fields['password'] = str(hashlib.sha3_256(request.data['password'].encode('utf8')).hexdigest())
                #save User in the databank
                serializer.save()
                #creating the session_token++
                session_token = JwToken.create_session_token(request.data['username'])
                data = {
                'success': 'True',
                'description': 'User wurde erstellt',
                'data': {'session_token': session_token}
                }

                return Response(data)
            else:
                data = {
                'success': 'False',
                'description': 'Username existiert bereits',
                'data': {}
                }

                return Response(data)

        return Response(serializer.errors)






