from django.test import TestCase
from .models import *

class UserTestCase(TestCase):
    def setUp(self):
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(id=0)
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
    
    def check_if_exists(self):
        self.assertTrue(Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").exists())
        self.assertTrue(User.objects.filter(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=0, email_address="prescher-erik@web.de", password="Password1234").exists())

    def check_if_user_gets_deleted_when_trainer_gets_deleted(self):
        Trainer.objects.delete(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.assertFalse(Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").exists())
        self.assertFalse(User.objects.filter(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=0, email_address="prescher-erik@web.de", password="Password1234").exists())