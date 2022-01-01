import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BPBackendDjango.settings')
django.setup()
import hashlib
from .models import Admin, User, Trainer
from .settings import INTERN_SETTINGS

# check if at least one admin account exists
try:
    if not Admin.objects.filter().exists():
        newAdmin = Admin(first_name="Admin", last_name="Admin", username=INTERN_SETTINGS["admin_username"],
                         password=str(hashlib.sha3_256(INTERN_SETTINGS["admin_password"].encode('utf-8')).hexdigest()))
        newAdmin.save()
except:
    pass

try:
    if not User.objects.filter().exists():
        newUser = User(first_name="User", last_name="User", username=INTERN_SETTINGS["user_username"],
                       password=str(hashlib.sha3_256(INTERN_SETTINGS["user_password"].encode('utf-8')).hexdigest()))

        newUser.save()
except:
    pass

try:
    if not Trainer.objects.filter().exists():
        newTrainer = Trainer(first_name="User", last_name="User", username=INTERN_SETTINGS["trainer_username"],
                             password=str(
                                 hashlib.sha3_256(INTERN_SETTINGS["trainer_password"].encode('utf-8')).hexdigest()))

        newTrainer.save()
except:
    pass
