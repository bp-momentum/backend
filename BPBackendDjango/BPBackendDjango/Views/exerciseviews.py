import math
import time

from rest_framework.views import APIView
from rest_framework.response import Response

from ..Helperclasses.ai import DummyAI
from ..models import DoneExercises, Exercise, ExerciseInPlan, Leaderboard, User
from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import DateHandler, ErrorHandler, ExerciseHandler, LanguageHandler

MAX_POINTS = 100


class GetExerciseView(APIView):
    def post(self, request, *args, **kwargs):
        #checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, ['id'], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        info = token['info']
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)
        
        #check if requested exercise exists
        if not Exercise.objects.filter(id=int(req_data['id'])).exists():
            data = {
                'success': False,
                'description': 'no exercise with this id exists',
                'data': {}
            }

            return Response(data)

        #check if user is allowed to request
        if not (token["info"]["account_type"] == "trainer" or token["info"]["account_type"] == "user"):
            data = {
                'success': False,
                'description': 'Not allowed to request list of exercises',
                'data': {}
                }
            return Response(data)

        #get exercise
        ex:Exercise = Exercise.objects.get(id=int(req_data['id']))

        #checks wether exercise is activated
        if not ex.activated:
            data = {
                'success': True,
                'description': 'Be careful, exercise is deactivated! Returned data',
                'data': {
                    'title': ex.title,
                    'description': LanguageHandler.get_in_correct_language(info['username'], ex.description),
                    'video': ex.video,
                    'activated': False
                }
            }

            return Response(data)
            
        data = {
                'success': True,
                'description': 'Returned data',
                'data': {
                    'title': ex.title,
                    'description': LanguageHandler.get_in_correct_language(info['username'], ex.description),
                    'video': ex.video,
                    'activated': True
                }
        }

        return Response(data)


class GetExerciseListView(APIView):
    def get(self, request, *args, **kwargs):
        #checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, [], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        info = token['info']
        #only trainers can request all exercises
        if not info['account_type'] == 'trainer':
            data = {
                'success': False,
                'description': 'you are not allow to request all exercises',
                'data': {}
                }
            return Response(data)

        #get all exercises as list
        exercises = Exercise.objects.all()
        exs_res = []
        #get all ids as list
        for ex in exercises:
            exs_res.append({
                'id': ex.id,
                'title': ex.title
                })

        data = {
                'success': True,
                'description': 'returning all exercises',
                'data': {
                    'exercises': exs_res
                }
        }

        return Response(data)


class DoneExerciseView(APIView):

    def post(self, request, *args, **kwargs):
        #checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, ['exercise_plan_id'], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        info = token['info']
        #check if is user/user exists
        if not User.objects.filter(username=info['username']).exists():
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
            }
            return Response(data)

        user:User = User.objects.get(username=info['username'])

        #check if exercise in plan with given id exists
        if not ExerciseInPlan.objects.filter(id=req_data['exercise_plan_id']).exists():
            data = {
                'success': False,
                'description': 'Exercise in plan id does not exists',
                'data': {}
            }
            return Response(data)
        eip:ExerciseInPlan = ExerciseInPlan.objects.get(id=req_data['exercise_plan_id'])

        # check if its already done this week
        done = DoneExercises.objects.filter(exercise=eip, user=user)
        for d in done:
            # calculate the timespan and if its already done done
            if time.time() - (d.date - d.date%86400) < 604800:
                data = {
                    'success': False,
                    'description': 'User already did this exercise in this week',
                    'data': {}
                }
                return Response(data)

        # calculating points
        a, b, c = DummyAI.dummy_function(ex=eip.exercise.id, video=None)
        intensity = b['intensity']
        speed = b['speed']
        cleanliness = b['cleanliness']

        points = int(math.ceil((intensity + speed + cleanliness) / 3))
        leaderboard_entry:Leaderboard = Leaderboard.objects.get(user=user)
        leaderboard_entry.score += points
        leaderboard_entry.save(force_update=True)
        # creating the new DoneExercise entry
        new_entry = DoneExercises(exercise=eip, user=user, points=points, date=int(time.time()))
        new_entry.save()
        data = {
            'success': True,
            'description': 'Done Exercise is now saved',
            'data': {}
        }

        return Response(data)


class GetDoneExercisesView(APIView):

    def get(self, request, *args, **kwargs):
        #checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, [], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        #check session token
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        info = token['info']
        if not User.objects.filter(username=info['username']).exists():
            data = {
                'success': False,
                'description': 'Non existing user',
                'data': {}
            }
            return Response(data)
        user:User = User.objects.get(username=info['username'])

        if user.plan is None:
            data = {
                'success': False,
                'description': 'User has no plan assigned',
                'data': {}
            }
            return Response(data)

        #create data in form of get plan
        data = ExerciseHandler.get_done(user=user)
        return Response(data)

    def post(self, request, *args, **kwargs):
        #checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, ['user'], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        req_data = dict(request.data)
        #check session token
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        # security: only trainer and admin can access other users data
        if not (token["info"]["account_type"] in ["trainer", "admin"]):
            data = {
                'success': False,
                'description': 'type of account is not allowed to access other users data',
                'data': {}
            }
            return Response(data)

        if not User.objects.filter(username=req_data['user']).exists():
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
            }
            return Response(data)
        user:User = User.objects.get(username=req_data['user'])
        data = ExerciseHandler.get_done(user=user)
        return Response(data)


class GetDoneExercisesOfMonthView(APIView):

    def post(self, request, *args, **kwargs):
        #checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, ['month', 'year'], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        req_data = dict(request.data)
        #check session token
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)
        info = token['info']
        if info['account_type'] == 'user':
            user:User = User.objects.get(username=info['username'])
        else:
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
            }
            return Response(data)
        if not DateHandler.valid_month(month=req_data['month']):
            data = {
                'success': False,
                'description': 'invalid month',
                'data': {}
            }
            return Response(data)
        done = ExerciseHandler.get_done_exercises_of_month(int(req_data['month']), int(req_data['year']), user)
        data = {
            'success': True,
            'description': 'Returning exercises done in this month',
            'data': {
                'done': done
            }
        }
        return Response(data)