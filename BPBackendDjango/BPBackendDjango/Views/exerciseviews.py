import time

from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..Helperclasses.jwttoken import JwToken

def user_needs_ex(username, id):
    #TODO user needs exercise
    return True


class GetExerciseView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
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
        if not (token["info"]["account_type"] == "trainer" or (token["info"]["account_type"] == "user" and user_needs_ex(token["info"]['username'], int(req_data['id'])))):
            data = {
                'success': False,
                'description': 'Not allowed to request list of exercises',
                'data': {}
                }
            return Response(data)

        #get exercise
        ex = Exercise.objects.get(id=int(req_data['id']))

        #checks wether exercise is activated
        if not ex.activated:
            data = {
                'success': True,
                'description': 'Be careful, exercise is deactivated! Returned data',
                'data': {
                    'title': ex.title,
                    'description': ex.description,
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
                    'description': ex.description,
                    'video': ex.video,
                    'activated': True
                }
        }

        return Response(data)


class GetExerciseListView(APIView):
    def get(self, request, *args, **kwargs):
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
        user = User.objects.get(username=info['username'])
        eip = ExerciseInPlan.objects.get(id=req_data['exercise_plan_id'])

        ## check if its alrady done this week
        done = DoneExercises.objects.filter(exercise=eip, user=user)
        for d in done:
            if time.time() - (d.date - d.date%86400) < 604800:
                data = {
                    'success': False,
                    'description': 'User already did this exercise in this week',
                    'data': {}
                }
                return Response(data)


        new_entry = DoneExercises(exercise=eip, user=user, points=0, date=int(time.time()))
        new_entry.save()
        data = {
            'success': True,
            'description': 'Done Exercise is now saved',
            'data': {}
        }

        return Response(data)

class GetDoneExercisesView(APIView):
    def GetDone(self, username):
        ## list of all done in last week
        done = DoneExercises.objects.filter(user=user, date__gt=time.time() + 86400 - time.time() % 86400 - 604800)

        all = ExerciseInPlan.objects.filter(plan=user.plan)
        out = []
        for a in all:
            for d in done:
                if a.id == d.plan.id:
                    out.append({"exercise_plan_id": a.id,
                                "id": a.exercise,
                                "date": a.date,
                                "sets": a.sets,
                                "repeats_per_set": a.repeats_per_set,
                                "done": True
                                })
                    break

            out.append({"exercise_plan_id": a.id,
                        "id": a.exercise,
                        "date": a.date,
                        "sets": a.sets,
                        "repeats_per_set": a.repeats_per_set,
                        "done": False
                        })

        data = {
            "success": True,
            "description": "Returned list of Exercises and if its done",
            "data": out
        }

        return data


    def get(self, request, *args, **kwargs):
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        info = token['info']
        user = User.objects.get(username=info['username'])

        data = self.GetDone(user)
        return Response(data)

    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers['Session-Token'])
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
            }
            return Response(data)

        if not (token["info"]["account_type"] in ["trainer", "admin"]):
            data = {
                'success': False,
                'description': 'type of account is not allowed to access other users data',
                'data': {}
            }
            return Response(data)

        data = self.GetDone(req_data['user'])
        return Response(data)










