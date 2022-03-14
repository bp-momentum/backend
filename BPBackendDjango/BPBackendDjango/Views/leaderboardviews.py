import math

from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Leaderboard
from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import ErrorHandler, LeaderboardHandler


class ListLeaderboardView(APIView):

    def post(self, request, *args, **kwargs):

        # check if leaderboard already got resetted in this week

        LeaderboardHandler.reset_leaderboard()


        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, ['count'], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token['valid']:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        info = token['info']
        leaderboard = Leaderboard.objects.order_by("-score")
        out = []
        rank = 0
        count_of_entries = req_data['count']
        count_entries = len(leaderboard)
        user_index = 0
        is_trainer = info["account_type"] == "trainer"
        username = info["username"]

        if not info['account_type'] == "user":
            for i in range(0, count_of_entries):
                if i >= count_entries:
                    continue
                rank += 1
                entry = LeaderboardHandler.build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

            data = {
                'success': True,
                'description': 'Got the top count of users',
                'data': {
                    "leaderboard": out
                }
            }
            return Response(data)

        for entry in leaderboard:
            if entry.user.username == info['username']:
                break
            else:
                user_index += 1

        # they are just as many entries as requested
        if len(leaderboard) <= count_of_entries:
            for i in range(len(leaderboard)):
                rank += 1
                entry = LeaderboardHandler.build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

        # user is in top count_of_series
        elif user_index < math.floor(count_of_entries / 2):
            for i in range(0, count_of_entries):
                if i >= count_entries:
                    break
                rank += 1
                entry = LeaderboardHandler.build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

        # user in bottom count_of_series
        elif user_index > count_entries - math.ceil(count_of_entries / 2):
            rank = count_entries - count_of_entries
            for i in range(count_entries - count_of_entries, count_entries):
                if i < 0:
                    continue
                rank += 1
                entry = LeaderboardHandler.build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

        else:
            for i in range(user_index - math.floor(count_of_entries / 2), user_index + math.ceil(count_of_entries / 2)):
                rank += 1
                entry = LeaderboardHandler.build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

        data = {
            'success': True,
            'description': 'The Leaderboard got listed',
            'data': {
                'leaderboard': out
            }
        }

        return Response(data)
