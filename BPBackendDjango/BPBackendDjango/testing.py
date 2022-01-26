from django.http import request
from django.test import TestCase
from .Helperclasses.fortests import ViewSupport
from rest_framework import response
from django.test.utils import setup_test_environment
from .models import *
from .Helperclasses.jwttoken import JwToken
from .Views.achievementviews import GetAchievementsView
from .Views.userviews import *
from .Views.exerciseviews import *
from .Views.planviews import *

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
        #test cascade if Exercise is deleted
        Exercise.objects.filter(title='Kniebeuge').delete()
        self.assertFalse(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id))
        #recreate data
        Exercise.objects.create(title='Kniebeuge', description="Gehe in die Knie, achte...")
        ex = Exercise.objects.get(title='Kniebeuge')
        self.ex_id = ex.id
        ts = TrainingSchedule.objects.get(id=self.ts_id)
        ExerciseInPlan.objects.create(date="monday", sets=5, repeats_per_set=10, exercise=ex, plan=ts)
        #test cascade if Trainer is deleted
        Trainer.objects.filter(first_name="Erik").delete()
        self.assertFalse(User.objects.filter(first_name="Erik").exists())
        self.assertFalse(TrainingSchedule.objects.filter(id=self.ts_id).exists())
        self.assertFalse(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id))
        #recreate data        
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        user = User.objects.get(first_name="Erik")
        self.user_id = user.id
        TrainingSchedule.objects.create(trainer=trainer)
        ts = TrainingSchedule.objects.get(trainer=self.trainer_id)
        self.ts_id = ts.id
        ExerciseInPlan.objects.create(date="monday", sets=5, repeats_per_set=10, exercise=ex, plan=ts)
        user.plan = ts
        user.save()
        #delete plan
        TrainingSchedule.objects.filter(id=self.ts_id).delete()
        self.assertFalse(TrainingSchedule.objects.filter(id=self.ts_id).exists())
        user = User.objects.get(first_name="Erik")
        self.assertFalse(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id))
        self.assertEquals(user.plan, None)


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

#TODO edge cases
class TestUserViews(TestCase):

    trainer_id = 1
    user_id = 1
    trainer_token = None
    user_token = None
    user_refresh_token = None
    admin_token = None

    def setUp(self):
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256("Password1234".encode('utf8')).hexdigest()))
        Admin.objects.create(first_name="Erik", last_name="Prescher", username="derAdmin", password="Password1234")
        user = User.objects.get(first_name="Erik")
        self.user_id = user.id
        admin = Admin.objects.get(first_name="Erik")
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        self.user_token = JwToken.create_session_token(user.username, 'user')
        self.admin_token = JwToken.create_session_token(admin.username, 'admin')

    def test_delete_account(self):
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        response = DeleteAccountView.post(self=APIView, request=request) 
        self.assertTrue(response.data.get('success'))
        self.assertFalse(User.objects.filter(id=self.user_id).exists())
        #setup user again
        trainer = Trainer.objects.get(id=self.trainer_id)
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256("Password1234".encode('utf8')).hexdigest()))
        user = User.objects.get(first_name="Erik")
        self.user_id = user.id

    def test_login(self):
        #correct
        request = ViewSupport.setup_request({}, {
                'username': "DeadlyFarts",
                'password': "Password1234" 
            })
        response = LoginView.post(LoginView, request)
        self.assertTrue(response.data.get('success'))
        self.user_token = response.data.get('data').get('session_token')
        self.user_refresh_token = response.data.get('data').get('refresh_token')
        self.assertTrue(JwToken.check_session_token(self.user_token))
        self.assertTrue(JwToken.check_refresh_token(self.user_refresh_token))
        #invalid username
        request = ViewSupport.setup_request({}, {
                'username': "cooleKids",
                'password': "Password1234" 
            })
        response = LoginView.post(LoginView, request)
        self.assertFalse(response.data.get('success'))
        #invalid username
        request = ViewSupport.setup_request({}, {
                'username': "DeadlyFarts",
                'password': "wrong" 
            })
        response = LoginView.post(LoginView, request)
        self.assertFalse(response.data.get('success'))
    
    def test_register(self):
        #TODO
        self.assertTrue(True)

    def test_createUser(self):
        #TODO
        self.assertTrue(True)

    def test_auth(self):
        #correct
        request = ViewSupport.setup_request({}, {
                'refresh_token': self.user_refresh_token
            })
        if self.user_refresh_token == None:
            self.user_refresh_token = JwToken.create_refresh_token('DeadlyFarts', 'user', True)
        response = AuthView.post(AuthView, request)
        self.assertTrue(response.data.get('success'))
        #incorrect
        request = ViewSupport.setup_request({}, {
                'refresh_token': JwToken.create_refresh_token('DerTrainer', 'trainer', False)
            })
        response = AuthView.post(AuthView, request)
        self.assertFalse(response.data.get('success'))

    def test_logoutAllDevices(self):
        if self.user_refresh_token == None:
            self.user_refresh_token = JwToken.create_refresh_token('DeadlyFarts', 'user', True)
        self.assertTrue(JwToken.check_refresh_token(self.user_refresh_token).get('valid'))
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        response = LogoutAllDevicesView.post(LogoutAllDevicesView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(JwToken.check_refresh_token(self.user_refresh_token).get('valid')) #TODO failing


#TODO edge cases/every case
class TestExerciseView(TestCase):

    trainer_id = 1
    ex_id = 1
    trainer_token = None
    user_token = None
    admin_token = None

    def setUp(self):
        Exercise.objects.create(title='Kniebeuge', description='{"german": "Gehe in die Knie, achte...", "english": "Do squats..."}')
        Exercise.objects.create(title='Liegestütze', description='{"german": "Mache Liegestütze...", "english": "Do pushups..."}', activated=False)
        self.ex_id = Exercise.objects.get(title='Kniebeuge').id

        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        Admin.objects.create(first_name="Erik", last_name="Prescher", username="derAdmin", password="Password1234")
        user = User.objects.get(first_name="Erik")
        admin = Admin.objects.get(first_name="Erik")
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        self.user_token = JwToken.create_session_token(user.username, 'user')
        self.admin_token = JwToken.create_session_token(admin.username, 'admin')

    def test_get(self):
        #valid exercise
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'id': self.ex_id})
        response = GetExerciseView.post(GetExerciseView, request)
        self.assertTrue(response.data.get('success'))
        data = response.data.get('data')
        self.assertEquals(data.get('title'), 'Kniebeuge')
        self.assertEquals(data.get('description'), "Do squats...")
        self.assertEquals(data.get('video'), None)
        self.assertEquals(data.get('activated'), True)
        #invalid exercise
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token},{'id': 2543})
        response = GetExerciseView.post(GetExerciseView, request)
        self.assertFalse(response.data.get('success'))

    def test_get_list(self):
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {})
        response = GetExerciseListView.get(GetExerciseListView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(len(response.data.get('data').get('exercises')) == len(Exercise.objects.all()))


class TestPlanView(TestCase):

    trainer_token = None
    user_token = None
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
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        self.user_token = JwToken.create_session_token(user.username, 'user')

    def test_create_new(self):
        #without user
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {
            'name': 'test_plan',
            'exercise': [{
                "date": 'monday',
                "sets": 4,
                "repeats_per_set": 10,
                "id": self.ex_id
            }, {
                "date": 'wednesday',
                "sets": 3,
                "repeats_per_set": 10,
                "id": self.ex_id
            }]
        })
        response = CreatePlanView.post(CreatePlanView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(TrainingSchedule.objects.filter(id=int(response.data.get('data').get('plan_id'))).exists())
        #with user
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {
            'name': 'test_plan',
            'exercise': [{
                "date": 'monday',
                "sets": 4,
                "repeats_per_set": 10,
                "id": self.ex_id
            }, {
                "date": 'wednesday',
                "sets": 3,
                "repeats_per_set": 10,
                "id": self.ex_id
            }],
            'user': 'DeadlyFarts'
        })
        response = CreatePlanView.post(CreatePlanView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(TrainingSchedule.objects.filter(id=int(response.data.get('data').get('plan_id'))).exists())
        user = User.objects.get(first_name="Erik")
        self.assertEquals(user.plan.id, int(response.data.get('data').get('plan_id')))

    def test_create_change(self):
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {
            'name': 'test_plan',
            'exercise': [{
                "date": 'monday',
                "sets": 4,
                "repeats_per_set": 10,
                "id": self.ex_id
            }, {
                "date": 'wednesday',
                "sets": 3,
                "repeats_per_set": 10,
                "id": self.ex_id
            }],
            'id': self.ts_id
        })
        response = CreatePlanView.post(CreatePlanView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(TrainingSchedule.objects.filter(id=int(response.data.get('data').get('plan_id'))).exists())
        self.assertFalse(TrainingSchedule.objects.filter(id=self.ts_id).exists())
        self.ts_id = int(response.data.get('data').get('plan_id'))

    def test_add_user(self):
        TrainingSchedule.objects.create(name='addtouser_plan', trainer=Trainer.objects.get(id=self.trainer_id))
        self.ts_id = TrainingSchedule.objects.get(name='addtouser_plan').id
        User.objects.create(first_name="Jannis", last_name="Bauer", username="jbadV", trainer=Trainer.objects.get(id=self.trainer_id), email_address="fake@web.de", password="Password1234")
        #valid user and plan
        user = User.objects.get(username='jbadV')
        user.plan = None
        user.save()
        request = ViewSupport.setup_request({'Session-Token':  self.trainer_token}, {
            'plan': self.ts_id,
            'user': 'jbadV'
        })
        response = AddPlanToUserView.post(AddPlanToUserView, request)
        self.assertTrue(response.data.get('success'))
        user = User.objects.get(username='jbadV')
        self.assertEquals(user.plan.id, self.ts_id)
        #invalid user
        request = ViewSupport.setup_request({'Session-Token':  self.trainer_token}, {
            'plan': self.ts_id,
            'user': '1234567'
        })
        response = AddPlanToUserView.post(AddPlanToUserView, request)
        self.assertFalse(response.data.get('success'))
        #invalid plan
        user = User.objects.get(username='DeadlyFarts')
        user.plan = None
        user.save()
        request = ViewSupport.setup_request({'Session-Token':  self.trainer_id}, {
            'plan': -1,
            'user': 'DeadlyFarts'
        })
        response = AddPlanToUserView.post(AddPlanToUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(user.plan.id, None)

    def test_get_list(self):
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {})
        response = GetAllPlansView.get(GetAllPlansView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(len(response.data.get('data').get('plans')), len(TrainingSchedule.objects.filter(trainer=self.trainer_id)))

    def test_get(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'plan': self.ts_id})
        response = ShowPlanView.post(ShowPlanView, request)
        ts = TrainingSchedule.objects.get(id=self.ts_id)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('name'), ts.name)
        self.assertEquals(len(response.data.get('data').get('exercises')), len(ExerciseInPlan.objects.filter(plan=self.ts_id)))
        #invalid
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'plan': -1})
        response = ShowPlanView.post(ShowPlanView, request)
        self.assertFalse(response.data.get('success'))

    def test_get_for_user(self):
        user = User.objects.get(id=self.user_id)
        TrainingSchedule.objects.create(name='getfromuser_plan', trainer=Trainer.objects.get(id=self.trainer_id))
        ts = TrainingSchedule.objects.get(name='getfromuser_plan')
        #as user
        if user.plan == None:
            user.plan = ts
            user.save()
        elif not user.plan.id == ts.id:
            user.plan = ts
            user.save()
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(len(response.data.get('data').get('exercises')), len(ExerciseInPlan.objects.filter(plan=ts.id)))
        #as trainer
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'username': user.username})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(len(response.data.get('data').get('exercises')), len(ExerciseInPlan.objects.filter(plan=ts.id)))
        #invalid
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'username': 'user.username'})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertFalse(response.data.get('success'))

    def test_delete(self):
        #valid
        TrainingSchedule.objects.create(name='delete_plan', trainer=Trainer.objects.get(id=self.trainer_id))
        ts = TrainingSchedule.objects.get(name='delete_plan')
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'id': ts.id})
        response = DeletePlanView.post(DeletePlanView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(TrainingSchedule.objects.filter(id=ts.id).exists())
        #TODO invalid
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'id': -1})
        response = DeletePlanView.post(DeletePlanView, request)
        self.assertFalse(response.data.get('success'))
