from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import *
from ..serializers import *
from ..Helperclasses.jwttoken import JwToken

def add_plan_to_user(username, plan):
    if not User.objects.filter(username=username).exists():
        return "user_invalid"
    if not TrainingSchedule.objects.filter(id=plan).exists():
        return "plan_invalid"
    user = User.objects.get(username=username)
    ts = TrainingSchedule.objects.get(id=plan)
    user.plan = ts
    return "success"

def create_plan(trainer, date, sets, rps, exercise):
    new_plan = CreatePlan(trainer=trainer)
    if new_plan.is_valid():
        plan = new_plan.save()
    else:
        return "invalid", new_plan.errors
    new_data = CreateExerciseInPlan(date=date, sets=sets, repeats_per_set=rps, exercise=exercise, plan=plan)
    if new_data.is_valid():
        new_data.save()
        return "valid", plan
    return "invalid", new_data.errors


class createPlanView(APIView):
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

        if not Trainer.objects.filter(username=token['username']).exists():
            data = {
                'success': False,
                'description': 'no valid trainer',
                'data': {}
                }

            return Response(data)

        trainer = Trainer.objects.get(username=token['username'])
        plan = create_plan(trainer, req_data['date'], int(req_data['sets']), int(req_data['repeats_per_set']), req_data['exercise'])
        if plan[0] == "invalid":
            return Response(plan[1])

        res = add_plan_to_user(username=req_data['user'], plan=plan.id)

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


class addPlanToUserView(APIView):
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

        res = add_plan_to_user(username=req_data['user'], plan=int(req_data['plan']))

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
        