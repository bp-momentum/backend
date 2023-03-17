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
    # validate json against schema
    try:
        validate(instance=jsonData, schema=exerciseSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    # validate json for id uniqueness
    if len(set(map(lambda ex: ex["id"], exercises))) != len(exercises):
        return False
    return True

try:
    exercises = json.loads(open("exercises.json", "r", encoding="UTF-8").read())
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
    Exercise.objects.exclude(id__in=[exercise["id"] for exercise in exercises]).delete()

except Exception as e:
    print(e)
