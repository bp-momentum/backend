from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *
from .models import *

class TesView(APIView):
    def get(self, request, *args, **kwargs):
        print("get get")
        data = {
            'irgendwas': 'schreiben',
            'irgendwasanderes': 'manBinIchLustig'
        }
        return Response(data)

    def post(self, request, *args, **kwargs):
        print("post post")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            user = None
            try:
                 user = User.objects.get(username=serializer.username)
            except user.DoesNotExist:
                #serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)






