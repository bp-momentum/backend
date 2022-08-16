import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MomentumBackend.settings")
django.setup()


import hashlib
from .models import Admin, ExerciseInPlan, User, Trainer, Exercise, Leaderboard
from .settings import CONFIGURATION
import json
import jsonschema
from jsonschema import validate

# check if at least one admin account exists
try:
    if not Admin.objects.filter().exists():
        newAdmin = Admin(
            first_name="Admin",
            last_name="Admin",
            username=CONFIGURATION["admin_username"],
            password=str(
                hashlib.sha3_256(
                    CONFIGURATION["admin_password"].encode("utf-8")
                ).hexdigest()
            ),
        )
        newAdmin.save()
except Exception as e:
    pass

try:
    if not Trainer.objects.filter().exists():
        newTrainer = Trainer(
            first_name="Trainer",
            last_name="Trainer",
            username=CONFIGURATION["trainer_username"],
            password=str(
                hashlib.sha3_256(
                    CONFIGURATION["trainer_password"].encode("utf-8")
                ).hexdigest()
            ),
        )

        newTrainer.save()
except:
    pass

try:
    if not User.objects.filter().exists():
        trainer = Trainer.objects.get(username=CONFIGURATION["trainer_username"])
        newUser = User(
            first_name="User",
            last_name="User",
            username=CONFIGURATION["user_username"],
            password=str(
                hashlib.sha3_256(
                    CONFIGURATION["user_password"].encode("utf-8")
                ).hexdigest()
            ),
            trainer=trainer,
        )

        newUser.save()
        Leaderboard.objects.create(
            user=User.objects.get(username=CONFIGURATION["user_username"]), score=0
        )
except:
    pass


exerciseSchema = json.loads(open("MomentumBackend/schemas/exercises.json", "r").read())

def validateJson(jsonData):
    try:
        validate(instance=jsonData, schema=exerciseSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

try:
    exercises = json.loads(open("exercises.json", "r").read())
    if not validateJson(exercises):
        raise Exception("[WARNING] Invalid exercises.json\nThe schema can be found here: https://github.com/bp-momentum/blob/main/MomentumBackend/schemas/exercises.json\nThe database will not be updated.")
    needsRebuilding = False
    # if amount of exercises in database is not equal to amount of exercises in json file, rebuild database
    if len(Exercise.objects.all()) != len(exercises):
        needsRebuilding = True
    # if any exercise in database is not equal to any exercise in json file, rebuild database
    for exercise in Exercise.objects.all():
        if (ex := exercises.get(exercise.title)) is None:
            needsRebuilding = True
            break
        if exercise.description["en"] != ex["description"]["en"] or exercise.description["de"] != ex["description"]["de"]:
            needsRebuilding = True
            break
        if exercise.video != ex.get("video"):
            needsRebuilding = True
            break

    if needsRebuilding:
        Exercise.objects.all().delete()
        for exercise in exercises:
            Exercise.objects.create(
                title=exercise,
                description=exercises[exercise]["description"],
                video=exercises[exercise].get("video"),
            )
except Exception as e:
    print(e)
