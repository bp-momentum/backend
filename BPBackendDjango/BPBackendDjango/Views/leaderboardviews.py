import math
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import *
from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import ErrorHandler


def build_entry(index, leaderboard, rank, is_trainer, username):
    exs_to_do = 0
    user = leaderboard[index].user
    if user.plan is not None:
        plan_data = ExerciseInPlan.objects.filter(plan=user.plan.id)
        for ex in plan_data:
            exs_to_do += ex.repeats_per_set * ex.sets
    execs_done = leaderboard[index].executions
    score = 0 if execs_done == 0 or exs_to_do == 0 else leaderboard[index].score
    speed = 0 if execs_done == 0 or exs_to_do == 0 else leaderboard[index].speed / execs_done
    intensity = 0 if execs_done == 0 or exs_to_do == 0 else leaderboard[index].intensity / execs_done
    cleanliness = 0 if execs_done == 0 or exs_to_do == 0 else leaderboard[index].cleanliness / execs_done
    show_real_name = is_trainer and username == user.trainer.username

    return {"rank": rank, "username": user.first_name + " " + user.last_name if show_real_name else user.username,
            "score": score,
            "speed": speed,
            "intensity": intensity,
            "cleanliness": cleanliness}


class ListLeaderboardView(APIView):

    def post(self, request, *args, **kwargs):
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
                entry = build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
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
                entry = build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

        # user is in top count_of_series
        elif user_index < math.floor(count_of_entries / 2):
            for i in range(0, count_of_entries):
                if i >= count_entries:
                    break
                rank += 1
                entry = build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

        # user in bottom count_of_series
        elif user_index > count_entries - math.ceil(count_of_entries / 2):
            rank = count_entries - count_of_entries
            for i in range(count_entries - count_of_entries, count_entries):
                if i < 0:
                    continue
                rank += 1
                entry = build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
                                    username=username)
                out.append(entry)

        else:
            for i in range(user_index - math.floor(count_of_entries / 2), user_index + math.ceil(count_of_entries / 2)):
                rank += 1
                entry = build_entry(index=i, leaderboard=leaderboard, rank=rank, is_trainer=is_trainer,
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
