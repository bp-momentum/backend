from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ..Helperclasses.jwttoken import JwToken
import string
import random
import hashlib
import time

from ..serializers import *
from ..models import *
from BPBackendDjango.settings import *

#creating random password
from ..settings import EMAIL_HOST_USER


def get_random_password(length):
    letters = string.ascii_lowercase
    letters += string.ascii_uppercase
    letters += "0123456789"
    out = ''.join(random.choice(letters) for i in range(length))
    return out

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

#only method needs to be changed to get different information about users
def get_users_data(users):
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username
        })

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        req_data['password'] = str(hashlib.sha3_256(req_data["password"].encode('utf8')).hexdigest())
        token = JwToken.check_new_user_token(request.data['new_user_token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        #check account type
        req_data["first_name"] = token["info"]["first_name"]
        req_data["last_name"] = token["info"]["last_name"]
        req_data["email_address"] = token["info"]["email_address"]
        if token["info"]["create_account_type"] == "user":
            trainer_id = Trainer.objects.get(username=token["info"]["initiator"]).id
            req_data["trainer"] = trainer_id
            serializer = CreateUserSerializer(data=req_data)
        
        elif token["info"]["create_account_type"] == "trainer":
            serializer = CreateTrainerSerializer(data=req_data)

        else:
            data = {
                'success': False,
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
                
                
                # save User in the databank
                serializer.save()

                # add user to leaderboard with score of 0
                Leaderboard.objects.create(user=User.objects.get(username=request.data['username']), score=0)

                #creating the session_token
                session_token = JwToken.create_session_token(req_data['username'], token["info"]["create_account_type"])
                refresh_token = JwToken.create_refresh_token(req_data['username'], token["info"]["create_account_type"], True)
                data = {
                'success': True,
                'description': 'User was created',
                'data': {
                    "session_token": session_token,
                    "refresh_token": refresh_token
                }
                }

                return Response(data)
            else:
                data = {
                'success': False,
                'description': 'Username already exists',
                'data': {}
                }

                return Response(data)

        return Response(serializer.errors)


class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        info = JwToken.check_session_token(request.headers["Session-Token"])["info"]
        
        #check account type and create new-user-token
        if info["account_type"] == "admin":
            new_user_token = JwToken.create_new_user_token(info["username"], req_data["first_name"], req_data["last_name"], req_data["email_address"], "trainer")
        elif info["account_type"] == "trainer":
            new_user_token = JwToken.create_new_user_token(info["username"], req_data["first_name"], req_data["last_name"], req_data["email_address"], "user")
        else:
            data = {
                'success': False,
                'description': 'account type is not allowed to add new users',
                'data': {}
                }

            return Response(data)
        #create and send mail
        html_message = render_to_string('BPBackendDjango/registrationEmail.html', {'full_name': f' {req_data["first_name"]} {req_data["last_name"]}', "account_type": info["account_type"], "link": f'http://78.46.150.116/#/?new_user_token={new_user_token}'})
        plain_message = strip_tags(html_message)
        send_mail("BachelorPraktum Passwort",
                    plain_message,
                     EMAIL_HOST_USER, 
                     [req_data['email_address']], html_message=html_message)
        data = {
                'success': True,
                'description': 'email with invite was sent',
                'data': {
                    "new_user_token": new_user_token
                }
                }

        return Response(data)


class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        print(req_data)
        #check password
        passcheck = check_password(req_data['username'], req_data['password'])
        if passcheck == "invalid":
            data = {
            'success': False,
            'description': 'Data of user is invalid',
            'data': {}
            }

            return Response(data)

        #create session- and refresh-token
        session_token = JwToken.create_session_token(req_data['username'], passcheck)
        refresh_token = JwToken.create_refresh_token(req_data['username'], passcheck, False)
        data = {
            'success': True,
            'description': 'User is logged in',
            'data': {
                'session_token': session_token,
                'refresh_token': refresh_token
                }
            }

        return Response(data)
        


class LogoutAllDevicesView(APIView):

    def post(self, request, *args, **kqargs):
        token = JwToken.check_session_token(request.headers["Session-Token"])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        info = token["info"]
        #creates new password for refresh-token
        JwToken.save_refreshpswd(info['username'], JwToken.create_refreshpswd(info['username'], int(time.time())))
        JwToken.invalidate_session_token(info['username'])
        data = {
            'success': True,
            'description': 'refresh-token changed',
            'data': {}
            }

        return Response(data)


class AuthView(APIView):

    def post(self, request, *args, **kwargs):
        token = request.data['refresh_token']
        info = JwToken.check_refresh_token(token)
        #check if token is valid
        if not info['valid']:
            data = {
            'success': False,
            'description': 'refresh-token invalid',
            'data': {}
            }

            return Response(data)

        #create new tokens
        session_token = JwToken.create_session_token(username=info['info']['username'], account_type=info['info']['account_type'])
        refresh_token = JwToken.create_refresh_token(username=info['info']['username'], account_type=info['info']['account_type'], set_pswd=False)
        data = {
            'success': True,
            'description': 'user is now logged in',
            'data': {
                'session_token': session_token,
                'refresh-token': refresh_token
                }
            }

        return Response(data)


class DeleteAccountView(APIView):

    def post(self, request, *args, **kwargs):
        token = JwToken.check_session_token(request.headers['Session-Token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        info = token['info']

        #delete user
        if User.objects.filter(username=info['username']).exists():
            User.objects.filter(username=info['username']).delete()
        elif Trainer.objects.filter(username=info['username']).exists():
            Trainer.objects.filter(username=info['username']).delete()
        elif Admin.objects.filter(username=info['username']).exists():
            #admins can not be deleted
            data = {
            'success': False,
            'description': 'Admin account can not be deleted',
            'data': {}
            }

            return Response(data)
        else:
            data = {
            'success': False,
            'description': 'User not found',
            'data': {}
            }

            return Response(data)

        data = {
            'success': True,
            'description': 'User was successfully deleted',
            'data': {}
            }

        return Response(data)


class SearchUserView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        info = token['info']
        users = User.objects.filter(username__unaccent__icontains=req_data['search'])
        users_data = get_users_data(users)

        data = {
                'success': True,
                'description': 'returning list of matching users',
                'data': {
                    'users': users_data
                }
            }
        return Response(data)


class GetListOfUsers(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        users = User.objects.all()
        users_data = get_users_data(users)  

        data = {
                'success': True,
                'description': 'returning list of users',
                'data': {
                    'users': users_data
                }
            }
        return Response(data)

