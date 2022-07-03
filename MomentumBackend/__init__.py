import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MomentumBackend.settings")
django.setup()


import hashlib
from .models import Admin, User, Trainer, Exercise, Leaderboard
from .settings import CONFIGURATION

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

try:
    if not Exercise.objects.filter().exists():
        newExercise = Exercise(
            title="Example Exercise",
            description={
                "en": "This is an Example Exercise",
                "de": "Dies ist eine Beispiel Übung",
            },
        )
        newExercise.save()
except:
    pass
