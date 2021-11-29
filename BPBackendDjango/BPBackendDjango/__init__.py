import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BPBackendDjango.settings')
django.setup()
import hashlib
from .models import Admin
from .settings import INTERN_SETTINGS

## check if at least one admin account exists
print("checking admin")
if not Admin.objects.filter().exists():
    print("no admin found")
    newAdmin = Admin(first_name="Admin", last_name="Admin", username=INTERN_SETTINGS["admin_username"], password= str(hashlib.sha3_256(INTERN_SETTINGS["admin_password"].encode('utf-8')).hexdigest()))
    newAdmin.save()
    print("admin is now created")
else:
    print("admin found")