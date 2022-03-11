from urllib import request
from rest_framework.views import APIView
from rest_framework.response import Response
import json
import time

from ..Helperclasses.jwttoken import JwToken
from ..serializers import AchieveAchievement
from ..Helperclasses.handlers import ErrorHandler
from ..models import *
from .exerciseviews import MAX_POINTS

#data for achievements (hours->seconds)
NIGHT_START = 22*84600
NIGHT_END = 6*84600
EARLY_END = 8*84600

def achieve_achievement(user, achievement):
    #set up data for new achievement
    data = {
        'achievement': achievement,
        'user': user,
        'date': time.time()
    }
    #if already achieved do nothing
    if UserAchievedAchievement.objects.filter(achievement=achievement, user=user).exists():
        return True, 'achievement already achieved'
    serializer = AchieveAchievement(data=data)
    #if data not valid do nothing
    if not serializer.is_valid():
        return False, 'new data not valid'
    #save completed achievement
    serializer.save()
    return True, 'user achieved achievement'

def upgrade_level(user, achievement, level):
    #if user has not achieved achievement, he achieves it now
    if not UserAchievedAchievement.objects.filter(achievement=achievement.id, user=user.id).exists():
        res = achieve_achievement(user, achievement)
        if not res[0]:
            return res
    #update level
    uaa:UserAchievedAchievement = UserAchievedAchievement.objects.get(achievement=achievement.id,user=user.id)
    #only update if new level is higher
    if level <= uaa.level:
        return True, 'user already achieved (higher) level'
    uaa.level = level
    uaa.date = time.time()
    uaa.save(force_update=True)
    return True, 'level upgraded'

def get_correct_description(username, description):
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
    elif Trainer.objects.filter(username=username).exists():
        user = Trainer.objects.get(username=username)
    elif Admin.objects.filter(username=username).exists():
        user = Admin.objects.get(username=username)
    else:
        return "invalid user"
    lang = user.language
    desc = json.loads(description)
    res = desc.get(lang)
    if res == None:
        return "description not available in "+lang
    return res


class GetAchievementsView(APIView):
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

        #only users can get their own achievements
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

        #create non existing achievements (#TODO add icon path)
        if not Achievement.objects.filter(name='doneExercises').exists():
            Achievement.objects.create(name='doneExercises', description='{"en":"Do exercises top get/level this achievement","de":"Mache Übungen um dieses Achievemnet zu bekommen beziehungsweise hoch zu leveln"}')
        if not Achievement.objects.filter(name='havingFriends').exists():
            Achievement.objects.create(name='havingFriends', description='{"en":"Become friends with another user.","de":"Sei mit einem Spieler befreundet"}')
        if not Achievement.objects.filter(name='streak').exists():
            Achievement.objects.create(name='streak', description='{"en":"Reach a streak","de":"Erreiche eine Streak"}')
        if not Achievement.objects.filter(name='perfectExercise').exists():
            Achievement.objects.create(name='perfectExercise', description='{"en":"Reach 100 percent at one exercise","de":"Erreiche 100 Prozent bei einer Übung"}')
        if not Achievement.objects.filter(name='nightOwl').exists():
            Achievement.objects.create(name='nightOwl', description='{"en":"Do an exercise between 10 PM to 6 AM","de":"Mache eine Übung zwischen 10 Uhr abends und 6 Uhr morgens"}', hidden= True)
        if not Achievement.objects.filter(name='earlyBird').exists():
            Achievement.objects.create(name='earlyBird', description='{"en":"Do an exercise early in the morning (between 6 AM and 8 AM)","de":"Mache eine Übung frühmorgens (zwischen 6 und 8 Uhr)"}', hidden=True)
        #iterate over all existing achievements
        for achievement in Achievement.objects.all():
            #do excersises
            if achievement.name == 'doneExercises':
                #get number of done exercises
                nr_of_exs = len(DoneExercises.objects.filter(user=user.id))
                #check which level is reached
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 3,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 2,
                        'progress': str(nr_of_exs)+'/100',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': str(nr_of_exs)+'/50',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    }) 
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 0,
                        'progress': str(nr_of_exs)+'/10',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #make a friend
            elif achievement.name == 'havingFriends':
                #get number of friends
                nr_of_friends = len(Friends.objects.filter(friend1=user.id).union(Friends.objects.filter(friend2=user.id)))
                #check which level is reached
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    }) 
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 0,
                        'progress': '0/1',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    }) 
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #streak
            elif achievement.name == 'streak':
                #get users streak
                streak = user.streak
                #check which level is reached
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 4,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 3,
                        'progress': str(streak)+'/90',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 2,
                        'progress': str(streak)+'/30',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': str(streak)+'/7',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    }) 
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 0,
                        'progress': str(streak)+'/3',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    }) 
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #perfectExercise
            elif achievement.name == 'perfectExercise':
                found = False
                #get all exercise
                all = DoneExercises.objects.filter(user=user)
                #search for exercise with MAX_POINTS
                for a in all:
                    if a.points == MAX_POINTS:
                        found = True
                        break
                #set achievement
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 0,
                        'progress': '0/1',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #night owl
            elif achievement.name == 'nightOwl':
                found = False
                #get all done exercises
                all = DoneExercises.objects.filter(user=user)
                #check which exercises where done in the night
                for a in all:
                    if ((a.date % 86400) > NIGHT_START) and ((a.date % 84600) < NIGHT_END):
                        found = True
                        break
                #set achievement
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 0,
                        'progress': '0/1',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            #earlyBird
            elif achievement.name == 'earlyBird':
                found = False
                #get all exercises
                all = DoneExercises.objects.filter(user=user)
                #check which ones where done erly in the morning
                for a in all:
                    if ((a.date % 86400) > NIGHT_END) and ((a.date % 84600) < EARLY_END):
                        found = True
                        break
                #set achievement
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
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
                elif not achievement.hidden:
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 0,
                        'progress': '0/1',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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


class ReloadFriendAchievementView(APIView):

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

        #only users can get their own achievements
        if not User.objects.filter(username=info['username']).exists():
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])

        #can not be achieved
        if not Achievement.objects.filter(name='havingFriends').exists():
            Achievement.objects.create(name='havingFriends', description='{"en": "Become friends with another user.", "de": "Sei mit einem Spieler befreundet"}')

        achievement = Achievement.objects.get(name='havingFriends')

        #already achieved
        if UserAchievedAchievement.objects.filter(achievement=achievement, user=user).exists():
            data = {
                'success': True,
                'description': 'Not achieved',
                'data': {}
                }
            return Response(data)

        #get number of friends
        nr_of_friends = len(Friends.objects.filter(friend1=user.id).union(Friends.objects.filter(friend2=user.id)))
        #check which level is reached
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
            data = {
                'success': True,
                'description': 'Achieved',
                'data': {
                    'achievements': {
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    }
                }
            }
        else:
            data = {
                'success': True,
                'description': 'Not achieved',
                'data': {}
            }
        return Response(data)


class ReloadAfterExerciseView(APIView):

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

        #only users can get their own achievements
        if not User.objects.filter(username=info['username']).exists():
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])
        achieved = []
        #do excersises
        if not Achievement.objects.filter(name='doneExercises').exists():
            Achievement.objects.create(name='doneExercises', description='{"en": "Do exercises top get/level this achievement", "de": "Mache Übungen um dieses Achievemnet zu bekommen beziehungsweise hoch zu leveln"}')
        achievement = Achievement.objects.get(name='doneExercises')
        #get number of done exercises
        nr_of_exs = len(DoneExercises.objects.filter(user=user.id))
        #already achieved
        if not UserAchievedAchievement.objects.filter(achievement=achievement, user=user, level=3).exists():
        #check which level is reached
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
                if res[1] == 'level upgraded':
                    achieved.append({
                    'name': achievement.name,
                    'description': get_correct_description(user.username, achievement.description),
                    'level': 3,
                    'progress': 'done',
                    'hidden': achievement.hidden,
                    'icon': achievement.icon
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
                if res[1] == 'level upgraded':
                    achieved.append({
                    'name': achievement.name,
                    'description': get_correct_description(user.username, achievement.description),
                    'level': 2,
                    'progress': str(nr_of_exs)+'/100',
                    'hidden': achievement.hidden,
                    'icon': achievement.icon
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
                if res[1] == 'user achieved achievement':
                    achieved.append({
                    'name': achievement.name,
                    'description': get_correct_description(user.username, achievement.description),
                    'level': 1,
                    'progress': str(nr_of_exs)+'/50',
                    'hidden': achievement.hidden,
                    'icon': achievement.icon
                }) 
        #perfectExercise
        if not Achievement.objects.filter(name='perfectExercise').exists():
            Achievement.objects.create(name='perfectExercise', description='{"en": "Reach 100 percent at one exercise", "de": Erreiche 100 Prozent bei einer Übung"}')
        achievement = Achievement.objects.get(name='perfectExercise')
        #check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(achievement=achievement, user=user).exists():
            found = False
            #get all exercise
            all = DoneExercises.objects.filter(user=user)
            #search for exercise with MAX_POINTS
            for a in all:
                if a.points == MAX_POINTS:
                    found = True
                    break
            #set achievement
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
                if res[1] == 'user achieved achievement':
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
        #night owl
        if not Achievement.objects.filter(name='nightOwl').exists():
            Achievement.objects.create(name='nightOwl', description='{"en": "Do an exercise between 10 PM to 6 AM", "de": "Mache eine Übung zwischen 10 Uhr abends und 6 Uhr morgens"}', hidden= True)
        achievement = Achievement.objects.get(name='nightOwl')
        #check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(achievement=achievement, user=user).exists():
            found = False
            #get all done exercises
            all = DoneExercises.objects.filter(user=user)
            #check which exercises where done in the night
            for a in all:
                if ((a.date % 86400) > NIGHT_START) and ((a.date % 84600) < NIGHT_END):
                    found = True
                    break
            #set achievement
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
                if res[1] == 'user achieved achievement':
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
        #earlyBird
        if not Achievement.objects.filter(name='earlyBird').exists():
            Achievement.objects.create(name='earlyBird', description='{"en": "Do an exercise early in the morning (between 6 AM and 8 AM)", "de": "Mache eine Übung frühmorgens (zwischen 6 und 8 Uhr)"}', hidden=True)
        achievement = Achievement.objects.get(name='earlyBird')
        #check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(achievement=achievement, user=user).exists():
            found = False
            #get all exercises
            all = DoneExercises.objects.filter(user=user)
            #check which ones where done erly in the morning
            for a in all:
                if ((a.date % 86400) > NIGHT_END) and ((a.date % 84600) < EARLY_END):
                    found = True
                    break
            #set achievement
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
                if res[1] == 'user achieved achievement':
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    })
        #streak
        if not Achievement.objects.filter(name='streak').exists():
            Achievement.objects.create(name='streak', description='{"en": "Reach a streak", "de": "Erreiche eine Streak"}')
        achievement = Achievement.objects.get(name='streak')
        #check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(achievement=achievement, user=user, level=4).exists():
            #get users streak
            streak = user.streak
            #check which level is reached
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
                if res[1] == 'level upgraded':
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 4,
                        'progress': 'done',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                if res[1] == 'level upgraded':
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 3,
                        'progress': str(streak)+'/90',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                if res[1] == 'level upgraded':
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 2,
                        'progress': str(streak)+'/30',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
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
                if res[1] == 'user achieved achievement':
                    achieved.append({
                        'name': achievement.name,
                        'description': get_correct_description(user.username, achievement.description),
                        'level': 1,
                        'progress': str(streak)+'/7',
                        'hidden': achievement.hidden,
                        'icon': achievement.icon
                    }) 
        #check if new achieved
        if len(achieved) == 0:
            data = {
                'success': True,
                'description': 'no new achieved',
                'data': {}
            }
        else:
            data = {
                'success': True,
                'description': 'new achieved',
                'data': {
                    'achievements': achieved
                }
            }
        return Response(data)


class GetMedals(APIView):

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
        #check if user
        if not info['account_type'] == 'user':
            data = {
                'success': False,
                'description': 'Not a user',
                'data': {}
                }
            return Response(data)

        user = User.objects.get(username=info['username'])
        medals = UserMedalInExercise.objects.filter(user=user)
        output = []
        for mex in medals:
            output.append({
                'exercise': mex.exercise.title,
                'gold': mex.gold,
                'silver': mex.silver,
                'bronze': mex.bronze
            })
        data = {
            'success': True,
            'description': 'returning medals',
            'data': {
                'medals': output
            }
        }
        return Response(data)