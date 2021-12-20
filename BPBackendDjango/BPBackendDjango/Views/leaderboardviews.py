import math

from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..Helperclasses.jwttoken import JwToken


class ListLeaderboard(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token['valid']:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            Response(data)

        info = token['info']
        if not info['account_type'] == "user":
            data = {
                'success': False,
                'description': 'Only users can access the leaderboard',
                'data': {}
            }
            Response(data)

        leaderboard = Leaderboard.objects.order_by("-score")
        out = []
        rank = 0
        count_of_entries = req_data['count']

        # they are just as many entries as requested
        if len(leaderboard) <= count_of_entries:
            for l in leaderboard:
                rank += 1
                entry = {"rank": rank, "username": l.user.username, "score": l.score}
                out.append(entry)


        user_index = 0
        for entry in leaderboard:
            if entry.user.username == info['username']:
                break
            else:
                user_index += 1

        count_entries = len(leaderboard)
        # user is in top count_of_series
        if user_index < math.floor(count_of_entries/2):
            for l in range(0, count_of_entries):
                if l >= count_entries:
                    break
                rank += 1
                entry = {"rank": rank, "username": leaderboard[l].user.username, "score": leaderboard[l].score}
                out.append(entry)



        # user in bottom count_of_series
        elif user_index > count_entries - math.ceil(count_of_entries/2):
            rank = count_entries - count_of_entries
            for l in range(count_entries - count_of_entries, count_entries):
                if l < 0:
                    continue
                rank += 1
                entry = {"rank": rank, "username": leaderboard[l].user.username, "score": leaderboard[l].score}
                out.append(entry)

        else:
            for l in range(user_index - math.floor(count_of_entries/2), user_index + math.ceil(count_entries/2)):
                rank += 1
                entry = {"rank": rank, "username": leaderboard[l].user.username, "score": leaderboard[l].score}
                out.append(entry)



        data = {
            'success': True,
            'description': 'The Leaderboard got listed',
            'data': {
                'leaderboard': out
                }
            }

        return Response(data)
