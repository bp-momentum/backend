from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer
from .models import User

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




