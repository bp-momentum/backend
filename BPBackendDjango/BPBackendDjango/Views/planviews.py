from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..Helperclasses.jwttoken import JwToken

def add_plan_to_user(username, plan):
    #checks if user exists
    if not User.objects.filter(username=username).exists():
        return "user_invalid"
    #checks if plan exists
    if not TrainingSchedule.objects.filter(id=plan).exists():
        return "plan_invalid"
    #assign plan to user
    user = User.objects.get(username=username)
    ts = TrainingSchedule.objects.get(id=plan)
    user.plan = ts
    return "success"

def create_plan(trainer, date, sets, rps, exercise):
    #create plan
    data = {
        'trainer': trainer
    }
    new_plan = CreatePlan(data=data)
    #check if plan is valid
    if new_plan.is_valid():
        plan = new_plan.save()
    else:
        return "invalid", new_plan.errors
    #create plan data
    data = {
        'date': date,
        'sets': sets,
        'repeats_per_set': rps,
        'exercise': exercise,
        'plan': plan
    }
    new_data = CreateExerciseInPlan(data=data)
    #check if plan data is valid
    if new_data.is_valid():
        new_data.save()
        return "valid", plan
    return "invalid", new_data.errors


class CreatePlanView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        req_data = request.data
        token = JwToken.check_session_token(request.headers['Session-Token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        #check if user is allowed to request
        if not token["info"]["account_type"] == "trainer":
            data = {
                'success': False,
                'description': 'Not allowed to add trainig schedule',
                'data': {}
                }
            return Response(data)

        #checks if trainer exists
        if not Trainer.objects.filter(username=token['info']['username']).exists():
            data = {
                'success': False,
                'description': 'no valid trainer',
                'data': {}
                }

            return Response(data)

        
        #check if exercise is valid
        if not Exercise.objects.filter(id=int(req_data['exercise'])).exists():
            data = {
                'success': False,
                'description': 'no valid exercise',
                'data': {}
                }

            return Response(data)

        #create plan and data
        trainer = Trainer.objects.get(username=token['info']['username'])
        plan = create_plan(trainer, req_data['date'], int(req_data['sets']), int(req_data['repeats_per_set']), int(req_data['exercise']))
        if plan[0] == "invalid":
            return Response(plan[1])

        #assign plan to user
        res = add_plan_to_user(username=req_data['user'], plan=plan.id)

        #checks whether assigning was successful
        if res == "user_invalid":
            data = {
                'success': False,
                'description': 'plan was created but could not be assigned to user',
                'data': {
                    'plan_id': plan.id
                }
            }
        #should not happen, needed for other view
        elif res == "plan_invalid":
            data = {
                'success': False,
                'description': 'plan created,  but does not exist',
                'data': {
                    'plan_id': plan.id
                }
            }
        else:
            data = {
                    'success': True,
                    'description': 'plan created',
                    'data': {
                        'plan_id': plan.id
                    }
            }

        return Response(data)


class AddPlanToUserView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        req_data = request.data
        token = JwToken.check_session_token(request.headers['Session-Token'])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)

        #check if user is allowed to request
        if not token["info"]["account_type"] == "trainer":
            data = {
                'success': False,
                'description': 'Not allowed to request list of exercises',
                'data': {}
                }
            return Response(data)

        #assign plan to user
        res = add_plan_to_user(username=req_data['user'], plan=int(req_data['plan']))

        #checks whether assigning was successful
        if res == "user_invalid":
            data = {
                'success': False,
                'description': 'invalid user',
                'data': {}
            }
        elif res == "plan_invalid":
            data = {
                'success': False,
                'description': 'plan does not exist',
                'data': {}
            }
        else:
            data = {
                    'success': True,
                    'description': 'plan assigned to user',
                    'data': {}
            }

        return Response(data)
        