from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken

from ..models import *

def get_friends(user):
    res = list(Friends.objects.filter(friend1=user))
    res.append(list(Friends.objects.filter(friend2=user)))
    return res

def get_requests(user):
    return list(Friends.objects.filter(friend2=user, accepted=False))

def get_pending_requests(user):
    return list(Friends.objects.filter(friend1=user, accepted=False))

class GetMyFriendsView(APIView):

    def get(self, request, *args, **kwargs):
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

        #must be user
        if not User.objects.filter(username=info['username']).exists():
            data = {
                    'success': False,
                    'description': 'Not a user',
                    'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])
        friends = get_friends(user.id)
        data = {
                'success': True,
                'description': 'returning friends',
                'data': {
                    'friends': friends
                }
            }
        return Response(data)







