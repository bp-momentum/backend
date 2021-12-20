from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..Helperclasses.jwttoken import JwToken


class ListLeaderboard(APIView):
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

        leaderboard = Leaderboard.objects.order_by("-score")
        out = []
        for l in leaderboard:
            entry = {"username": l.user.username, "score": l.score}
            out.append(entry)

        data = {
            'success': True,
            'description': 'The Leaderboard got listed',
            'data': {
                'leaderboard': out
                }
            }

        return Response(data)
