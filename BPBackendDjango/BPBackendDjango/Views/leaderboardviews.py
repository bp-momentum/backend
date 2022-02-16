import math

from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import ErrorHandler


class ListLeaderboardView(APIView):



    def post(self, request, *args, **kwargs):
        #checking if it contains all arguments
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

        exs_to_do = 0


        if not info['account_type'] == "user":

            for l in range(0, count_of_entries):
                if l >= count_entries:
                    continue
                rank += 1
                plan_data = ExerciseInPlan.objects.filter(plan=leaderboard[l].user.plan.id)
                for ex in plan_data:
                    exs_to_do += ex.repeats_per_set * ex.sets
                execs_done = leaderboard[l].executions
                score = 0 if execs_done == 0 else (leaderboard[l].speed + leaderboard[l].intensity + leaderboard[l].cleanliness) / (3 * exs_to_do)
                speed = 0 if execs_done == 0 else leaderboard[l].speed / execs_done
                intensity = 0 if execs_done == 0 else leaderboard[l].intensity / execs_done
                cleanliness = 0 if execs_done == 0 else leaderboard[l].cleanliness / execs_done

                entry = {"rank": rank, "username": leaderboard[l].user.username,
                         "score": score,
                         "speed": speed,
                         "intensity": intensity,
                         "cleanliness": cleanliness}

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
            for l in leaderboard:
                rank += 1
                plan_data = ExerciseInPlan.objects.filter(plan=l.user.plan.id)
                for ex in plan_data:
                    exs_to_do += ex.repeats_per_set * ex.sets
                execs_done = l.executions
                score = 0 if execs_done == 0 else (l.speed + l.intensity + l.cleanliness) / (3 * exs_to_do)
                speed = 0 if execs_done == 0 else l.speed / execs_done
                intensity = 0 if execs_done == 0 else l.intensity / execs_done
                cleanliness = 0 if execs_done == 0 else l.cleanliness / execs_done

                entry = {"rank": rank, "username": l.user.username,
                         "score": score,
                         "speed": speed,
                         "intensity": intensity,
                         "cleanliness": cleanliness}
                out.append(entry)



        # user is in top count_of_series
        elif user_index < math.floor(count_of_entries/2):
            for l in range(0, count_of_entries):
                if l >= count_entries:
                    break
                rank += 1

                plan_data = ExerciseInPlan.objects.filter(plan=leaderboard[l].user.plan.id)
                for ex in plan_data:
                    exs_to_do += ex.repeats_per_set * ex.sets
                execs_done = leaderboard[l].executions
                score = 0 if execs_done == 0 else (leaderboard[l].speed + leaderboard[l].intensity + leaderboard[l].cleanliness) / (
                        3 * exs_to_do)
                speed = 0 if execs_done == 0 else leaderboard[l].speed / execs_done
                intensity = 0 if execs_done == 0 else leaderboard[l].intensity / execs_done
                cleanliness = 0 if execs_done == 0 else leaderboard[l].cleanliness / execs_done

                entry = {"rank": rank, "username": leaderboard[l].user.username,
                         "score": score,
                         "speed": speed,
                         "intensity": intensity,
                         "cleanliness": cleanliness}
                out.append(entry)

        # user in bottom count_of_series
        elif user_index > count_entries - math.ceil(count_of_entries/2):
            rank = count_entries - count_of_entries
            for l in range(count_entries - count_of_entries, count_entries):
                if l < 0:
                    continue
                rank += 1
                plan_data = ExerciseInPlan.objects.filter(plan=leaderboard[l].user.plan.id)
                for ex in plan_data:
                    exs_to_do += ex.repeats_per_set * ex.sets
                execs_done = leaderboard[l].executions
                score = 0 if execs_done == 0 else (leaderboard[l].speed + leaderboard[l].intensity + leaderboard[l].cleanliness) / (
                                                          3 * exs_to_do)
                speed = 0 if execs_done == 0 else leaderboard[l].speed / execs_done
                intensity = 0 if execs_done == 0 else leaderboard[l].intensity / execs_done
                cleanliness = 0 if execs_done == 0 else leaderboard[l].cleanliness / execs_done

                entry = {"rank": rank, "username": leaderboard[l].user.username,
                         "score": score,
                         "speed": speed,
                         "intensity": intensity,
                         "cleanliness": cleanliness}
                out.append(entry)

        else:
            for l in range(user_index - math.floor(count_of_entries/2), user_index + math.ceil(count_of_entries/2)):
                plan_data = ExerciseInPlan.objects.filter(plan=leaderboard[l].user.plan.id)
                for ex in plan_data:
                    exs_to_do += ex.repeats_per_set * ex.sets
                execs_done = leaderboard[l].executions
                score = 0 if execs_done == 0 else (leaderboard[l].speed + leaderboard[l].intensity + leaderboard[l].cleanliness) / (
                                                          3 * exs_to_do)
                speed = 0 if execs_done == 0 else leaderboard[l].speed / execs_done
                intensity = 0 if execs_done == 0 else leaderboard[l].intensity / execs_done
                cleanliness = 0 if execs_done == 0 else leaderboard[l].cleanliness / execs_done

                entry = {"rank": rank, "username": leaderboard[l].user.username,
                         "score": score,
                         "speed": speed,
                         "intensity": intensity,
                         "cleanliness": cleanliness}
                out.append(entry)



        data = {
            'success': True,
            'description': 'The Leaderboard got listed',
            'data': {
                'leaderboard': out
                }
            }

        return Response(data)
