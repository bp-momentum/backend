from rest_framework.views import APIView
from rest_framework.response import Response
import json

from ..models import *
from ..Helperclasses.jwttoken import JwToken

def user_needs_ex(username, id):
    #TODO user needs exercise
    return True

def get_correct_description(username, description):
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    elif Trainer.objects.filter(username=username).exists():
        user = Trainer.objects.get(username=username)
    elif Admin.objects.filter(username=username).exists():
        user = Admin.objects.get(username=username)
    else:
        return "invalid user"
    lang = user.language
    desc = json.loads(description)
    res = desc.get(lang)
    if res == None:
        return "description not available in "+lang
    return res


class GetExerciseView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        info = token['info']
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)
        
        #check if requested exercise exists
        if not Exercise.objects.filter(id=int(req_data['id'])).exists():
            data = {
                'success': False,
                'description': 'no exercise with this id exists',
                'data': {}
            }

            return Response(data)

        #check if user is allowed to request
        if not (token["info"]["account_type"] == "trainer" or (token["info"]["account_type"] == "user" and user_needs_ex(token["info"]['username'], int(req_data['id'])))):
            data = {
                'success': False,
                'description': 'Not allowed to request list of exercises',
                'data': {}
                }
            return Response(data)

        #get exercise
        ex = Exercise.objects.get(id=int(req_data['id']))

        #checks wether exercise is activated
        if not ex.activated:
            data = {
                'success': True,
                'description': 'Be careful, exercise is deactivated! Returned data',
                'data': {
                    'title': ex.title,
                    'description': get_correct_description(info['username'], ex.description),
                    'video': ex.video,
                    'activated': False
                }
            }

            return Response(data)
            
        data = {
                'success': True,
                'description': 'Returned data',
                'data': {
                    'title': ex.title,
                    'description': get_correct_description(info['username'], ex.description),
                    'video': ex.video,
                    'activated': True
                }
        }

        return Response(data)


class GetExerciseListView(APIView):
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
        #only trainers can request all exercises
        if not info['account_type'] == 'trainer':
            data = {
                'success': False,
                'description': 'you are not allow to request all exercises',
                'data': {}
                }
            return Response(data)

        #get all exercises as list
        exercises = Exercise.objects.all()
        exs_res = []
        #get all ids as list
        for ex in exercises:
            exs_res.append({
                'id': ex.id,
                'title': ex.title
                })
        data = {
                'success': True,
                'description': 'returning all exercises',
                'data': {
                    'exercises': exs_res
                }
        }

        return Response(data)