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

class GetExerciseView(APIView):
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
                'success': True,
                'description': 'Achtung Übung ist zur Zeit deaktiviert! Übungsdaten zurückgegeben',
                'data': {
                    'title': ex.title,
                    'description': ex.description,
                    'video': ex.video,
                    'activated': False
                }
            }

            return Response(data)
        data = {
                'success': True,
                'description': 'Übungsdaten zurückgegeben',
                'data': {
                    'title': ex.title,
                    'description': ex.description,
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
            exercises.append({
                'id': ex.id,
                'title': ex.title
                })
        data = {
                'success': True,
                'description': 'returning all exercises',
                'data': {
                    'plans': exs_res
                }
        }
        return Response(data)