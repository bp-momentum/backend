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