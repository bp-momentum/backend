from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..Helperclasses.jwttoken import JwToken


class LoginView(APIView):

    def get(self, request, *args, **kwargs):
        req_data = dict(request.data)
        v, token = JwToken.check_session_token(request.headers['Session-Token'])
        if not v:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            Response(data)

        leaderboard = Leaderboard.filter()
        out = []
        for l in leaderboard:
            out.append(l.id)

        data = {
            'success': True,
            'description': 'User is logged in',
            'data': {
                'leaderboard': out
                }
            }

        return Response(data)
