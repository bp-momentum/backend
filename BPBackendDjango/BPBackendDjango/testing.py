from django.test import TestCase
from .models import *

class UserTestCase(TestCase):
    
    trainer_id = 1

    def setUp(self):
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        UserTestCase.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
    
    def test_if_exists(self):
        self.assertTrue(Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").exists())
        self.assertTrue(User.objects.filter(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=UserTestCase.trainer_id, email_address="prescher-erik@web.de", password="Password1234").exists())

    def test_if_user_gets_deleted_when_trainer_gets_deleted(self):
        Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").delete()
        self.assertFalse(Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").exists())
        self.assertFalse(User.objects.filter(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=UserTestCase.trainer_id, email_address="prescher-erik@web.de", password="Password1234").exists())


class DeleteUserTestCase(TestCase):

    user_id = 1
    user_id_2 = 2
    trainer_id = 1
    exercise_id = 1
    done_ex_id = 1
    friends_id = 1

    def setUp(self):
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        DeleteUserTestCase.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password="Password1234")
        user1 = User.objects.get(first_name='Erik')
        user2 = User.objects.get(first_name='Jannis')
        DeleteUserTestCase.user_id = user1.id
        DeleteUserTestCase.user_id_2 = user2.id
        Exercise.objects.create(title='Squat', description='Just do it.')
        exercise = Exercise.objects.get(title='Squat')
        DeleteUserTestCase.exercise_id = exercise.id
        DoneExercises.objects.create(exercise=exercise, user=user1, points=98)
        DeleteUserTestCase.done_ex_id = DoneExercises.objects.get(points=98).id
        Friends.objects.create(friend1=user1, friend2=user2)
        DeleteUserTestCase.friends_id = Friends.objects.get(friend1=DeleteUserTestCase.user_id).id

    def test_cascade(self):
        User.objects.filter(id=DeleteUserTestCase.user_id).delete()
        self.assertTrue(User.objects.filter(id=DeleteUserTestCase.user_id_2).exists())
        self.assertTrue(Trainer.objects.filter(id=DeleteUserTestCase.trainer_id).exists())
        self.assertTrue(Exercise.objects.filter(id=DeleteUserTestCase.exercise_id).exists())
        self.assertFalse(User.objects.filter(id=DeleteUserTestCase.user_id).exists())
        self.assertFalse(DoneExercises.objects.filter(id=DeleteUserTestCase.done_ex_id).exists())
        self.assertFalse(Friends.objects.filter(id=DeleteUserTestCase.friends_id).exists())


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
