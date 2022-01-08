from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken

from ..models import Friends
from ..models import User
from ..serializers import CreateFriends

def get_friends(user):
    sql = list(Friends.objects.filter(friend1=user, accepted=True))
    sql.append(list(Friends.objects.filter(friend2=user, accepted=True)))
    res = []
    for f in sql:
        res.append({
            'id': f.id,
            'friend1': f.friend1,
            'friend2': f.friend2
        })
    return res

def get_requests(user):
    sql = list(Friends.objects.filter(friend2=user, accepted=False))
    res = []
    for f in sql:
        res.append({
            'id': f.id,
            'friend1': f.friend1,
            'friend2': f.friend2
        })
    return res

def get_pending_requests(user):
    sql =  list(Friends.objects.filter(friend1=user, accepted=False))
    res = []
    for f in sql:
        res.append({
            'id': f.id,
            'friend1': f.friend1,
            'friend2': f.friend2
        })
    return res


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


class GetPendingRequestView(APIView):

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
        pending = get_pending_requests(user.id)
        data = {
                'success': True,
                'description': 'returning pending requests',
                'data': {
                    'pending': pending
                }
            }
        return Response(data)
    

class GetRequestView(APIView):

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
        requests = get_requests(user.id)
        data = {
                'success': True,
                'description': 'returning requests',
                'data': {
                    'requests': requests
                }
            }
        return Response(data)


class AddFriendView(APIView):

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

        #must be user
        if not User.objects.filter(username=info['username']).exists():
            data = {
                    'success': False,
                    'description': 'Not a user',
                    'data': {}
                }
            return Response(data)

        #added must be user/exist
        if not User.objects.filter(username=req_data['username']).exists():
            data = {
                    'success': False,
                    'description': 'Does not exist or is not a user',
                    'data': {}
                }
            return Response(data)

        is_from = User.objects.get(username=info['username'])
        is_to = User.objects.get(username=req_data['username'])
        request_data = {
            'friend1': is_from.id,
            'friend2': is_to.id
        }
        serializer = CreateFriends(data=request_data)
        if not serializer.is_valid():
            data = {
                    'success': False,
                    'description': 'invalid data',
                    'data': {}
                }
            return Response(data)

        serializer.save()
        data = {
                'success': True,
                'description': 'Request sent',
                'data': {}
            }
        return Response(data)


class AcceptRequestView(APIView):
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

        #must be user
        if not User.objects.filter(username=info['username']).exists():
            data = {
                    'success': False,
                    'description': 'Not a user',
                    'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])

        #check if request exists
        if not Friends.objects.filter(id=int(req_data['id']), friend2=user.id, accepted=False).exists():
            data = {
                    'success': False,
                    'description': 'Invalid request',
                    'data': {}
                }
            return Response(data)

        friend = Friends.objects.get(id=int(req_data['id']))
        friend.accepted = True
        friend.save()
        data = {
                'success': True,
                'description': 'Request accepted',
                'data': {}
            }
        return Response(data)


class DeclineRequestView(APIView):
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

        #must be user
        if not User.objects.filter(username=info['username']).exists():
            data = {
                    'success': False,
                    'description': 'Not a user',
                    'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])

        #check if request exists
        if not Friends.objects.filter(id=int(req_data['id']), friend2=user.id, accepted=False).exists():
            data = {
                    'success': False,
                    'description': 'Invalid request',
                    'data': {}
                }
            return Response(data)

        Friends.objects.filter(id=int(req_data['id']), accepted=False).delete()
        data = {
                'success': True,
                'description': 'Request decliened',
                'data': {}
            }
        return Response(data)


class DeleteFriendView(APIView):
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

        #must be user
        if not User.objects.filter(username=info['username']).exists():
            data = {
                    'success': False,
                    'description': 'Not a user',
                    'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])

        #check if request exists
        if not (Friends.objects.filter(id=int(req_data['id']), friend2=user.id).exists() or Friends.objects.filter(id=int(req_data['id']), friend1=user.id).exists()):
            data = {
                    'success': False,
                    'description': 'Invalid request',
                    'data': {}
                }
            return Response(data)

        f = Friends.objects.get(id=int(req_data['id']))
        removed_friend = f.friend1
        if removed_friend.id == user.id:
            removed_friend = f.friend2
        Friends.objects.filter(id=int(req_data['id'])).delete()

        data = {
                'success': True,
                'description': 'Removed friend',
                'data': {
                    'removed_friend': removed_friend
                }
            }
        return Response(data)