from ..Helperclasses.ai import AIInterface
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from ..Helperclasses.jwttoken import JwToken

class AIView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_new_user_token(request.headers["Session-Token"])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)
        res = AIInterface.call_ai(req_data['exercise'], req_data['video'], token['info']['username'])
        data = {
                'success': True,
                'description': 'Result available',
                'data': {
                    'results': res
                }
        }
        return Response(data)