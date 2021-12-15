from django.test import TestCase
from .models import *

class UserTestCase(TestCase):

    trainer_id = 1

    def setUp(self):
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
    
    def test_if_exists(self):
        self.assertTrue(Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").exists())
        self.assertTrue(User.objects.filter(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=self.trainer_id, email_address="prescher-erik@web.de", password="Password1234").exists())

    def test_if_user_gets_deleted_when_trainer_gets_deleted(self):
        Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").delete()
        self.assertFalse(Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").exists())
        self.assertFalse(User.objects.filter(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=self.trainer_id, email_address="prescher-erik@web.de", password="Password1234").exists())


class ExerciseTestCase(TestCase):
    def setUp(self):
        Exercise.objects.create(title='Kniebeuge', description="Gehe in die Knie, achte...")
        Exercise.objects.create(title='Liegestütze', description="Mache Liegestütze", activated=False)

    def test_if_exists(self):
        self.assertTrue(Exercise.objects.filter(title='Kniebeuge', description="Gehe in die Knie, achte...", video=None, activated=True).exists())
        self.assertTrue(Exercise.objects.filter(title='Liegestütze', description="Mache Liegestütze", video=None, activated=False).exists())

    def test_if_delete_works(self):
        Exercise.objects.filter(title='Kniebeuge', description="Gehe in die Knie, achte...", video=None, activated=True).delete()
        Exercise.objects.filter(title='Liegestütze', description="Mache Liegestütze", video=None, activated=False).delete()
        self.assertFalse(Exercise.objects.filter(title='Kniebeuge', description="Gehe in die Knie, achte...", video=None, activated=True).exists())
        self.assertFalse(Exercise.objects.filter(title='Liegestütze', description="Mache Liegestütze", video=None, activated=False).exists())


class PlanTestCase(TestCase):

    trainer_id = 0
    user_id = 0
    ex_id = 0
    ts_id = 0

    def setUp(self):
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        user = User.objects.get(first_name="Erik")
        self.user_id = user.id
        Exercise.objects.create(title='Kniebeuge', description="Gehe in die Knie, achte...")
        ex = Exercise.objects.get(title='Kniebeuge')
        self.ex_id = ex.id
        TrainingSchedule.objects.create(trainer=trainer)
        ts = TrainingSchedule.objects.get(trainer=trainer.id)
        self.ts_id = ts.id
        ExerciseInPlan.objects.create(date="monday", sets=5, repeats_per_set=10, exercise=ex, plan=ts)
        user.plan = ts
        user.save()

    def test_if_exists(self):
        self.assertTrue(TrainingSchedule.objects.filter(trainer=self.trainer_id).exists())
        self.assertTrue(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id).exists())
        self.assertTrue(User.objects.filter(first_name="Erik").exists())
        user = User.objects.get(first_name="Erik")
        self.assertEquals(user.plan, self.ts_id)

    def test_if_related_deletes_work(self):
        Exercise.objects.filter(title='Kniebeuge').delete()
        Trainer.objects.filter(first_name="Erik").delete()
        self.assertFalse(User.objects.filter(first_name="Erik").exists())
        self.assertFalse(TrainingSchedule.objects.filter(id=self.ts_id).exists())
        self.assertFalse(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id))