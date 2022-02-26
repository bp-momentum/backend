from urllib import request
from django.test import TestCase

from .Views.exerciseviews import GetDoneExercisesOfMonthView, get_done_exercises_of_month
from .Helperclasses.fortests import ViewSupport
from .Helperclasses.jwttoken import JwToken
from .Views.friendviews import AcceptRequestView, AddFriendView, DeclineRequestView, DeleteFriendView, GetMyFriendsView, GetPendingRequestView, GetRequestView, get_friends, get_pending_requests, get_requests
from .Views.userviews import DeleteTrainerView, DeleteUserView, GetUsersOfTrainerView, GetTrainersView, get_trainers_data, get_users_data_for_upper
from .Views.userviews import GetInvitedView, InvalidateInviteView, get_invited_data
from .Views.userviews import ChangeAvatarView, ChangeMotovationView, ChangePasswordView, ChangeTrainerAcademiaView, ChangeTrainerTelephoneView, ChangeUsernameView, DeleteTrainerView, DeleteUserView, GetProfileView, GetTrainerContactView, GetUsersOfTrainerView, GetTrainersView, SetTrainerLocationView, get_trainers_data, get_users_data_for_upper
from .Views.userviews import DeleteTrainerView, DeleteUserView, GetInvitedView, GetUsersOfTrainerView, GetTrainersView, InvalidateInviteView, get_invited_data, get_trainers_data, get_users_data_for_upper
from .Views.userviews import GetUserLevelView
from .models import *
from .Helperclasses.jwttoken import JwToken
from .Views.achievementviews import GetAchievementsView
import hashlib
import time
import datetime

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
        plan = TrainingSchedule.objects.create(name="testplan", trainer=trainer)
        exercise_plan = ExerciseInPlan.objects.create(exercise=exercise, plan=plan)
        DoneExercises.objects.create(exercise=exercise_plan, user=user1, points=98)
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
        self.assertEquals(user.plan.id, self.ts_id)

    def test_if_related_deletes_work(self):
        Exercise.objects.filter(title='Kniebeuge').delete()
        Trainer.objects.filter(first_name="Erik").delete()
        self.assertFalse(User.objects.filter(first_name="Erik").exists())
        self.assertFalse(TrainingSchedule.objects.filter(id=self.ts_id).exists())
        self.assertFalse(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id))


class getUsersAndTrainersTestCase(TestCase):

    admin = None
    trainers = []
    users = []

    def setUp(self) -> None:
        Admin.objects.create(first_name="Erik", last_name="Prescher", username="DerAdmin", password="Password1234")
        self.admin = Admin.objects.get(username="DerAdmin")
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainers.append(Trainer.objects.get(first_name="Erik"))
        Trainer.objects.create(first_name="Jannis", last_name="Bauer", username="DerAndereTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainers.append(Trainer.objects.get(first_name="Jannis"))
        User.objects.create(first_name="vorname", last_name="nachname", username="user1", email_address="user1@users.com", trainer=self.trainers[0],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user2", email_address="user2@users.com", trainer=self.trainers[0],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user3", email_address="user3@users.com", trainer=self.trainers[0],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user4", email_address="user4@users.com", trainer=self.trainers[0],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user5", email_address="user5@users.com", trainer=self.trainers[0],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user6", email_address="user6@users.com", trainer=self.trainers[1],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user7", email_address="user7@users.com", trainer=self.trainers[1],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user8", email_address="user8@users.com", trainer=self.trainers[1],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user9", email_address="user9@users.com", trainer=self.trainers[1],password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user10", email_address="user10@users.com", trainer=self.trainers[1],password="pswd22")
        self.users = list(User.objects.all())

    def test_methods(self):
        token1 = JwToken.create_session_token(self.admin.username, 'admin')
        token2 = JwToken.create_session_token(self.trainers[0].username, 'trainer')
        token3 = JwToken.create_session_token(self.trainers[1].username, 'trainer')
        request = ViewSupport.setup_request({'Session-Token': token2}, {})
        response = GetUsersOfTrainerView.get(GetUsersOfTrainerView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), get_users_data_for_upper(User.objects.filter(trainer=self.trainers[0])))
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': self.trainers[1].id})
        response = GetUsersOfTrainerView.post(GetUsersOfTrainerView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), get_users_data_for_upper(User.objects.filter(trainer=self.trainers[1])))
        request = ViewSupport.setup_request({'Session-Token': token1}, {})
        response = GetTrainersView.get(GetTrainersView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('trainers'), get_trainers_data(Trainer.objects.all()))
        id = self.users[9].id
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(User.objects.filter(id=id).exists())
        id = self.users[8].id
        request = ViewSupport.setup_request({'Session-Token': token2}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(User.objects.filter(id=id).exists())
        request = ViewSupport.setup_request({'Session-Token': token3}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(User.objects.filter(id=id).exists())
        id = self.trainers[1].id
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': id})
        response = DeleteTrainerView.post(DeleteTrainerView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(Trainer.objects.filter(id=id).exists())


class AchievementTestCase(TestCase):

    trainer = None
    user1 = None
    user2 = None

    def setUp(self) -> None:
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer = trainer
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password="Password1234")
        user1 = User.objects.get(first_name='Erik')
        user2 = User.objects.get(first_name='Jannis')
        self.user1 = user1
        self.user2 = user2

    def test_get_achievements_empty(self):
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.user1.username, 'user')}, {})
        response = GetAchievementsView.get(GetAchievementsView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('achievements'), [])
        self.assertEquals(response.data.get('data').get('nr_unachieved_hidden'), 0)


class LevelTestCase(TestCase):

    def setUp(self):
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer = trainer
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password="Password1234")
        user1 = User.objects.get(first_name='Erik')
        user2 = User.objects.get(first_name='Jannis')
        user2.xp = 400
        user2.save()
        self.user1 = user1
        self.user2 = user2

    def test_level(self):
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.user1.username, 'user')}, {'username': self.user1.username})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('level'), 0)
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.user1.username, 'user')}, {'username': self.user2.username})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('level'), 1)


class HandlingInvitesTestCase(TestCase):

    def setUp(self) -> None:
        trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer = trainer
        trainer2 = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerAndereTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer2 = trainer2
        token = JwToken.create_new_user_token(trainer.username, 'Jannis', 'Bauer', 'jannis@test.de', 'user')
        self.ot1 = OpenToken.objects.create(token=token, email='jannis@test.de', first_name='Jannis', last_name='Bauer', creator=trainer.username)
        token = JwToken.create_new_user_token(trainer2.username, 'Julian', 'Imhof', 'julian@test.de', 'user')
        self.ot2 = OpenToken.objects.create(token=token, email='julian@test.de', first_name='Julian', last_name='Imhof', creator=trainer2.username)
        self.token = JwToken.create_session_token('DerTrainer', 'trainer')

    def test_get(self):
        request = ViewSupport.setup_request({'Session-Token': self.token}, {})
        response = GetInvitedView.get(GetInvitedView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('invited'), get_invited_data([self.ot1,]))

    def test_invalidate(self):
        request = ViewSupport.setup_request({'Session-Token': self.token}, {'id': self.ot1.id})
        response = InvalidateInviteView.post(InvalidateInviteView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(OpenToken.objects.filter(id=self.ot1.id).exists())
        request = ViewSupport.setup_request({'Session-Token': self.token}, {'id': self.ot2.id})
        response = InvalidateInviteView.post(InvalidateInviteView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(OpenToken.objects.filter(id=self.ot2.id).exists())


class ProfileTestCase(TestCase):

    def setUp(self) -> None:
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('Passwort'.encode('utf8')).hexdigest()))
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('passwd'.encode('utf8')).hexdigest()))
        User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password=str(hashlib.sha3_256('passwdyo'.encode('utf8')).hexdigest()))
        user1 = User.objects.get(first_name='Erik')
        user2 = User.objects.get(first_name='Jannis')
        self.user1_id = user1.id
        self.user2_id = user2.id
        self.token1 = JwToken.create_session_token(trainer.username, 'trainer')
        self.token2 = JwToken.create_session_token(user1.username, 'user')
        self.token3 = JwToken.create_session_token(user2.username, 'user')

    def test_change_username(self):
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'username': 'neuerName'})
        response = ChangeUsernameView.post(ChangeUsernameView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.username, 'neuerName')
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'username': 'coolerName'})
        response = ChangeUsernameView.post(ChangeUsernameView, request)
        self.assertTrue(response.data.get('success'))
        user1 = User.objects.get(id=self.user1_id)
        self.assertEqual(user1.username, 'coolerName')

    def test_change_password(self):
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {
            'password': 'Passwort',
            'new_password': 'pswd_new'
        })
        response = ChangePasswordView.post(ChangePasswordView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.password, str(hashlib.sha3_256('pswd_new'.encode('utf8')).hexdigest()))
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {
            'password': 'passwd',
            'new_password': 'neue1234'
        })
        response = ChangePasswordView.post(ChangePasswordView, request)
        self.assertTrue(response.data.get('success'))
        user1 = User.objects.get(id=self.user1_id)
        self.assertEqual(user1.password, str(hashlib.sha3_256('neue1234'.encode('utf8')).hexdigest()))

    def test_change_avatar(self):
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'avatar': 1})
        response = ChangeAvatarView.post(ChangeAvatarView, request)
        self.assertTrue(response.data.get('success'))
        user2 = User.objects.get(id=self.user2_id)
        self.assertEqual(user2.avatar, 1)
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'avatar': 2})
        response = ChangeAvatarView.post(ChangeAvatarView, request)
        self.assertTrue(response.data.get('success'))
        user1 = User.objects.get(id=self.user1_id)
        self.assertEqual(user1.avatar, 2)

    def test_change_motivation(self):
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'motivation': 'Nieder mit der Schwerkraft, lang lebe der Leichtsinn'})
        response = ChangeMotovationView.post(ChangeMotovationView, request)
        self.assertTrue(response.data.get('success'))
        user2 = User.objects.get(id=self.user2_id)
        self.assertEqual(user2.motivation, 'Nieder mit der Schwerkraft, lang lebe der Leichtsinn')

    def test_profile_data(self):
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetProfileView.get(GetProfileView, request)
        self.assertTrue(response.data.get('success'))
        user2 = User.objects.get(id=self.user2_id)
        self.assertEqual(user2.username, response.data.get('data').get('username'))
        self.assertEqual(user2.avatar, response.data.get('data').get('avatar'))
        self.assertEqual(user2.first_login, response.data.get('data').get('first_login'))
        self.assertEqual(user2.motivation, response.data.get('data').get('motivation'))
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'telephone': '015712251102'})
        response = ChangeTrainerTelephoneView.post(ChangeTrainerTelephoneView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.telephone, '015712251102')
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'academia': 'dr. nat'})
        response = ChangeTrainerAcademiaView.post(ChangeTrainerAcademiaView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.academia, 'dr. nat')
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {
            'street': 'Straße',
            'house_nr': '4',
            'postal_code': '64287',
            'city': 'Darmstadt',
            'country': 'Deutschland',
            'address_add': ''
            })
        response = SetTrainerLocationView.post(SetTrainerLocationView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        loc = Location.objects.get()
        self.assertEqual(trainer.location, loc)
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetTrainerContactView.get(GetTrainerContactView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(response.data.get('data').get('name'), 'dr. nat Erik Prescher')
        self.assertEqual(response.data.get('data').get('address'), 'Straße 4, 64287 Darmstadt, Deutschland')
        self.assertEqual(trainer.telephone, response.data.get('data').get('telephone'))
        self.assertEqual(trainer.email_address, response.data.get('data').get('email'))

    def test_done_exercises_of_month(self):
        ex = Exercise.objects.create(title='Kniebeuge')
        trainer = Trainer.objects.get(id=self.trainer_id)
        plan = TrainingSchedule.objects.create(trainer=trainer)
        exip = ExerciseInPlan.objects.create(sets=1, repeats_per_set=10, exercise=ex, plan=plan)
        user = User.objects.get(id=self.user1_id)
        dex = DoneExercises.objects.create(exercise=exip, user=user, points=100, date=int(time.time()))
        now = datetime.datetime.now()
        result = get_done_exercises_of_month(now.month, now.year, user)
        '''[{
            "exercise_plan_id": dex.exercise.id,
            "id": dex.exercise.exercise.id,
            "date": dex.date,
            "points": dex.points
        }]'''
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {
            'year': now.year,
            'month': now.month
        })
        response = GetDoneExercisesOfMonthView.post(GetDoneExercisesOfMonthView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('done'), result)