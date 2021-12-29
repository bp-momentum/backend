from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken

from ..serializers import AchieveAchievement
from ..models import *
from exerciseviews import MAX_POINTS

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
        nr_unachieved_hidden = 0

        #iterate over all existing achievements
        for achievement in Achievment.objects.all():
            #do excersises
            if achievement.name == 'doneExercises':
                nr_of_exs = len(DoneExercises.objects.filter(user=user.id))
                if nr_of_exs >= 100:
                    upgrade_level(user.id, 'doneExercises', 3)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 3,
                        'progress': 'done',
                        'hidden': achievement.hidden
                    }) 
                elif nr_of_exs >= 50:
                    upgrade_level(user.id, 'doneExercises', 2)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 2,
                        'progress': str(nr_of_exs)+'/100',
                        'hidden': achievement.hidden
                    }) 
                elif nr_of_exs >= 10:
                    achieve_achievement(user.id, 'doneExercises')
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 1,
                        'progress': str(nr_of_exs)+'/50',
                        'hidden': achievement.hidden
                    }) 
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 0,
                        'progress': str(nr_of_exs)+'/10',
                        'hidden': achievement.hidden
                    })
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #make a friend
            elif achievement.name == 'havingFriends':
                nr_of_friends = len(Friends.objects.filter(friend1=user.id).union(Friends.objects.filter(friend2=user.id)))
                if nr_of_friends >= 1:
                    achieve_achievement(user.id, 'havingFriends')
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden
                    }) 
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 0,
                        'progress': '0/1',
                        'hidden': achievement.hidden
                    }) 
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #streak
            elif achievement.name == 'streak':
                streak = user.streak
                if streak >= 90:
                    achieve_achievement(user.id, 'streak')
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 4,
                        'progress': 'done',
                        'hidden': achievement.hidden
                    }) 
                elif streak >= 30:
                    achieve_achievement(user.id, 'streak')
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 3,
                        'progress': str(streak)+'/90',
                        'hidden': achievement.hidden
                    }) 
                elif streak >= 7:
                    achieve_achievement(user.id, 'streak')
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 2,
                        'progress': str(streak)+'/30',
                        'hidden': achievement.hidden
                    }) 
                elif streak >= 3:
                    achieve_achievement(user.id, 'streak')
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 1,
                        'progress': str(streak)+'/7',
                        'hidden': achievement.hidden
                    }) 
                elif not achievement.hidden:
                    achieve_achievement(user.id, 'streak')
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 0,
                        'progress': str(streak)+'/3',
                        'hidden': achievement.hidden
                    }) 
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #perfectExercise
            elif achievement.name == 'perfectExercise':
                found = False
                all = DoneExercises.objects.filter(user=user)
                for a in all:
                    if a.points == MAX_POINTS:
                        found = True
                        break
                if found:
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden
                    })
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 0,
                        'progress': '0/1',
                        'hidden': achievement.hidden
                    })
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1

        data = {
            'success': True,
            'description': 'Returning achievements',
            'data': {
                'achievements': achieved,
                'nr_unachieved_hidden': nr_unachieved_hidden
                }
            }
        return Response(data)