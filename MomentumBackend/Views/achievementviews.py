from urllib import request
from rest_framework.views import APIView
from rest_framework.response import Response

from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import AchievementHandler, ErrorHandler, LanguageHandler
from ..models import (
    Achievement,
    DoneExercises,
    Friends,
    User,
    UserAchievedAchievement,
    UserMedalInExercise,
)
from .exerciseviews import MAX_POINTS

# data for achievements (hours->seconds)
NIGHT_START = 22 * 84600
NIGHT_END = 6 * 84600
EARLY_END = 8 * 84600

ROOT_PATH = "https://cdn.geoscribble.de/achievements/"


class GetAchievementsView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # only users can get their own achievements
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])
        achieved = []
        nr_unachieved_hidden = 0

        # create non existing achievements (#TODO add icon path)
        if not Achievement.objects.filter(name="doneExercises").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'doneExercises_0.svg","1":"'
                + ROOT_PATH
                + 'doneExercises_1.svg","2":"'
                + ROOT_PATH
                + 'doneExercises_2.svg","3":"'
                + ROOT_PATH
                + 'doneExercises_3.svg"}'
            )
            Achievement.objects.create(
                name="doneExercises",
                title='{"en":"Done Exercises","de":"Abgeschlossene Übungen"}',
                description='{"en":"Do exercises to get/level this achievement","de":"Mache Übungen um diese Errungenschaft zu bekommen beziehungsweise hoch zu leveln"}',
                icon=icon_dict,
            )
        if not Achievement.objects.filter(name="havingFriends").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'friends_0.svg","1":"'
                + ROOT_PATH
                + 'friends_1.svg"}'
            )
            Achievement.objects.create(
                name="havingFriends",
                title='{"en":"A Friend!","de":"Freundschaft!"}',
                description='{"en":"Become friends with another user.","de":"Schließe eine Freundschaft mit einem/r anderen Spieler*in"}',
                icon=icon_dict,
            )
        if not Achievement.objects.filter(name="streak").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'streak_0.svg","1":"'
                + ROOT_PATH
                + 'streak_1.svg","2":"'
                + ROOT_PATH
                + 'streak_2.svg","3":"'
                + ROOT_PATH
                + 'streak_3.svg","4":"'
                + ROOT_PATH
                + 'streak_4.svg"}'
            )
            Achievement.objects.create(
                name="streak",
                title='{"en":"Streak","de":"Streak"}',
                description='{"en":"Reach a streak","de":"Erreiche eine Streak"}',
                icon=icon_dict,
            )
        if not Achievement.objects.filter(name="perfectExercise").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'perfectExercise_0.svg","1":"'
                + ROOT_PATH
                + 'perfectExercise_1.svg"}'
            )
            Achievement.objects.create(
                name="perfectExercise",
                title='{"en":"Perfect Exercise","de":"Perfekte Übung"}',
                description='{"en":"Complete an exercise with 100 percent","de":"Erreiche 100 Prozent bei einer Übung"}',
                icon=icon_dict,
            )
        if not Achievement.objects.filter(name="nightOwl").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'nightOwl_0.svg","1":"'
                + ROOT_PATH
                + 'nightOwl_1.svg"}'
            )
            Achievement.objects.create(
                name="nightOwl",
                title='{"en":"Night Owl","de":"Nachteule"}',
                description='{"en":"Do an exercise between 10 PM and 6 AM","de":"Mache eine Übung zwischen 10 Uhr abends und 6 Uhr morgens"}',
                hidden=True,
                icon=icon_dict,
            )
        if not Achievement.objects.filter(name="earlyBird").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'earlyBird_0.svg","1":"'
                + ROOT_PATH
                + 'earlyBird_1.svg"}'
            )
            Achievement.objects.create(
                name="earlyBird",
                title='{"en":"Early Bird","de":"Der frühe Vogel.."}',
                description='{"en":"Do an exercise early in the morning (between 6 AM and 8 AM)","de":"Mache eine Übung frühmorgens (zwischen 6 und 8 Uhr)"}',
                hidden=True,
                icon=icon_dict,
            )
        # iterate over all existing achievements
        for achievement in Achievement.objects.all():
            # do excersises
            if achievement.name == "doneExercises":
                # get number of done exercises
                nr_of_exs = len(DoneExercises.objects.filter(user=user.id))
                # check which level is reached
                if nr_of_exs >= 100:
                    res = AchievementHandler.upgrade_level(user, achievement, 3)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 3,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(3, achievement.icon),
                        }
                    )
                elif nr_of_exs >= 50:
                    res = AchievementHandler.upgrade_level(user, achievement, 2)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 2,
                            "progress": str(nr_of_exs) + "/100",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(2, achievement.icon),
                        }
                    )
                elif nr_of_exs >= 10:
                    res = AchievementHandler.achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": str(nr_of_exs) + "/50",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(2, achievement.icon),
                        }
                    )
                elif not achievement.hidden:
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 0,
                            "progress": str(nr_of_exs) + "/10",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(0, achievement.icon),
                        }
                    )
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            # make a friend
            elif achievement.name == "havingFriends":
                # get number of friends
                nr_of_friends = len(
                    Friends.objects.filter(friend1=user.id, accepted=True).union(
                        Friends.objects.filter(friend2=user.id, accepted=True)
                    )
                )
                # check which level is reached
                if nr_of_friends >= 1:
                    res = AchievementHandler.achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
                elif not achievement.hidden:
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 0,
                            "progress": "0/1",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(0, achievement.icon),
                        }
                    )
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            # streak
            elif achievement.name == "streak":
                # get users streak
                streak = user.streak
                # check which level is reached
                if streak >= 90:
                    res = AchievementHandler.upgrade_level(user, achievement, 4)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 4,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(4, achievement.icon),
                        }
                    )
                elif streak >= 30:
                    res = AchievementHandler.upgrade_level(user, achievement, 3)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 3,
                            "progress": str(streak) + "/90",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(3, achievement.icon),
                        }
                    )
                elif streak >= 7:
                    res = AchievementHandler.upgrade_level(user, achievement, 2)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 2,
                            "progress": str(streak) + "/30",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(2, achievement.icon),
                        }
                    )
                elif streak >= 3:
                    res = AchievementHandler.achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": str(streak) + "/7",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
                elif not achievement.hidden:
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 0,
                            "progress": str(streak) + "/3",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(0, achievement.icon),
                        }
                    )
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            # perfectExercise
            elif achievement.name == "perfectExercise":
                found = False
                # get all exercise
                all = DoneExercises.objects.filter(user=user)
                # search for exercise with MAX_POINTS
                for a in all:
                    if a.points == MAX_POINTS:
                        found = True
                        break
                # set achievement
                if found:
                    res = AchievementHandler.achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
                elif not achievement.hidden:
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 0,
                            "progress": "0/1",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(0, achievement.icon),
                        }
                    )
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            # night owl
            elif achievement.name == "nightOwl":
                found = False
                # get all done exercises
                all = DoneExercises.objects.filter(user=user)
                # check which exercises where done in the night
                for a in all:
                    if ((a.date % 86400) > NIGHT_START) and (
                        (a.date % 84600) < NIGHT_END
                    ):
                        found = True
                        break
                # set achievement
                if found:
                    res = AchievementHandler.achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
                elif not achievement.hidden:
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 0,
                            "progress": "0/1",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(0, achievement.icon),
                        }
                    )
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1
            # earlyBird
            elif achievement.name == "earlyBird":
                found = False
                # get all exercises
                all = DoneExercises.objects.filter(user=user)
                # check which ones where done erly in the morning
                for a in all:
                    if ((a.date % 86400) > NIGHT_END) and (
                        (a.date % 84600) < EARLY_END
                    ):
                        found = True
                        break
                # set achievement
                if found:
                    res = AchievementHandler.achieve_achievement(user, achievement)
                    if not res[0]:
                        data = {
                            "success": False,
                            "description": "assigning achievement failed",
                            "data": {"error": res[1], "achievement": achievement.name},
                        }
                        return Response(data)
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
                elif not achievement.hidden:
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 0,
                            "progress": "0/1",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(0, achievement.icon),
                        }
                    )
                else:
                    nr_unachieved_hidden = nr_unachieved_hidden + 1

        data = {
            "success": True,
            "description": "Returning achievements",
            "data": {
                "achievements": achieved,
                "nr_unachieved_hidden": nr_unachieved_hidden,
            },
        }
        return Response(data)


class ReloadFriendAchievementView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # only users can get their own achievements
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])

        # can not be achieved
        if not Achievement.objects.filter(name="havingFriends").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'friends_0.svg","1":"'
                + ROOT_PATH
                + 'friends_1.svg"}'
            )
            Achievement.objects.create(
                name="havingFriends",
                title='{"en":"A Friend!","de":"Freundschaft!"}',
                description='{"en": "Become friends with another user.", "de": "Sei mit einem Spieler befreundet"}',
                icon=icon_dict,
            )

        achievement: Achievement = Achievement.objects.get(name="havingFriends")

        # already achieved
        if UserAchievedAchievement.objects.filter(
            achievement=achievement, user=user
        ).exists():
            data = {"success": True, "description": "Not achieved", "data": {}}
            return Response(data)

        # get number of friends
        nr_of_friends = len(
            Friends.objects.filter(friend1=user.id, accepted=True).union(
                Friends.objects.filter(friend2=user.id, accepted=True)
            )
        )
        # check which level is reached
        if nr_of_friends >= 1:
            res = AchievementHandler.achieve_achievement(user, achievement)
            if not res[0]:
                data = {
                    "success": False,
                    "description": "assigning achievement failed",
                    "data": {"error": res[1], "achievement": achievement.name},
                }
                return Response(data)
            data = {
                "success": True,
                "description": "Achieved",
                "data": {
                    "achievements": {
                        "name": achievement.name,
                        "title": LanguageHandler.get_in_correct_language(
                            user.username, achievement.title
                        ),
                        "description": LanguageHandler.get_in_correct_language(
                            user.username, achievement.description
                        ),
                        "level": 1,
                        "progress": "done",
                        "hidden": achievement.hidden,
                        "icon": AchievementHandler.get_icon(1, achievement.icon),
                    }
                },
            }
        else:
            data = {"success": True, "description": "Not achieved", "data": {}}
        return Response(data)


class ReloadAfterExerciseView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # only users can get their own achievements
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])
        achieved = []
        # do excersises
        if not Achievement.objects.filter(name="doneExercises").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'doneExercises_0.svg","1":"'
                + ROOT_PATH
                + 'doneExercises_1.svg","2":"'
                + ROOT_PATH
                + 'doneExercises_2.svg","3":"'
                + ROOT_PATH
                + 'doneExercises_3.svg"}'
            )
            Achievement.objects.create(
                name="doneExercises",
                title='{"en":"Done Exercises","de":"Abgeschlossene Übungen"}',
                description='{"en": "Do exercises to get/level this achievement", "de": "Mache Übungen um diese Errungenschaft zu bekommen beziehungsweise hoch zu leveln"}',
            )
        achievement: Achievement = Achievement.objects.get(name="doneExercises")
        # get number of done exercises
        nr_of_exs = len(DoneExercises.objects.filter(user=user.id))
        # already achieved
        if not UserAchievedAchievement.objects.filter(
            achievement=achievement, user=user, level=3
        ).exists():
            # check which level is reached
            if nr_of_exs >= 100:
                res = AchievementHandler.upgrade_level(user, achievement, 3)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "level upgraded":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 3,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(3, achievement.icon),
                        }
                    )
            elif nr_of_exs >= 50:
                res = AchievementHandler.upgrade_level(user, achievement, 2)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "level upgraded":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 2,
                            "progress": str(nr_of_exs) + "/100",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(2, achievement.icon),
                        }
                    )
            elif nr_of_exs >= 10:
                res = AchievementHandler.achieve_achievement(user, achievement)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "user achieved achievement":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": str(nr_of_exs) + "/50",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
        # perfectExercise
        if not Achievement.objects.filter(name="perfectExercise").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'perfectExercise_0.svg","1":"'
                + ROOT_PATH
                + 'perfectExercise_1.svg"}'
            )
            Achievement.objects.create(
                name="perfectExercise",
                title='{"en":"Perfect Exercise","de":"Perfekte Übung"}',
                description='{"en": "Complete an exercise with 100 percent", "de": "Erreiche 100 Prozent bei einer Übung"}',
            )
        achievement = Achievement.objects.get(name="perfectExercise")
        # check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(
            achievement=achievement, user=user
        ).exists():
            found = False
            # get all exercise
            all = DoneExercises.objects.filter(user=user)
            # search for exercise with MAX_POINTS
            for a in all:
                if a.points == MAX_POINTS:
                    found = True
                    break
            # set achievement
            if found:
                res = AchievementHandler.achieve_achievement(user, achievement)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "user achieved achievement":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
        # night owl
        if not Achievement.objects.filter(name="nightOwl").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'nightOwl_0.svg","1":"'
                + ROOT_PATH
                + 'nightOwl_1.svg"}'
            )
            Achievement.objects.create(
                name="nightOwl",
                title='{"en":"Night Owl","de":"Nachteule"}',
                description='{"en": "Do an exercise between 10 PM and 6 AM", "de": "Mache eine Übung zwischen 10 Uhr abends und 6 Uhr morgens"}',
                hidden=True,
            )
        achievement = Achievement.objects.get(name="nightOwl")
        # check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(
            achievement=achievement, user=user
        ).exists():
            found = False
            # get all done exercises
            all = DoneExercises.objects.filter(user=user)
            # check which exercises where done in the night
            for a in all:
                if ((a.date % 86400) > NIGHT_START) and ((a.date % 84600) < NIGHT_END):
                    found = True
                    break
            # set achievement
            if found:
                res = AchievementHandler.achieve_achievement(user, achievement)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "user achieved achievement":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
        # earlyBird
        if not Achievement.objects.filter(name="earlyBird").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'earlyBird_0.svg","1":"'
                + ROOT_PATH
                + 'earlyBird_1.svg"}'
            )
            Achievement.objects.create(
                name="earlyBird",
                title='{"en":"Early Bird","de":"Der frühe Vogel.."}',
                description='{"en": "Do an exercise early in the morning (between 6 AM and 8 AM)", "de": "Mache eine Übung frühmorgens (zwischen 6 und 8 Uhr)"}',
                hidden=True,
                icon=icon_dict,
            )
        achievement = Achievement.objects.get(name="earlyBird")
        # check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(
            achievement=achievement, user=user
        ).exists():
            found = False
            # get all exercises
            all = DoneExercises.objects.filter(user=user)
            # check which ones where done erly in the morning
            for a in all:
                if ((a.date % 86400) > NIGHT_END) and ((a.date % 84600) < EARLY_END):
                    found = True
                    break
            # set achievement
            if found:
                res = AchievementHandler.achieve_achievement(user, achievement)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "user achieved achievement":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
        # streak
        if not Achievement.objects.filter(name="streak").exists():
            icon_dict = (
                '{"0":"'
                + ROOT_PATH
                + 'streak_0.svg","1":"'
                + ROOT_PATH
                + 'streak_1.svg","2":"'
                + ROOT_PATH
                + 'streak_2.svg","3":"'
                + ROOT_PATH
                + 'streak_3.svg","4":"'
                + ROOT_PATH
                + 'streak_4.svg"}'
            )
            Achievement.objects.create(
                name="streak",
                title='{"en":"Streak","de":"Streak"}',
                description='{"en": "Reach a streak", "de": "Erreiche eine Streak"}',
                icon=icon_dict,
            )
        achievement = Achievement.objects.get(name="streak")
        # check if achievement already achieved
        if not UserAchievedAchievement.objects.filter(
            achievement=achievement, user=user, level=4
        ).exists():
            # get users streak
            streak = user.streak
            # check which level is reached
            if streak >= 90:
                res = AchievementHandler.upgrade_level(user, achievement, 4)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "level upgraded":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 4,
                            "progress": "done",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(4, achievement.icon),
                        }
                    )
            elif streak >= 30:
                res = AchievementHandler.upgrade_level(user, achievement, 3)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "level upgraded":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 3,
                            "progress": str(streak) + "/90",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(3, achievement.icon),
                        }
                    )
            elif streak >= 7:
                res = AchievementHandler.upgrade_level(user, achievement, 2)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "level upgraded":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 2,
                            "progress": str(streak) + "/30",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(2, achievement.icon),
                        }
                    )
            elif streak >= 3:
                res = AchievementHandler.achieve_achievement(user, achievement)
                if not res[0]:
                    data = {
                        "success": False,
                        "description": "assigning achievement failed",
                        "data": {"error": res[1], "achievement": achievement.name},
                    }
                    return Response(data)
                if res[1] == "user achieved achievement":
                    achieved.append(
                        {
                            "name": achievement.name,
                            "title": LanguageHandler.get_in_correct_language(
                                user.username, achievement.title
                            ),
                            "description": LanguageHandler.get_in_correct_language(
                                user.username, achievement.description
                            ),
                            "level": 1,
                            "progress": str(streak) + "/7",
                            "hidden": achievement.hidden,
                            "icon": AchievementHandler.get_icon(1, achievement.icon),
                        }
                    )
        # check if new achieved
        if len(achieved) == 0:
            data = {"success": True, "description": "Not achieved", "data": {}}
        else:
            data = {
                "success": True,
                "description": "new achieved",
                "data": {"achievements": achieved},
            }
        return Response(data)


class GetMedals(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # check if user
        if not info["account_type"] == "user":
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])
        medals = UserMedalInExercise.objects.filter(user=user)
        output = []
        for mex in medals:
            output.append(
                {
                    "exercise": mex.exercise.title,
                    "gold": mex.gold,
                    "silver": mex.silver,
                    "bronze": mex.bronze,
                }
            )
        data = {
            "success": True,
            "description": "returning medals",
            "data": {"medals": output},
        }
        return Response(data)
