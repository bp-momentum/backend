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

def create_plan():
    new_plan = ""
    new_data = ""


class createPlanView(APIView):
    def post(self, request, *args, **kwargs):
        req_data = dict(request.data)
        req_data = request.data
        token = JwToken.check_session_token(request.headers["Session-Token"])["info"]

        if not token["account_type"] == "trainer":
            data = {
                'success': False,
                'description': 'account type is not allowed to add training schedules',
                'data': {}
                }

            return Response(data)

        