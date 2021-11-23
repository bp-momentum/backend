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
        print(req_data)
        token = JwToken.check_session_token(req_data['session_token'])
        req_data.pop("session_token")
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': 'False',
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        #check account type
        
        if token["info"]["account_type"] == "trainer":
            serializer = CreateUserSerializer(data=req_data)
            account_type = "user"
        
        elif token["info"]["account_type"] == "admin":
            serializer = CreateUserSerializer(data=req_data)
            account_type ="trainer"
        else:
            data = {
                'success': 'False',
                'description': 'account type cannot create a new account',
                'data': {}
                }
            return Response(data)

        
        #trainer creates new User

        if serializer.is_valid():
            #check if username already exists
            if (not User.objects.filter(username=request.data['username']).exists() and
                not Trainer.objects.filter(username=request.data['username']).exists() and 
                not Admin.objects.filter(username=request.data['username']).exists()):
                
                #save User in the databank
                serializer.save()
                #creating the session_token
                data = {
                'success': 'True',
                'description': 'User wurde erstellt',
                'data': {}
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

def check_password(username, passwd):
    passwd = str(hashlib.sha3_256(passwd.encode('utf8')).hexdigest())
    if User.objects.filter(username=username, password=passwd).exists():
        return "user"
    elif Trainer.objects.filter(username=username, password=passwd).exists():
        return "trainer"
    elif Admin.objects.filter(username=username, password=passwd).exists():
        return "admin"
    else:
        return "invalid"

class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        print(req_data)
        passcheck = check_password(req_data['username'], req_data['password'])
        if passcheck == "invalid":
            data = {
            'success': 'False',
            'description': 'Nutzerdaten sind Fehlerhaft',
            'data': {}
            }

            return Response(data)

        session_token = JwToken.create_session_token(req_data['username'], passcheck)
        data = {
            'success': 'True',
            'description': 'Nutzer ist nun eingeloggt',
            'data': {'session_token': session_token}
            }

        return Response(data)
        
            








