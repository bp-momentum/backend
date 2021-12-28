from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken

from ..serializers import AchieveAchievement
from ..models import *

def achieve_achievement(user, achievement):
    if not Achievment.objects.filter(name=achievement).exists():
        return False, 'invalid achievement'
    if not User.objects.filter(id=user).exists():
        return False, 'invalid user'
    a = Achievment.objects.get(name=achievement)
    u = User.objects.get(id=user)
    data = {
        'achievement': a.id,
        'user': user.id
    }
    if UserAchievedAchievment.objects.filter(achievement=a.id, user=user.id).exists():
        return False, 'achievement already achieved'
    serializer = AchieveAchievement(data=data)
    if not serializer.is_valid():
        return False, 'new data not valid'
    serializer.save()
    return True, 'user achieved achievement'

def upgrade_level(user, achievement, level):
    if not Achievment.objects.filter(name=achievement).exists():
        return False, 'invalid achievement'
    if not User.objects.filter(id=user).exists():
        return False, 'invalid user'
    a = Achievment.objects.get(name=achievement)
    u = User.objects.get(id=user)
    if not UserAchievedAchievment.objects.filter(achievement=a.id, user=user.id).exists():
        res = achieve_achievement(user, achievement)
        if not res[0]:
            return res
    uaa = UserAchievedAchievment.objects.get(achievement=a.id,user=user.id)
    uaa.level = level
    uaa.save()
    return True, 'level upgraded'


class GetAchievementsView(APIView):
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

        if not User.objects.filter(username=info['username']).exists():
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])
        achieved = []

        #iterate over all existing achievements
        for achievement in Achievment.objects.all():
            if achievement.name == '':
                if True: #überprüfen der Bedingen zum erreichen
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'progress': 'done',
                        'hidden': achievement.hidden
                    }) #hinzufügen zur Liste


        data = {
            'success': True,
            'description': 'Returning achievements',
            'data': {
                'achievements': achieved
                }
            }
        return Response(data)