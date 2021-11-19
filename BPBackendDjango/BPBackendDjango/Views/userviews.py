from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken
import hashlib

from ..serializers import *
from ..models import *

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        req_data['password'] = str(hashlib.sha3_256(req_data['password'].encode('utf8')).hexdigest())
        serializer = RegisterSerializer(data=req_data)
        print(req_data)
        #hashing password
        if serializer.is_valid():
            #check if username already exists
            if not User.objects.filter(username=request.data['username']).exists():
                #save User in the databank
                serializer.save()
                #creating the session_token
                session_token = JwToken.create_session_token(req_data['username'])
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






