from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *

class GetExerciseView(APIView):
    def get(self, request, *args, **kwargs):
        req_data = dict(request.data)
        if not Exercise.objects.filter(title=req_data['title']).exists():
            data = {
                'success': False,
                'description': 'Es existiert keine Übung mit diesem Titel',
                'data': {}
            }

            return Response(data)

        ex = Exercise.objects.get(title=req_data['title'])

        if not ex.activated:
            data = {
                'success': False,
                'description': 'Achtung Übung ist zur Zeit deaktiviert! Übungsdaten zurückgegeben',
                'data': {
                    'title': ex.title,
                    'description': ex.description,
                    'video': ex.viedo
                }
            }

            return Response(data)
        data = {
                'success': True,
                'description': 'Übungsdaten zurückgegeben',
                'data': {
                    'title': ex.title,
                    'description': ex.description,
                    'video': ex.viedo
                }
        }

        return Response(data)