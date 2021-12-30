from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken

from ..serializers import AchieveAchievement
from ..models import *
from exerciseviews import MAX_POINTS

NIGHT_START = 22*84600
NIGHT_END = 6*84600
EARLY_END = 8*84600

def achieve_achievement(user, achievement):
    data = {
        'achievement': achievement.id,
        'user': user.id
    }
    if UserAchievedAchievment.objects.filter(achievement=achievement.id, user=user.id).exists():
        return True, 'achievement already achieved'
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
                    res = upgrade_level(user, achievement, 3)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 3,
                        'progress': 'done',
                        'hidden': achievement.hidden
                    }) 
                elif nr_of_exs >= 50:
                    res = upgrade_level(user, achievement, 2)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 2,
                        'progress': str(nr_of_exs)+'/100',
                        'hidden': achievement.hidden
                    }) 
                elif nr_of_exs >= 10:
                    res = achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
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
                    res = achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
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
                    res = upgrade_level(user, achievement, 4)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 4,
                        'progress': 'done',
                        'hidden': achievement.hidden
                    }) 
                elif streak >= 30:
                    res = upgrade_level(user, achievement, 3)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 3,
                        'progress': str(streak)+'/90',
                        'hidden': achievement.hidden
                    }) 
                elif streak >= 7:
                    res = upgrade_level(user, achievement, 2)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 2,
                        'progress': str(streak)+'/30',
                        'hidden': achievement.hidden
                    }) 
                elif streak >= 3:
                    res = achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
                    achieved.append({
                        'name': achievement.name,
                        'description': achievement.description,
                        'level': 1,
                        'progress': str(streak)+'/7',
                        'hidden': achievement.hidden
                    }) 
                elif not achievement.hidden:
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
                    res = achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
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
            #night owl
            elif achievement.name == 'nightOwl':
                found = False
                all = DoneExercises.objects.filter(user=user)
                for a in all:
                    if ((a.date % 86400) > NIGHT_START) and ((a.date % 84600) < NIGHT_END):
                        found = True
                        break
                if found:
                    res = achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
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
            #earlyBird
            elif achievement.name == 'earlyBird':
                found = False
                all = DoneExercises.objects.filter(user=user)
                for a in all:
                    if ((a.date % 86400) > NIGHT_END) and ((a.date % 84600) < EARLY_END):
                        found = True
                        break
                if found:
                    res = achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            'success': False,
                            'description': 'assigning achievement failed',
                            'data': {
                                'error': res[1],
                                'achievement': achievement.name
                                }
                            }
                        return Response(data)
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