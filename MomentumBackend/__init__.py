import json
import locale
import jsonschema
import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MomentumBackend.settings")
django.setup()

from .settings import CONFIGURATION  # noqa: E402
from .models import Account, Exercise, Leaderboard, User  # noqa: E402


locale.setlocale(locale.LC_ALL, "en_US.utf8")

# check if at least one admin account (role == ADMIN) exists
try:
    if not User.objects.filter(account__role=Account.ADMIN).exists():
        newAdmin = User.objects.create_user(
            CONFIGURATION["admin_username"],
            "admin@example.com",  # TODO: maybe add this to the config as well
            CONFIGURATION["admin_password"]
        )
        newAdmin.is_superuser = True
        newAdmin.is_staff = True
        newAdmin.account = Account()
        newAdmin.save()

        newAdmin.account.role = Account.ADMIN
        newAdmin.account.save()
except Exception as e:
    print(e)

try:
    if not User.objects.filter(account__role=Account.TRAINER).exists():
        newTrainer = User.objects.create_user(
            CONFIGURATION["trainer_username"],
            "trainer@example.com",  # TODO: maybe add this to the config as well
            CONFIGURATION["trainer_password"]
        )
        newTrainer.account = Account()
        newTrainer.save()

        newTrainer.account.role = Account.TRAINER
        newTrainer.account.save()
except Exception as e:
    print(e)

try:
    if not User.objects.filter(account__role=Account.PLAYER).exists():
        trainer = User.objects.get(
            username=CONFIGURATION["trainer_username"])
        newUser = User.objects.create_user(
            CONFIGURATION["user_username"],
            "user@example.com",  # TODO: maybe add this to the config as well
            CONFIGURATION["user_password"]
        )
        newUser.account = Account()
        newUser.save()

        newUser.account.role = Account.PLAYER
        newUser.account.trainer = trainer
        newUser.account.save()

        Leaderboard.objects.create(
            user=User.objects.get(username=CONFIGURATION["user_username"]), score=0
        )
except Exception as e:
    print(e)


exerciseSchema = json.loads(
    open("MomentumBackend/schemas/exercises.json", "r").read())


def validateJson(jsonData):
    # validate json against schema
    try:
        jsonschema.validate(instance=jsonData, schema=exerciseSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    # validate json for id uniqueness
    if len(set(map(lambda ex: ex["id"], exercises))) != len(exercises):
        return False
    return True


try:
    exercises = json.loads(
        open("exercises.json", "r", encoding="UTF-8").read())
    if not validateJson(exercises):
        raise Exception("[WARNING] Invalid exercises.json\nThe schema can be found here: https://github.com/bp-momentum/backend/blob/main/MomentumBackend/schemas/exercises.json\nAlso make sure the Exercise IDs are unique.\nThe database will not be updated.")

    for exercise in exercises:
        if not Exercise.objects.filter(id=exercise["id"]).exists():
            ex = Exercise(
                title=exercise["title"],
                id=exercise["id"],
                description=exercise["description"],
                video=exercise.get("video"),
                expectation=exercise["expectation"],
            )
            ex.save()
        else:
            # can't use update here because it doesn't work with custom json type
            ex = Exercise.objects.filter(id=exercise["id"]).first()
            ex.title = exercise["title"]
            ex.description = exercise["description"]
            ex.video = exercise.get("video")
            ex.expectation = exercise["expectation"]
            ex.save()

    # delete exercises that are not in the exercises.json anymore
    Exercise.objects.exclude(id__in=[exercise["id"]
                             for exercise in exercises]).delete()

except Exception as e:
    print(e)
