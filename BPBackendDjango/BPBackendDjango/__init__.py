import hashlib
from .models import Admin
from settings import INTERN_SETTINGS

## check if at least one admin account exists
if not Admin.objects.filter().exists():
    newAdmin = Admin(first_name="Admin", last_name="Admin", username=INTERN_SETTINGS["admin_username"], password= str(hashlib.sha3_256(INTERN_SETTINGS["admin_password"].encode('utf-8')).hexdigest()))
