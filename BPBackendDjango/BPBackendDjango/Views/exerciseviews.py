from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..Helperclasses.jwttoken import JwToken

class GetExerciseView(APIView):
    def get(self, request, *args, **kwargs):
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
        
        #check if requested exercise exists
        if not Exercise.objects.filter(title=req_data['title']).exists():
            data = {
                'success': False,
                'description': 'no exercise with this title exists',
                'data': {}
            }

            return Response(data)

        #get exercise
        ex = Exercise.objects.get(title=req_data['title'])

        #checks wether exercise is activated
        if not ex.activated:
            data = {
                'success': False,
                'description': 'Be careful, exercise is deactivated! Returned data',
                'data': {
                    'title': ex.title,
                    'description': ex.description,
                    'video': ex.video
                }
            }

            return Response(data)
            
        data = {
                'success': True,
                'description': 'Returned data',
                'data': {
                    'title': ex.title,
                    'description': ex.description,
                    'video': ex.video
                }
        }

        return Response(data)