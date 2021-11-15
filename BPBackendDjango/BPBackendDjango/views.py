from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

class TesView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'irgendwas': 'schreiben',
            'irgendwasanderes': 'manBinIchLustig'
        }
        return Response(data)
