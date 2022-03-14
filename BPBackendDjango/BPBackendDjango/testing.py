from django.test import TestCase

from .models import Achievement, Admin, DoneExercises, Exercise, ExerciseInPlan, Friends, Leaderboard, Location, OpenToken, Trainer, TrainingSchedule, User, UserAchievedAchievement, UserMedalInExercise
from .settings import INTERN_SETTINGS
from .Helperclasses.fortests import ViewSupport
from .Helperclasses.jwttoken import JwToken
from .Helperclasses.handlers import ExerciseHandler, FriendHandler, InvitationsHandler, TrainerHandler, UserHandler
from .Views.leaderboardviews import ListLeaderboardView
from .Views.friendviews import AcceptRequestView, AddFriendView, DeclineRequestView, DeleteFriendView, GetMyFriendsView, GetPendingRequestView, GetProfileOfFriendView, GetRequestView
from .Views.userviews import AuthView, ChangeAvatarView, ChangeMotivationView, ChangePasswordView, ChangeTrainerAcademiaView, ChangeTrainerTelephoneView, ChangeUsernameView, CreateUserView, DeleteAccountView, DeleteTrainerView, DeleteUserView, GetInvitedView, GetListOfUsers, GetProfileView, GetStreakView, GetPasswordResetEmailView, GetTrainerContactView, GetUserLevelView, GetUsersOfTrainerView, GetTrainersView, InvalidateInviteView, LoginView, LogoutAllDevicesView, RegisterView, SearchUserView, SetPasswordResetEmailView, SetTrainerLocationView
from .Views.achievementviews import GetAchievementsView, ReloadAfterExerciseView, ReloadFriendAchievementView, GetMedals
from .Views.exerciseviews import DoneExerciseView, GetDoneExercisesOfMonthView, GetDoneExercisesView, GetExerciseListView, GetExerciseView
from .Views.planviews import AddPlanToUserView, CreatePlanView, DeletePlanView, GetAllPlansView, GetPlanOfUser, ShowPlanView
import hashlib
import time
import datetime

class UserTestCase(TestCase):

    trainer_id = 1

    def setUp(self):
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")

    def test_if_exists(self):
        #test if was created
        self.assertTrue(Trainer.objects.filter(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234").exists())
        self.assertTrue(User.objects.filter(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=self.trainer_id, email_address="prescher-erik@web.de", password="Password1234").exists())

    def test_if_user_gets_deleted_when_trainer_gets_deleted(self):
        #test if on_delete works as wanted
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
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer_id = trainer.id
        user1:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        user2:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password="Password1234")
        self.user_id = user1.id
        self.user_id_2 = user2.id
        exercise:Exercise = Exercise.objects.create(title='Squat', description='Just do it.')
        self.exercise_id = exercise.id
        plan:TrainingSchedule = TrainingSchedule.objects.create(name="testplan", trainer=trainer)
        exercise_plan:ExerciseInPlan = ExerciseInPlan.objects.create(exercise=exercise, plan=plan)
        DoneExercises.objects.create(exercise=exercise_plan, user=user1, points=98)
        self.done_ex_id = DoneExercises.objects.get(points=98).id
        Friends.objects.create(friend1=user1, friend2=user2)
        self.friends_id = Friends.objects.get(friend1=self.user_id).id

    def test_cascade(self):
        #test cascade of user
        User.objects.filter(id=self.user_id).delete()
        self.assertTrue(User.objects.filter(id=self.user_id_2).exists())
        self.assertTrue(Trainer.objects.filter(id=self.trainer_id).exists())
        self.assertTrue(Exercise.objects.filter(id=self.exercise_id).exists())
        self.assertFalse(User.objects.filter(id=self.user_id).exists())
        self.assertFalse(DoneExercises.objects.filter(id=self.done_ex_id).exists())
        self.assertFalse(Friends.objects.filter(id=self.friends_id).exists())


class ExerciseTestCase(TestCase):
    def setUp(self):
        Exercise.objects.create(title='Kniebeuge', description="Gehe in die Knie, achte...")
        Exercise.objects.create(title='Liegestütze', description="Mache Liegestütze", activated=False)

    def test_if_exists(self):
        #test if exist
        self.assertTrue(Exercise.objects.filter(title='Kniebeuge', description="Gehe in die Knie, achte...", video=None, activated=True).exists())
        self.assertTrue(Exercise.objects.filter(title='Liegestütze', description="Mache Liegestütze", video=None, activated=False).exists())

    def test_if_delete_works(self):
        #test delete
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
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer_id = trainer.id
        user:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        self.user_id = user.id
        ex:Exercise = Exercise.objects.create(title='Kniebeuge', description="Gehe in die Knie, achte...")
        self.ex_id = ex.id
        ts:TrainingSchedule = TrainingSchedule.objects.create(trainer=trainer)
        self.ts_id = ts.id
        ExerciseInPlan.objects.create(date="monday", sets=5, repeats_per_set=10, exercise=ex, plan=ts)
        user.plan = ts
        user.save()

    def test_if_exists(self):
        self.assertTrue(TrainingSchedule.objects.filter(trainer=self.trainer_id).exists())
        self.assertTrue(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id).exists())
        self.assertTrue(User.objects.filter(first_name="Erik").exists())
        user:User = User.objects.get(first_name="Erik")
        self.assertEquals(user.plan.id, self.ts_id)

    def test_if_related_deletes_work(self):
        #test cascade if Exercise is deleted
        Exercise.objects.filter(title='Kniebeuge').delete()
        self.assertFalse(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id))
        #recreate data
        Exercise.objects.create(title='Kniebeuge', description="Gehe in die Knie, achte...")
        ex:Exercise = Exercise.objects.get(title='Kniebeuge')
        self.ex_id = ex.id
        ts:TrainingSchedule = TrainingSchedule.objects.get(id=self.ts_id)
        ExerciseInPlan.objects.create(date="monday", sets=5, repeats_per_set=10, exercise=ex, plan=ts)
        #test cascade if Trainer is deleted
        Trainer.objects.filter(first_name="Erik").delete()
        self.assertFalse(User.objects.filter(first_name="Erik").exists())
        self.assertFalse(TrainingSchedule.objects.filter(id=self.ts_id).exists())
        self.assertFalse(ExerciseInPlan.objects.filter(exercise=self.ex_id, plan=self.ts_id))
        #recreate data        
        Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        trainer:Trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_id = trainer.id
        User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        user:User = User.objects.get(first_name="Erik")
        self.user_id = user.id
        ts:TrainingSchedule = TrainingSchedule.objects.create(trainer=trainer)
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

    admin:Admin = None
    trainers = []
    users = []

    def setUp(self) -> None:
        self.admin:Admin = Admin.objects.create(first_name="Erik", last_name="Prescher", username="DerAdmin", password="Password1234")
        self.trainers.append(Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234"))
        self.trainers.append(Trainer.objects.create(first_name="Jannis", last_name="Bauer", username="DerAndereTrainer", email_address="prescher-erik@web.de", password="Password1234"))
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
        token4 = JwToken.create_session_token(self.users[0].username, 'user')
        #trainer getting his user
        request = ViewSupport.setup_request({'Session-Token': token2}, {})
        response = GetUsersOfTrainerView.get(GetUsersOfTrainerView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data_for_upper(User.objects.filter(trainer=self.trainers[0])))
        #admin getting user of specific trainer
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': self.trainers[1].id})
        response = GetUsersOfTrainerView.post(GetUsersOfTrainerView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data_for_upper(User.objects.filter(trainer=self.trainers[1])))
        #admin getting trainers
        request = ViewSupport.setup_request({'Session-Token': token1}, {})
        response = GetTrainersView.get(GetTrainersView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('trainers'), TrainerHandler.get_trainers_data(Trainer.objects.all()))
        #trainer deleting user
        id = self.users[9].id
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(User.objects.filter(id=id).exists())
        #trainer not allowed to delete user
        id = self.users[8].id
        request = ViewSupport.setup_request({'Session-Token': token2}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(User.objects.filter(id=id).exists())
        #same user now deleted by his trainer
        request = ViewSupport.setup_request({'Session-Token': token3}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(User.objects.filter(id=id).exists())
        #admin deleting trainer
        id = self.trainers[1].id
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': id})
        response = DeleteTrainerView.post(DeleteTrainerView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(Trainer.objects.filter(id=id).exists())
        #invalid request
        #user not allowed to get users of trainer
        request = ViewSupport.setup_request({'Session-Token': token4}, {})
        response = GetUsersOfTrainerView.get(GetUsersOfTrainerView, request)
        self.assertFalse(response.data.get('success'))
        #invalid trainer
        request = ViewSupport.setup_request({'Session-Token': token4}, {})
        response = GetUsersOfTrainerView.get(GetUsersOfTrainerView, request)
        self.assertFalse(response.data.get('success'))
        #admin can not get users of himself
        request = ViewSupport.setup_request({'Session-Token': token1}, {})
        response = GetUsersOfTrainerView.get(GetUsersOfTrainerView, request)
        self.assertFalse(response.data.get('success'))
        #trainer not allowed to get other trainers users
        request = ViewSupport.setup_request({'Session-Token': token2}, {'id': self.trainers[1].id})
        response = GetUsersOfTrainerView.post(GetUsersOfTrainerView, request)
        self.assertFalse(response.data.get('success'))
        #user not allowed to get trainers users
        request = ViewSupport.setup_request({'Session-Token': token4}, {'id': self.trainers[1].id})
        response = GetUsersOfTrainerView.post(GetUsersOfTrainerView, request)
        self.assertFalse(response.data.get('success'))
        #trainer not allowed to get trainers
        request = ViewSupport.setup_request({'Session-Token': token2}, {})
        response = GetTrainersView.get(GetTrainersView, request)
        self.assertFalse(response.data.get('success'))
        #user not allowed to get trainers
        request = ViewSupport.setup_request({'Session-Token': token4}, {})
        response = GetTrainersView.get(GetTrainersView, request)
        self.assertFalse(response.data.get('success'))
        #user not allowed to delte other users
        id = self.users[4].id
        request = ViewSupport.setup_request({'Session-Token': token4}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(User.objects.filter(id=id).exists())
        #invalid user
        id = self.users[7].id
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': id})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertFalse(response.data.get('success'))
        #invalid trainer
        id = self.trainers[1].id
        request = ViewSupport.setup_request({'Session-Token': token1}, {'id': id})
        response = DeleteTrainerView.post(DeleteTrainerView, request)
        self.assertFalse(response.data.get('success'))
        self.assertFalse(Trainer.objects.filter(id=id).exists())
        #user can not delete trainer
        id = self.trainers[0].id
        request = ViewSupport.setup_request({'Session-Token': token4}, {'id': id})
        response = DeleteTrainerView.post(DeleteTrainerView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(Trainer.objects.filter(id=id).exists())
        #trainer can not delete itself (via this view)
        id = self.trainers[0].id
        request = ViewSupport.setup_request({'Session-Token': token2}, {'id': id})
        response = DeleteTrainerView.post(DeleteTrainerView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(Trainer.objects.filter(id=id).exists())
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetTrainersView.get(GetTrainersView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        request = ViewSupport.setup_request({}, {})
        response = GetUsersOfTrainerView.get(GetUsersOfTrainerView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        request = ViewSupport.setup_request({}, {})
        response = GetUsersOfTrainerView.post(GetUsersOfTrainerView, request)
        self.assertFalse(response.data.get('success'))
        request = ViewSupport.setup_request({}, {})
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])
        response = DeleteTrainerView.post(DeleteTrainerView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])
        request = ViewSupport.setup_request({}, {})
        response = DeleteUserView.post(DeleteUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])


class AchievementTestCase(TestCase):

    trainer:Trainer = None
    user1:User = None
    user2:User = None
    token1 = None
    token2 = None
    token3 = None
    achievement1:Achievement = None
    achievement2:Achievement = None

    def setUp(self) -> None:
        admin:Admin = Admin.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", password="Password1234")
        self.trainer:User = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.user1:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=self.trainer, email_address="prescher-erik@web.de", password="Password1234", streak=3)
        self.user2:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=self.trainer, email_address="test@bla.de", password="Password1234")
        self.token1 = JwToken.create_session_token(admin.username, 'admin')
        self.token2 = JwToken.create_session_token(self.trainer.username, 'trainer')
        self.token3 = JwToken.create_session_token(self.user1.username, 'user')
        self.achievement1:Achievement = Achievement.objects.create(name='streak', title='{"en":"Streak","de":"Streak"}', description='{"en": "get a streak", "de": "sammel eine Streak"}', icon='{"4":"www.test.de/streak4","3":"www.test.de/streak3","2":"www.test.de/streak2","1":"www.test.de/streak1","0":"www.test.de/streak0"}')
        self.achievement2:Achievement = Achievement.objects.create(name='havingFriends', title='{"en":"A Friend!","de":"Freundschaft!"}', description='{"en": "add a friend", "de": "habe einen Freund"}', icon='{"1":"www.test.de/friends1","0":"www.test.de/friends0"}')

    def test_get_achievements(self):
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetAchievementsView.get(GetAchievementsView, request)
        self.assertTrue(response.data.get('success'))
        expected = [{
            'name': 'doneExercises',
            'title': 'Done Exercises',
            'description': "Do exercises to get/level this achievement",
            'level': 0,
            'progress': '0/10',
            'hidden': False,
            'icon': 'https://cdn.geoscribble.de/achievements/doneExercises_0.svg'
        }, {
            'name': 'havingFriends',
            'title': 'A Friend!',
            'description': "add a friend",
            'level': 0,
            'progress': '0/1',
            'hidden': False,
            'icon': "www.test.de/friends0"
        }, {
            'name': 'streak',
            'title': 'Streak',
            'description': "get a streak",
            'level': 1,
            'progress': '3/7',
            'hidden': False,
            'icon': "www.test.de/streak1"
        }, {
            'name': 'perfectExercise',
            'title': 'Perfect Exercise',
            'description': "Complete an exercise with 100 percent",
            'level': 0,
            'progress': '0/1',
            'hidden': False,
            'icon': 'https://cdn.geoscribble.de/achievements/perfectExercise_0.svg'
        }]
        actual = response.data.get('data').get('achievements')
        self.assertEquals(len(actual), len(expected))
        for i in actual:
            self.assertTrue(expected.__contains__(i))
        for i in expected:
            self.assertTrue(actual.__contains__(i))
        self.assertEquals(response.data.get('data').get('nr_unachieved_hidden'), 2)
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetAchievementsView.get(GetAchievementsView, request)
        self.assertFalse(response.data.get('success'))
        #trainer not allowed to
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.trainer.username, 'trainer')}, {})
        response = GetAchievementsView.get(GetAchievementsView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetAchievementsView.get(GetAchievementsView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])

    def test_reload_friends(self):
        Friends.objects.create(friend1=self.user1, friend2=self.user2, accepted=True)
        #valid
        #changed
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = ReloadFriendAchievementView.get(ReloadFriendAchievementView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('achievements'), {
            'name': 'havingFriends',
            'title': 'A Friend!',
            'description': "add a friend",
            'level': 1,
            'progress': 'done',
            'hidden': False,
            'icon': "www.test.de/friends1"
        })
        #nothing changed
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = ReloadFriendAchievementView.get(ReloadFriendAchievementView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data'), {})
        #invalid
        #as Trainer not possible
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = ReloadFriendAchievementView.get(ReloadFriendAchievementView, request)
        self.assertFalse(response.data.get('success'))
        #as Admin not possible
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = ReloadFriendAchievementView.get(ReloadFriendAchievementView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetAchievementsView.get(GetAchievementsView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ReloadFriendAchievementView.get(ReloadFriendAchievementView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #delete Friends again
        Friends.objects.all().delete()

    def test_reload_exercise(self):
        #valid
        #change
        self.user1.streak = 7
        self.user1.save(force_update=True)
        self.user1:User = User.objects.get(username=self.user1.username)
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = ReloadAfterExerciseView.get(ReloadAfterExerciseView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('achievements'), [{
            'name': 'streak',
            'title': 'Streak',
            'description': "get a streak",
            'level': 2,
            'progress': '7/30',
            'hidden': False,
            'icon': "www.test.de/streak2"
        }])
        #no change
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = ReloadAfterExerciseView.get(ReloadAfterExerciseView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data'), {})
        #invalid
        #as Trainer not possible
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = ReloadAfterExerciseView.get(ReloadAfterExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #as Admin not possible
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = ReloadAfterExerciseView.get(ReloadAfterExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = ReloadAfterExerciseView.get(ReloadAfterExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ReloadAfterExerciseView.get(ReloadAfterExerciseView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])

    def test_streak(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetStreakView.get(GetStreakView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('days'), 3)
        self.assertTrue(response.data.get('data').get('flame_glow'))
        self.assertEquals(response.data.get('data').get('flame_height'), 0.3)
        #invalid
        #as Trainer not possible
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetStreakView.get(GetStreakView, request)
        self.assertFalse(response.data.get('success'))
        #as Admin not possible
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetStreakView.get(GetStreakView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetStreakView.get(GetStreakView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetStreakView.get(GetStreakView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])


class LevelTestCase(TestCase):

    user1:User = None
    user2:User = None

    def setUp(self):
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer = trainer
        user1:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        user2:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password="Password1234")
        user2.xp = 400
        user2.save()
        self.user1:User = user1
        self.user2:User = user2

    def test_level(self):
        #user getting own level
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.user1.username, 'user')}, {'username': self.user1.username})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('level'), 0)
        #user getting level of another user
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.user1.username, 'user')}, {'username': self.user2.username})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('level'), 1)
        #trainer getting user's level
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.trainer.username, 'trainer')}, {'username': self.user2.username})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('level'), 1)
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'ìnvalid'}, {'username': self.user2.username})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertFalse(response.data.get('success'))
        #trainers have no level
        request = ViewSupport.setup_request({'Session-Token': JwToken.create_session_token(self.trainer.username, 'trainer')}, {'username': self.trainer.username})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetUserLevelView.post(GetUserLevelView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['username'])


class HandlingInvitesTestCase(TestCase):

    def setUp(self) -> None:
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer = trainer
        trainer2:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerAndereTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer2 = trainer2
        token = JwToken.create_new_user_token(trainer.username, 'Jannis', 'Bauer', 'jannis@test.de', 'user')
        self.ot1:OpenToken = OpenToken.objects.create(token=token, email='jannis@test.de', first_name='Jannis', last_name='Bauer', creator=trainer.username)
        token = JwToken.create_new_user_token(trainer2.username, 'Julian', 'Imhof', 'julian@test.de', 'user')
        self.ot2:OpenToken = OpenToken.objects.create(token=token, email='julian@test.de', first_name='Julian', last_name='Imhof', creator=trainer2.username)
        self.token = JwToken.create_session_token('DerTrainer', 'trainer')

    def test_get(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.token}, {})
        response = GetInvitedView.get(GetInvitedView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('invited'), InvitationsHandler.get_invited_data([self.ot1,]))
        #invalid
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetInvitedView.get(GetInvitedView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetInvitedView.get(GetInvitedView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])

    def test_invalidate(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.token}, {'id': self.ot1.id})
        response = InvalidateInviteView.post(InvalidateInviteView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(OpenToken.objects.filter(id=self.ot1.id).exists())
        #invalid
        #not allowed to delete
        request = ViewSupport.setup_request({'Session-Token': self.token}, {'id': self.ot2.id})
        response = InvalidateInviteView.post(InvalidateInviteView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(OpenToken.objects.filter(id=self.ot2.id).exists())
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'id': self.ot2.id})
        response = InvalidateInviteView.post(InvalidateInviteView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = InvalidateInviteView.post(InvalidateInviteView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])


class ProfileTestCase(TestCase):

    def setUp(self) -> None:
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('Passwort'.encode('utf8')).hexdigest()))
        self.trainer_id = trainer.id
        user1:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('passwd'.encode('utf8')).hexdigest()))
        user2:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password=str(hashlib.sha3_256('passwdyo'.encode('utf8')).hexdigest()))
        self.user1_id = user1.id
        self.user2_id = user2.id
        self.token1 = JwToken.create_session_token(trainer.username, 'trainer')
        self.token2 = JwToken.create_session_token(user1.username, 'user')
        self.token3 = JwToken.create_session_token(user2.username, 'user')

    def test_change_username(self):
        #valid
        #triner
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'username': 'neuerName'})
        response = ChangeUsernameView.post(ChangeUsernameView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.username, 'neuerName')
        #user
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'username': 'coolerName'})
        response = ChangeUsernameView.post(ChangeUsernameView, request)
        self.assertTrue(response.data.get('success'))
        user1:User = User.objects.get(id=self.user1_id)
        self.assertEqual(user1.username, 'coolerName')
        #invalid
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'username': 'coolerName'})
        response = ChangeUsernameView.post(ChangeUsernameView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ChangeUsernameView.post(ChangeUsernameView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['username'])

    def test_change_password(self):
        #valid
        #trainer
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {
            'password': 'Passwort',
            'new_password': 'pswd_new'
        })
        response = ChangePasswordView.post(ChangePasswordView, request)
        self.assertTrue(response.data.get('success'))
        trainer:Trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.password, str(hashlib.sha3_256('pswd_new'.encode('utf8')).hexdigest()))
        #user
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {
            'password': 'passwd',
            'new_password': 'neue1234'
        })
        response = ChangePasswordView.post(ChangePasswordView, request)
        self.assertTrue(response.data.get('success'))
        user1:User = User.objects.get(id=self.user1_id)
        self.assertEqual(user1.password, str(hashlib.sha3_256('neue1234'.encode('utf8')).hexdigest()))
        #invalid
        #wrong password
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {
            'password': 'wrong',
            'new_password': 'neverReached'
        })
        response = ChangePasswordView.post(ChangePasswordView, request)
        self.assertFalse(response.data.get('success'))
        user2:User = User.objects.get(id=self.user2_id)
        self.assertEqual(user2.password, str(hashlib.sha3_256('passwdyo'.encode('utf8')).hexdigest()))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {
            'password': 'wrong',
            'new_password': 'neverReached'
        })
        response = ChangePasswordView.post(ChangePasswordView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ChangePasswordView.post(ChangePasswordView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['password', 'new_password'])

    def test_change_avatar(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'avatar': 1})
        response = ChangeAvatarView.post(ChangeAvatarView, request)
        self.assertTrue(response.data.get('success'))
        user2:User = User.objects.get(id=self.user2_id)
        self.assertEqual(user2.avatar, 1)
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'avatar': 2})
        response = ChangeAvatarView.post(ChangeAvatarView, request)
        self.assertTrue(response.data.get('success'))
        user1:User = User.objects.get(id=self.user1_id)
        self.assertEqual(user1.avatar, 2)
        #invalid
        #trainer not allowed
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'avatar': 1})
        response = ChangeAvatarView.post(ChangeAvatarView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'avatar': 1})
        response = ChangeAvatarView.post(ChangeAvatarView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ChangeAvatarView.post(ChangeAvatarView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['avatar'])

    def test_change_motivation(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'motivation': 'Nieder mit der Schwerkraft, lang lebe der Leichtsinn'})
        response = ChangeMotivationView.post(ChangeMotivationView, request)
        self.assertTrue(response.data.get('success'))
        user2:User = User.objects.get(id=self.user2_id)
        self.assertEqual(user2.motivation, 'Nieder mit der Schwerkraft, lang lebe der Leichtsinn')
        #invalid
        #trainer not able to use
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'motivation': 'Nieder mit der Schwerkraft, lang lebe der Leichtsinn'})
        response = ChangeMotivationView.post(ChangeMotivationView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'motivation': 'Nieder mit der Schwerkraft, lang lebe der Leichtsinn'})
        response = ChangeMotivationView.post(ChangeMotivationView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ChangeMotivationView.post(ChangeMotivationView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['motivation'])

    def test_profile_data(self):
        #valid
        #get profile
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetProfileView.get(GetProfileView, request)
        self.assertTrue(response.data.get('success'))
        user2:User = User.objects.get(id=self.user2_id)
        self.assertEqual(user2.username, response.data.get('data').get('username'))
        self.assertEqual(user2.avatar, response.data.get('data').get('avatar'))
        self.assertEqual(user2.first_login, response.data.get('data').get('first_login'))
        self.assertEqual(user2.motivation, response.data.get('data').get('motivation'))
        #change telephone number of trainer
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'telephone': '015712251102'})
        response = ChangeTrainerTelephoneView.post(ChangeTrainerTelephoneView, request)
        self.assertTrue(response.data.get('success'))
        trainer:Trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.telephone, '015712251102')
        #change academia of trainer
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'academia': 'dr. nat'})
        response = ChangeTrainerAcademiaView.post(ChangeTrainerAcademiaView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(trainer.academia, 'dr. nat')
        #change location of trainer
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
        loc:Location = Location.objects.get()
        self.assertEqual(trainer.location, loc)
        #user gets trainers contact
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetTrainerContactView.get(GetTrainerContactView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(response.data.get('data').get('name'), 'dr. nat Erik Prescher')
        self.assertEqual(response.data.get('data').get('address'), 'Straße 4, 64287 Darmstadt, Deutschland')
        self.assertEqual(trainer.telephone, response.data.get('data').get('telephone'))
        self.assertEqual(trainer.email_address, response.data.get('data').get('email'))
        #trainer gets its contact
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetTrainerContactView.get(GetTrainerContactView, request)
        self.assertTrue(response.data.get('success'))
        trainer = Trainer.objects.get(id=self.trainer_id)
        self.assertEqual(response.data.get('data').get('name'), 'dr. nat Erik Prescher')
        self.assertEqual(response.data.get('data').get('academia'), 'dr. nat')
        self.assertEqual(response.data.get('data').get('street'), 'Straße')
        self.assertEqual(response.data.get('data').get('city'), 'Darmstadt')
        self.assertEqual(response.data.get('data').get('country'), 'Deutschland')
        self.assertEqual(response.data.get('data').get('address_addition'), '')
        self.assertEqual(response.data.get('data').get('postal_code'), '64287')
        self.assertEqual(response.data.get('data').get('house_nr'), '4')
        self.assertEqual(trainer.telephone, response.data.get('data').get('telephone'))
        self.assertEqual(trainer.email_address, response.data.get('data').get('email'))
        #invalid
        #trainer not allowed to get profile
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetProfileView.get(GetProfileView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetProfileView.get(GetProfileView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetProfileView.get(GetProfileView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #user not able to change telephone number
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'telephone': '015712251102'})
        response = ChangeTrainerTelephoneView.post(ChangeTrainerTelephoneView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'telephone': '015712251102'})
        response = ChangeTrainerTelephoneView.post(ChangeTrainerTelephoneView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ChangeTrainerTelephoneView.post(ChangeTrainerTelephoneView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['telephone'])
        #user not able to change academia
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'academia': 'dr. nat'})
        response = ChangeTrainerAcademiaView.post(ChangeTrainerAcademiaView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'academia': 'dr. nat'})
        response = ChangeTrainerAcademiaView.post(ChangeTrainerAcademiaView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ChangeTrainerAcademiaView.post(ChangeTrainerAcademiaView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['academia'])
        #user not able to change location
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {
            'street': 'Straße',
            'house_nr': '4',
            'postal_code': '64287',
            'city': 'Darmstadt',
            'country': 'Deutschland',
            'address_add': ''
            })
        response = SetTrainerLocationView.post(SetTrainerLocationView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {
            'street': 'Straße',
            'house_nr': '4',
            'postal_code': '64287',
            'city': 'Darmstadt',
            'country': 'Deutschland',
            'address_add': ''
            })
        response = SetTrainerLocationView.post(SetTrainerLocationView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = SetTrainerLocationView.post(SetTrainerLocationView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['street', 'postal_code', 'country', 'city', 'house_nr', 'address_add'])
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetTrainerContactView.get(GetTrainerContactView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetTrainerContactView.get(GetTrainerContactView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])

    def test_done_exercises_of_month(self):
        #additional setup
        ex:Exercise = Exercise.objects.create(title='Kniebeuge')
        trainer:Trainer = Trainer.objects.get(id=self.trainer_id)
        plan:TrainingSchedule = TrainingSchedule.objects.create(trainer=trainer)
        exip:ExerciseInPlan = ExerciseInPlan.objects.create(sets=1, repeats_per_set=10, exercise=ex, plan=plan)
        user:User = User.objects.get(id=self.user1_id)
        dex:DoneExercises = DoneExercises.objects.create(exercise=exip, user=user, points=100, date=int(time.time()))
        now = datetime.datetime.now()
        #valid
        result = ExerciseHandler.get_done_exercises_of_month(now.month, now.year, user)
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
        #invalid
        #trainer not able to
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {
            'year': now.year,
            'month': now.month
        })
        response = GetDoneExercisesOfMonthView.post(GetDoneExercisesOfMonthView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {
            'year': now.year,
            'month': now.month
        })
        response = GetDoneExercisesOfMonthView.post(GetDoneExercisesOfMonthView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetDoneExercisesOfMonthView.post(GetDoneExercisesOfMonthView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['month', 'year'])


class TestUserViews(TestCase):

    trainer_id = 1
    user_id = 1
    admin_id = 1
    trainer_token = None
    user_token = None
    user_refresh_token = None
    admin_token = None
    new_user_token = None
    new_trainer_token = None

    def setUp(self):
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer_id = trainer.id
        user:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256("Password1234".encode('utf8')).hexdigest()))
        admin:Admin = Admin.objects.create(first_name="Erik", last_name="Prescher", username="derAdmin", password="Password1234")
        self.user_id = user.id
        self.admin_id = admin.id
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        self.user_token = JwToken.create_session_token(user.username, 'user')
        self.admin_token = JwToken.create_session_token(admin.username, 'admin')

    def test_delete_account(self):
        #valid token
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        response = DeleteAccountView.post(DeleteAccountView, request=request) 
        self.assertTrue(response.data.get('success'))
        self.assertFalse(User.objects.filter(id=self.user_id).exists())
        #invalid
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = DeleteAccountView.post(DeleteAccountView, request=request) 
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = DeleteAccountView.post(DeleteAccountView, request=request) 
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #setup user again
        trainer:Trainer = Trainer.objects.get(id=self.trainer_id)
        user:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256("Password1234".encode('utf8')).hexdigest()))
        self.user_id = user.id
        self.user_token = JwToken.create_session_token(user.username, 'user')

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
        #invalid
        #invalid username
        request = ViewSupport.setup_request({}, {
                'username': "cooleKids",
                'password': "Password1234" 
            })
        response = LoginView.post(LoginView, request)
        self.assertFalse(response.data.get('success'))
        #invalid pasword
        request = ViewSupport.setup_request({}, {
                'username': "DeadlyFarts",
                'password': "wrong" 
            })
        response = LoginView.post(LoginView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = LoginView.post(LoginView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), [])
        self.assertEquals(response.data.get('data').get('data'), ['username', 'password'])
    
    def test_register(self):
        #register user
        if self.new_user_token == None:
            trainer:Trainer = Trainer.objects.get(id=self.trainer_id)
            self.new_user_token = JwToken.create_new_user_token(trainer.username, 'Jannis', 'Bauer', 'bptestmail52@gmail.com', 'user')
            OpenToken.objects.create(token=self.new_user_token, email='bptestmail52@gmail.com', first_name='Jannis', last_name='Bauer', creator=trainer.username)
        request = ViewSupport.setup_request({}, {
            'username': 'jbad',
            'password': '1234567890',
            'new_user_token': self.new_user_token
        })
        response = RegisterView.post(RegisterView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(User.objects.filter(username='jbad').exists())
        #not again possible
        request = ViewSupport.setup_request({}, {
            'username': 'jbad',
            'password': '1234567890',
            'new_user_token': self.new_user_token
        })
        response = RegisterView.post(RegisterView, request)
        self.assertFalse(response.data.get('success'))
        #register trainer
        if self.new_trainer_token == None:
            admin:Admin = Admin.objects.get(id=self.admin_id)
            self.new_trainer_token = JwToken.create_new_user_token(admin.username, 'Jannis', 'Bauer', 'bptestmail52@gmail.com', 'trainer')
            OpenToken.objects.create(token=self.new_trainer_token, email='bptestmail52@gmail.com', first_name='Jannis', last_name='Bauer', creator=trainer.username)
        request = ViewSupport.setup_request({}, {
            'username': 'Notjbad',
            'password': '1234567890',
            'new_user_token': self.new_trainer_token
        })
        response = RegisterView.post(RegisterView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(Trainer.objects.filter(username='Notjbad').exists())
        #invalid
        #invalid token
        request = ViewSupport.setup_request({}, {
            'username': 'againjbad',
            'password': '1234567890',
            'new_user_token': 'invalid'
        })
        response = RegisterView.post(RegisterView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = RegisterView.post(RegisterView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), [])
        self.assertEquals(response.data.get('data').get('data'), ['password', 'username', 'new_user_token'])

    def test_createUser(self):
        trainer:Trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        #create user
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {
            'first_name': 'Jannis',
            'last_name': 'Bauer',
            'email_address': 'bptestmail52@gmail.com',
            'url': 'bptest.com'
        })
        response = CreateUserView.post(CreateUserView, request)
        self.assertTrue(response.data.get('success'))
        self.new_user_token = response.data.get('data').get('new_user_token')
        #create trainer
        request = ViewSupport.setup_request({'Session-Token': self.admin_token}, {
            'first_name': 'Jannis',
            'last_name': 'Bauer',
            'email_address': 'bptestmail52@gmail.com',
            'url': 'bptest.com'
        })
        response = CreateUserView.post(CreateUserView, request)
        self.assertTrue(response.data.get('success'))
        self.new_trainer_token = response.data.get('data').get('new_user_token')
        #invalid
        #user not allowed to
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {
            'first_name': 'Jannis',
            'last_name': 'Bauer',
            'email_address': 'bptestmail52@gmail.com',
            'url': 'bptest.com'
        })
        response = CreateUserView.post(CreateUserView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {
            'first_name': 'Jannis',
            'last_name': 'Bauer',
            'email_address': 'bptestmail52@gmail.com',
            'url': 'bptest.com'
        })
        response = CreateUserView.post(CreateUserView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = CreateUserView.post(CreateUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['first_name', 'last_name', 'email_address', 'url'])

    def test_auth(self):
        #correct
        if self.user_refresh_token == None:
            self.user_refresh_token = JwToken.create_refresh_token('DeadlyFarts', 'user', True)
        request = ViewSupport.setup_request({}, {
                'refresh_token': self.user_refresh_token
            })
        response = AuthView.post(AuthView, request)
        self.assertTrue(response.data.get('success'))
        #invalid
        #incorrect
        request = ViewSupport.setup_request({}, {
                'refresh_token': 'justsomeinvalidstuff'
            })
        response = AuthView.post(AuthView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = AuthView.post(AuthView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), [])
        self.assertEquals(response.data.get('data').get('data'), ['refresh_token'])

    def test_logoutAllDevices(self):
        #valid
        if self.user_refresh_token == None:
            self.user_refresh_token = JwToken.create_refresh_token('DeadlyFarts', 'user', True)
        self.assertTrue(JwToken.check_refresh_token(self.user_refresh_token).get('valid'))
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        time.sleep(10)
        response = LogoutAllDevicesView.post(LogoutAllDevicesView, request)
        self.assertTrue(response.data.get('success'))
        request = ViewSupport.setup_request({}, {
                'refresh_token': self.user_refresh_token
            })
        response = AuthView.post(AuthView, request)
        self.assertFalse(response.data.get('success'))
        #invalid
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = LogoutAllDevicesView.post(LogoutAllDevicesView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = LogoutAllDevicesView.post(LogoutAllDevicesView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])


class TestExerciseView(TestCase):

    trainer_id = 1
    ex_id = 1
    trainer_token = None
    user_token = None
    admin_token = None

    def setUp(self):
        Exercise.objects.create(title='Kniebeuge', description='{"de": "Gehe in die Knie, achte...", "en": "Do squats..."}')
        Exercise.objects.create(title='Liegestütze', description='{"de": "Mache Liegestütze...", "en": "Do pushups..."}', activated=False)
        self.ex_id = Exercise.objects.get(title='Kniebeuge').id

        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer_id = trainer.id
        user:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        admin:Admin = Admin.objects.create(first_name="Erik", last_name="Prescher", username="derAdmin", password="Password1234")
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
        #invalid
        #invalid exercise
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token},{'id': 2543})
        response = GetExerciseView.post(GetExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #admin not allowed
        request = ViewSupport.setup_request({'Session-Token': self.admin_token},{'id': self.ex_id})
        response = GetExerciseView.post(GetExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'},{'id': self.ex_id})
        response = GetExerciseView.post(GetExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({},{})
        response = GetExerciseView.post(GetExerciseView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])

    def test_get_list(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {})
        response = GetExerciseListView.get(GetExerciseListView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(len(response.data.get('data').get('exercises')) == len(Exercise.objects.all()))
        #invalid
        #user not allowed
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        response = GetExerciseListView.get(GetExerciseListView, request)
        self.assertFalse(response.data.get('success'))
        #admin not allowed
        request = ViewSupport.setup_request({'Session-Token': self.admin_token}, {})
        response = GetExerciseListView.get(GetExerciseListView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetExerciseListView.get(GetExerciseListView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetExerciseListView.get(GetExerciseListView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])


class TestPlanView(TestCase):

    trainer_token = None
    user_token = None
    trainer_id = 0
    user_id = 0
    ex_id = 0
    ts_id = 0

    def setUp(self):
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer_id = trainer.id
        user:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234")
        self.user_id = user.id
        ex:Exercise = Exercise.objects.create(title='Kniebeuge', description="Gehe in die Knie, achte...")
        self.ex_id = ex.id
        ts:TrainingSchedule = TrainingSchedule.objects.create(trainer=trainer)
        self.ts_id = ts.id
        ExerciseInPlan.objects.create(date="monday", sets=5, repeats_per_set=10, exercise=ex, plan=ts)
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        self.user_token = JwToken.create_session_token(user.username, 'user')

    def test_create_new(self):
        trainer:Trainer = Trainer.objects.get(first_name="Erik")
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        #valid
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
        #invalid
        #user not allowed
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {
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
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {
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
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = CreatePlanView.post(CreatePlanView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['name', 'exercise'])

    def test_create_change(self):
        #valid
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
        self.ts_id = int(response.data.get('data').get('plan_id'))
        #invalid
        #user not allowed
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {
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
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {
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
        self.assertFalse(response.data.get('success'))
        #missing arguments (same as create cause id is optional argument)
        request = ViewSupport.setup_request({}, {})
        response = CreatePlanView.post(CreatePlanView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['name', 'exercise'])

    def test_add_user(self):
        INTERN_SETTINGS['last_leaderboard_reset'] = time.time()
        TrainingSchedule.objects.create(name='addtouser_plan', trainer=Trainer.objects.get(id=self.trainer_id))
        self.ts_id = TrainingSchedule.objects.get(name='addtouser_plan').id
        user:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbadV", trainer=Trainer.objects.get(id=self.trainer_id), email_address="fake@web.de", password="Password1234")
        #valid user and plan
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
        #invalid
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
        user = User.objects.get(username='DeadlyFarts')
        self.assertEquals(user.plan, None)
        #user not allowed to
        request = ViewSupport.setup_request({'Session-Token':  self.user_token}, {
            'plan': self.ts_id,
            'user': 'DeadlyFarts'
        })
        response = AddPlanToUserView.post(AddPlanToUserView, request)
        self.assertFalse(response.data.get('success'))
        user = User.objects.get(username='DeadlyFarts')
        self.assertEquals(user.plan, None)
        #invalid token
        request = ViewSupport.setup_request({'Session-Token':  'invalid'}, {
            'plan': self.ts_id,
            'user': 'DeadlyFarts'
        })
        response = AddPlanToUserView.post(AddPlanToUserView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = AddPlanToUserView.post(AddPlanToUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['user'])

    def test_get_list(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {})
        response = GetAllPlansView.get(GetAllPlansView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(len(response.data.get('data').get('plans')), len(TrainingSchedule.objects.filter(trainer=self.trainer_id)))
        #invalid
        #user not allowed to
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        response = GetAllPlansView.get(GetAllPlansView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetAllPlansView.get(GetAllPlansView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetAllPlansView.get(GetAllPlansView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])

    def test_get(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'plan': self.ts_id})
        response = ShowPlanView.post(ShowPlanView, request)
        ts:TrainingSchedule = TrainingSchedule.objects.get(id=self.ts_id)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('name'), ts.name)
        self.assertEquals(len(response.data.get('data').get('exercises')), len(ExerciseInPlan.objects.filter(plan=self.ts_id)))
        #invalid
        #invalid plan
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'plan': -1})
        response = ShowPlanView.post(ShowPlanView, request)
        self.assertFalse(response.data.get('success'))
        #user not allowed
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {'plan': self.ts_id})
        response = ShowPlanView.post(ShowPlanView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'plan': self.ts_id})
        response = ShowPlanView.post(ShowPlanView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ShowPlanView.post(ShowPlanView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['plan'])

    def test_get_for_user(self):
        #valid
        user:User = User.objects.get(id=self.user_id)
        ts:TrainingSchedule = TrainingSchedule.objects.create(name='getfromuser_plan', trainer=Trainer.objects.get(id=self.trainer_id))
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
        #invalid user
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'username': 'user.username'})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertFalse(response.data.get('success'))
        #invalid token as user
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertFalse(response.data.get('success'))
        #invalid token as trainer
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'username': user.username})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #missing arguments as trainer
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {})
        response = GetPlanOfUser.post(GetPlanOfUser, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), [])
        self.assertEquals(response.data.get('data').get('data'), ['username'])

    def test_delete(self):
        #valid
        ts:TrainingSchedule = TrainingSchedule.objects.create(name='delete_plan', trainer=Trainer.objects.get(id=self.trainer_id))
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'id': ts.id})
        response = DeletePlanView.post(DeletePlanView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(TrainingSchedule.objects.filter(id=ts.id).exists())
        #invalid
        #invalid plan
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'id': -1})
        response = DeletePlanView.post(DeletePlanView, request)
        self.assertFalse(response.data.get('success'))
        ts = TrainingSchedule.objects.create(name='delete_plan', trainer=Trainer.objects.get(id=self.trainer_id))
        #user not allowed
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {'id': ts.id})
        response = DeletePlanView.post(DeletePlanView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(TrainingSchedule.objects.filter(id=ts.id).exists())
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'id': ts.id})
        response = DeletePlanView.post(DeletePlanView, request)
        self.assertFalse(response.data.get('success'))
        self.assertTrue(TrainingSchedule.objects.filter(id=ts.id).exists())
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = DeletePlanView.post(DeletePlanView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])


class TestLeaderboardView(TestCase):

    trainer_id = None
    trainer_token = None
    user_token = None
    users = []

    def setUp(self) -> None:
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.trainer_id = trainer.id
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        ts:TrainingSchedule = TrainingSchedule.objects.create(name='plan_for_everyone', trainer=trainer)
        ex:Exercise = Exercise.objects.create(title='Kniebeuge')
        ExerciseInPlan.objects.create(exercise=ex, plan=ts, sets=1, repeats_per_set=1)
        User.objects.create(first_name="vorname", last_name="nachname", username="user1", email_address="user1@users.com", trainer=trainer,password="pswd22", plan=ts)
        User.objects.create(first_name="vorname", last_name="nachname", username="user2", email_address="user2@users.com", trainer=trainer,password="pswd22", plan=ts)
        User.objects.create(first_name="vorname", last_name="nachname", username="user3", email_address="user3@users.com", trainer=trainer,password="pswd22", plan=ts)
        User.objects.create(first_name="vorname", last_name="nachname", username="user4", email_address="user4@users.com", trainer=trainer, password="pswd22", plan=ts)
        User.objects.create(first_name="vorname", last_name="nachname", username="user5", email_address="user5@users.com", trainer=trainer,password="pswd22", plan=ts)
        self.users = User.objects.all()
        score = 60
        for user in self.users:
            Leaderboard.objects.create(user=user, score=score, cleanliness=score, intensity=score, speed=score, executions=1)
            if score == 80:
                self.user_token = JwToken.create_session_token(user.username, 'user')
            score += 10

    def test_get(self):
        INTERN_SETTINGS['last_leaderboard_reset'] = time.time()
        self.maxDiff = None
        #as trainer
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'count': 3})
        response = ListLeaderboardView.post(ListLeaderboardView, request)
        self.assertTrue(response.data.get('success'))
        leaderboard = []
        entry = Leaderboard.objects.get(score=100)
        leaderboard.append({"rank": 1, "username": 'vorname nachname', "score": 100})
        entry = Leaderboard.objects.get(score=90)
        leaderboard.append({"rank": 2, "username": 'vorname nachname', "score": 90})
        entry = Leaderboard.objects.get(score=80)
        leaderboard.append({"rank": 3, "username": 'vorname nachname', "score": 80})

        get_response = []
        for ent in response.data.get('data').get('leaderboard'):
            get_response.append({"rank": ent.get('rank'), "username": ent.get('username'), "score": ent.get('score')})

        self.assertEquals(get_response, leaderboard)
        #as user
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {'count': 3})
        response = ListLeaderboardView.post(ListLeaderboardView, request)
        self.assertTrue(response.data.get('success'))
        leaderboard = []
        entry:Leaderboard = Leaderboard.objects.get(score=90)
        leaderboard.append({"rank": 1, "username": entry.user.username, "score": 90})
        entry = Leaderboard.objects.get(score=80)
        leaderboard.append({"rank": 2, "username": entry.user.username, "score": 80})
        entry = Leaderboard.objects.get(score=70)
        leaderboard.append({"rank": 3, "username": entry.user.username, "score": 70})
        get_response = []
        for ent in response.data.get('data').get('leaderboard'):
            get_response.append({"rank": ent.get('rank'), "username": ent.get('username'), "score": ent.get('score')})

        self.assertEquals(get_response, leaderboard)
        #invalid
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'count': 3})
        response = ListLeaderboardView.post(ListLeaderboardView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = ListLeaderboardView.post(ListLeaderboardView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['count'])


class TestDoneExercise(TestCase):

    trainer_id = 1
    ex = None
    trainer_token = None
    user_token = None
    admin_token = None
    user = None
    exip_id = 0

    def setUp(self) -> None:
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        self.ex:Exercise = Exercise.objects.create(title='Kniebeuge', description='{"de": "Gehe in die Knie, achte...", "en": "Do squats..."}')
        ts:TrainingSchedule = TrainingSchedule.objects.create(trainer=trainer)
        exip:ExerciseInPlan = ExerciseInPlan.objects.create(date="monday", sets=5, repeats_per_set=10, exercise=self.ex_id, plan=ts)
        self.exip_id = exip.id
        self.trainer_id = trainer.id
        user:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password="Password1234", plan=ts)
        admin:Admin = Admin.objects.create(first_name="Erik", last_name="Prescher", username="derAdmin", password="Password1234")
        user.plan = ts
        user.save(force_update=True)
        self.user:User = User.objects.get(username='DeadlyFarts')
        self.trainer_token = JwToken.create_session_token(trainer.username, 'trainer')
        self.user_token = JwToken.create_session_token(user.username, 'user')
        self.admin_token = JwToken.create_session_token(admin.username, 'admin')
        Leaderboard.objects.create(user=User.objects.get(username=self.user.username), score=0)

    def test_do_exercise(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {'exercise_plan_id': self.exip_id})
        response = DoneExerciseView.post(DoneExerciseView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(DoneExercises.objects.all().exists())
        #invalid
        #already done
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {'exercise_plan_id': self.exip_id})
        response = DoneExerciseView.post(DoneExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #invalid exercise in plan
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {'exercise_plan_id': 5412654})
        response = DoneExerciseView.post(DoneExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #admin not allowed to
        request = ViewSupport.setup_request({'Session-Token': self.admin_token}, {'exercise_plan_id': self.exip_id})
        response = DoneExerciseView.post(DoneExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #trainer not allowed to
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'exercise_plan_id': self.exip_id})
        response = DoneExerciseView.post(DoneExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'exercise_plan_id': self.exip_id})
        response = DoneExerciseView.post(DoneExerciseView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = DoneExerciseView.post(DoneExerciseView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['exercise_plan_id'])

    def test_get_done(self): #not working, issue with method in tests
        #valid
        #as user
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {})
        response = GetDoneExercisesView.get(GetDoneExercisesView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data, ExerciseHandler.get_done(self.user))
        #as trainer
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'user': self.user.username})
        response = GetDoneExercisesView.post(GetDoneExercisesView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data, ExerciseHandler.get_done(self.user))
        #invalid
        #trainer cant call user method
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {})
        response = GetDoneExercisesView.get(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        #admin cant call user method
        request = ViewSupport.setup_request({'Session-Token': self.admin_token}, {})
        response = GetDoneExercisesView.get(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token for user method
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetDoneExercisesView.get(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments for user method
        request = ViewSupport.setup_request({}, {})
        response = GetDoneExercisesView.get(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #invalid user for trainer
        request = ViewSupport.setup_request({'Session-Token': self.trainer_token}, {'user': 'unknown'})
        response = GetDoneExercisesView.post(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        #user cant call trainer method
        request = ViewSupport.setup_request({'Session-Token': self.user_token}, {'user': self.user.username})
        response = GetDoneExercisesView.post(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        #admin cant call trainer method
        request = ViewSupport.setup_request({'Session-Token': self.admin_token}, {'user': self.user.username})
        response = GetDoneExercisesView.post(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token for trainer method
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'user': self.user.username})
        response = GetDoneExercisesView.post(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments for trainer method
        request = ViewSupport.setup_request({}, {})
        response = GetDoneExercisesView.post(GetDoneExercisesView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['user'])


class TestFriendSystem(TestCase):

    users = []
    admin = None
    trainer = None
    token1 = None
    token2 = None
    token3 = None
    token4 = None
    token5 = None

    def setUp(self) -> None:
        self.admin:Admin = Admin.objects.create(first_name="Erik", last_name="Prescher", username="DerAdmin", password="Password1234")
        self.trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password="Password1234")
        User.objects.create(first_name="vorname", last_name="nachname", username="user1", email_address="user1@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user2", email_address="user2@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user3", email_address="user3@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user4", email_address="user4@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user5", email_address="user5@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user6", email_address="user6@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user7", email_address="user7@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user8", email_address="user8@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user9", email_address="user9@users.com", trainer=self.trainer,password="pswd22")
        User.objects.create(first_name="vorname", last_name="nachname", username="user10", email_address="user10@users.com", trainer=self.trainer,password="pswd22")
        self.users = list(User.objects.all())
        self.token1 = JwToken.create_session_token(self.admin.username, 'admin')
        self.token2 = JwToken.create_session_token(self.trainer.username, 'trainer')
        self.token3 = JwToken.create_session_token(self.users[0].username, 'user')
        self.token4 = JwToken.create_session_token(self.users[1].username, 'user')
        self.token5 = JwToken.create_session_token(self.users[2].username, 'user')

    def test_system(self):
        #valid
        #user1 adds user2
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'username': 'user2'})
        response = AddFriendView.post(AddFriendView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(Friends.objects.filter(friend1=self.users[0], friend2=self.users[1], accepted=False).exists())
        #user2 adds user1
        request = ViewSupport.setup_request({'Session-Token': self.token4}, {'username': 'user1'})
        response = AddFriendView.post(AddFriendView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(Friends.objects.filter(friend1=self.users[1], friend2=self.users[0], accepted=False).exists())
        #user1 adds user3
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'username': 'user3'})
        response = AddFriendView.post(AddFriendView, request)
        self.assertTrue(response.data.get('success'))
        self.assertTrue(Friends.objects.filter(friend1=self.users[0], friend2=self.users[2], accepted=False).exists())
        #user1 get requests
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetRequestView.get(GetRequestView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(len(response.data.get('data').get('requests')), 1)
        self.assertEquals(response.data.get('data').get('requests'), FriendHandler.get_requests(self.users[0]))
        #user1 get pending
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetPendingRequestView.get(GetPendingRequestView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(len(response.data.get('data').get('pending')), 2)
        self.assertEquals(response.data.get('data').get('pending'), FriendHandler.get_pending_requests(self.users[0]))
        #user1 accepts from user2
        id = Friends.objects.get(friend1=self.users[1], friend2=self.users[0], accepted=False).id
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'id': id})
        response = AcceptRequestView.post(AcceptRequestView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(Friends.objects.filter(friend1=self.users[1], friend2=self.users[0], accepted=False).exists())
        self.assertTrue(Friends.objects.filter(friend1=self.users[1], friend2=self.users[0], accepted=True).exists())
        self.assertFalse(Friends.objects.filter(friend1=self.users[0], friend2=self.users[1]).exists())
        #user3 declines from user1
        id = Friends.objects.get(friend1=self.users[0], friend2=self.users[2], accepted=False).id
        request = ViewSupport.setup_request({'Session-Token': self.token5}, {'id': id})
        response = DeclineRequestView.post(DeclineRequestView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(Friends.objects.filter(friend1=self.users[0], friend2=self.users[2]).exists())
        #user1 get friends
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetMyFriendsView.get(GetMyFriendsView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(len(response.data.get('data').get('friends')), 1)
        self.assertEquals(response.data.get('data').get('friends'), FriendHandler.get_friends(self.users[0]))
        #user1 delete friend (user2)
        id = Friends.objects.get(friend1=self.users[1], friend2=self.users[0], accepted=True).id
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'id': id})
        response = DeleteFriendView.post(DeleteFriendView, request)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(Friends.objects.filter(friend1=self.users[1], friend2=self.users[0]).exists())
        #invalid
        #admin not able to use
        #add
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'username': 'user2'})
        response = AddFriendView.post(AddFriendView, request)
        self.assertFalse(response.data.get('success'))
        #requests
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetRequestView.get(GetRequestView, request)
        self.assertFalse(response.data.get('success'))
        #pending requests
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetPendingRequestView.get(GetPendingRequestView, request)
        self.assertFalse(response.data.get('success'))
        #friends
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetMyFriendsView.get(GetMyFriendsView, request)
        self.assertFalse(response.data.get('success'))
        #accept
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'id': 1})
        response = AcceptRequestView.post(AcceptRequestView, request)
        self.assertFalse(response.data.get('success'))
        #decline
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'id': 1})
        response = DeclineRequestView.post(DeclineRequestView, request)
        self.assertFalse(response.data.get('success'))
        #delete
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'id': 1})
        response = DeleteFriendView.post(DeleteFriendView, request)
        self.assertFalse(response.data.get('success'))
        #trainers not able to use
        #add
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'username': 'user2'})
        response = AddFriendView.post(AddFriendView, request)
        self.assertFalse(response.data.get('success'))
        #requests
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetRequestView.get(GetRequestView, request)
        self.assertFalse(response.data.get('success'))
        #pending requests
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetPendingRequestView.get(GetPendingRequestView, request)
        self.assertFalse(response.data.get('success'))
        #friends
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetMyFriendsView.get(GetMyFriendsView, request)
        self.assertFalse(response.data.get('success'))
        #accept
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'id': 1})
        response = AcceptRequestView.post(AcceptRequestView, request)
        self.assertFalse(response.data.get('success'))
        #decline
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'id': 1})
        response = DeclineRequestView.post(DeclineRequestView, request)
        self.assertFalse(response.data.get('success'))
        #delete
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'id': 1})
        response = DeleteFriendView.post(DeleteFriendView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        #add
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'username': 'user2'})
        response = AddFriendView.post(AddFriendView, request)
        self.assertFalse(response.data.get('success'))
        #requests
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetRequestView.get(GetRequestView, request)
        self.assertFalse(response.data.get('success'))
        #pending requests
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetPendingRequestView.get(GetPendingRequestView, request)
        self.assertFalse(response.data.get('success'))
        #friends
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetMyFriendsView.get(GetMyFriendsView, request)
        self.assertFalse(response.data.get('success'))
        #accept
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'id': 1})
        response = AcceptRequestView.post(AcceptRequestView, request)
        self.assertFalse(response.data.get('success'))
        #decline
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'id': 1})
        response = DeclineRequestView.post(DeclineRequestView, request)
        self.assertFalse(response.data.get('success'))
        #delete
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'id': 1})
        response = DeleteFriendView.post(DeleteFriendView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        #add
        request = ViewSupport.setup_request({}, {})
        response = AddFriendView.post(AddFriendView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['username'])
        #requests
        request = ViewSupport.setup_request({}, {})
        response = GetRequestView.get(GetRequestView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #pending requests
        request = ViewSupport.setup_request({}, {})
        response = GetPendingRequestView.get(GetPendingRequestView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #friends
        request = ViewSupport.setup_request({}, {})
        response = GetMyFriendsView.get(GetMyFriendsView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])
        #accept
        request = ViewSupport.setup_request({}, {})
        response = AcceptRequestView.post(AcceptRequestView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])
        #decline
        request = ViewSupport.setup_request({}, {})
        response = DeclineRequestView.post(DeclineRequestView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])
        #delete
        request = ViewSupport.setup_request({}, {})
        response = DeleteFriendView.post(DeleteFriendView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['id'])

    def test_pattern_search(self):
        #valid
        #as admin
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'search': 'user1'})
        response = SearchUserView.post(SearchUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data([User.objects.get(username='user1'), User.objects.get(username='user10')]))
        #as trainer
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'search': 'user1'})
        response = SearchUserView.post(SearchUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data([User.objects.get(username='user1'), User.objects.get(username='user10')]))
        #as user
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'search': 'user1'})
        response = SearchUserView.post(SearchUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data([User.objects.get(username='user10')]))
        #empty
        request = ViewSupport.setup_request({'Session-Token': self.token4}, {'search': 'del'})
        response = SearchUserView.post(SearchUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data([]))
        #invalid
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'search': 'del'})
        response = SearchUserView.post(SearchUserView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = SearchUserView.post(SearchUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['search'])

    def test_get_list(self):
        #valid
        #as admin
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetListOfUsers.get(SearchUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data(User.objects.all()))
        #as trainer
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetListOfUsers.get(SearchUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data(User.objects.all()))
        #as user
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {})
        response = GetListOfUsers.get(SearchUserView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('users'), UserHandler.get_users_data(User.objects.all().exclude(username='user1')))
        #invalid
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetListOfUsers.get(SearchUserView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetListOfUsers.get(SearchUserView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])


class TestResetPassword(TestCase):

    token2 = None
    token3 = None
    user_id = 0
    trainer_id = 0

    def setUp(self) -> None:
        trainer:Trainer = Trainer.objects.create(first_name="Jannis", last_name="Bauer", username="DerTrainer", email_address="bptestmail52@gmail.com", password=str(hashlib.sha3_256('Passwort'.encode('utf8')).hexdigest()))
        self.trainer_id = trainer.id
        user:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="derNutzer", trainer=trainer, email_address="bptestmail52@gmail.com", password=str(hashlib.sha3_256('passwd'.encode('utf8')).hexdigest()))
        self.user_id = user.id
        self.token2 = JwToken.create_reset_password_token('DerTrainer')
        self.token3 = JwToken.create_reset_password_token('derNutzer')

    def test_send(self):
        #valid
        #user
        request = ViewSupport.setup_request({}, {
            'username': 'derNutzer',
            'url': 'www.test/#/'
        })
        response = GetPasswordResetEmailView.post(GetPasswordResetEmailView, request)
        self.assertTrue(response.data.get('success'))
        '''not implemented yet
        #trainer
        request = ViewSupport.setup_request({}, {
            'username': 'DerTrainer',
            'url': 'www.test/#/'
        })
        response = GetPasswordResetEmailView.post(GetPasswordResetEmailView, request)
        self.assertTrue(response.data.get('success'))'''
        #invalid
        #invalid username
        request = ViewSupport.setup_request({}, {
            'username': 'invalid',
            'url': 'www.test/#/'
        })
        response = GetPasswordResetEmailView.post(GetPasswordResetEmailView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetPasswordResetEmailView.post(GetPasswordResetEmailView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), [])
        self.assertEquals(response.data.get('data').get('data'), ['username', 'url'])

    def test_change(self):
        #valid
        #user
        request = ViewSupport.setup_request({}, {
            'reset_token': self.token3,
            'new_password': 'newFancy'
        })
        response = SetPasswordResetEmailView.post(SetPasswordResetEmailView, request)
        self.assertTrue(response.data.get('success'))
        user:User = User.objects.get(id=self.user_id)
        self.assertEquals(user.password, str(hashlib.sha3_256('newFancy'.encode('utf8')).hexdigest()))
        '''not implemented yet
        #trainer
        request = ViewSupport.setup_request({}, {
            'reset_token': self.token2,
            'new_password': 'newFancy'
        })
        response = SetPasswordResetEmailView.post(SetPasswordResetEmailView, request)
        self.assertTrue(response.data.get('success'))
        user = Trainer.objects.get(id=self.trainer_id)
        self.assertEquals(user.password, str(hashlib.sha3_256('newFancy'.encode('utf8')).hexdigest()))'''
        #invalid
        #invalid token
        request = ViewSupport.setup_request({}, {
            'reset_token': 'invalid',
            'new_password': 'newFancy'
        })
        response = SetPasswordResetEmailView.post(SetPasswordResetEmailView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = SetPasswordResetEmailView.post(SetPasswordResetEmailView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), [])
        self.assertEquals(response.data.get('data').get('data'), ['reset_token', 'new_password'])


class TestMedals(TestCase):

    user1_id = 0
    user2_id = 2
    trainer_id = 0
    umixs = []
    token1 = None
    token2 = None
    token3 = None

    def setUp(self) -> None:
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('Passwort'.encode('utf8')).hexdigest()))
        self.trainer_id = trainer.id
        user1:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('passwd'.encode('utf8')).hexdigest()))
        user2:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password=str(hashlib.sha3_256('passwdyo'.encode('utf8')).hexdigest()))
        self.user1_id = user1.id
        self.user2_id = user2.id
        self.token1 = JwToken.create_session_token(trainer.username, 'trainer')
        self.token2 = JwToken.create_session_token(user1.username, 'user')
        self.token3 = JwToken.create_session_token(user2.username, 'user')
        ex1 = Exercise.objects.create(title='Kniebeuge')
        ex2 = Exercise.objects.create(title='Liegestütze')
        UserMedalInExercise.objects.create(user=user1, gold=2, silver=5, exercise=ex1)
        UserMedalInExercise.objects.create(user=user1, gold=4, bronze=3, exercise=ex2)
        UserMedalInExercise.objects.create(user=user2, gold=6, silver=1, exercise=ex1)
        UserMedalInExercise.objects.create(user=user2, gold=1, silver=2, bronze=4, exercise=ex2)
        self.umixs = list(UserMedalInExercise.objects.all())

    def test_get(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {})
        response = GetMedals.get(GetMedals, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('medals'), [{
            'exercise': 'Kniebeuge',
            'gold': 2,
            'silver': 5,
            'bronze': 0
        },{
            'exercise': 'Liegestütze',
            'gold': 4,
            'silver': 0,
            'bronze': 3
        }])
        request = ViewSupport.setup_request({'Session-Token': self.token3},{})
        response = GetMedals.get(GetMedals, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('medals'), [{
            'exercise': 'Kniebeuge',
            'gold': 6,
            'silver': 1,
            'bronze': 0
        },{
            'exercise': 'Liegestütze',
            'gold': 1,
            'silver': 2,
            'bronze': 4
        }])
        #invalid
        #trainer not allowed
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {})
        response = GetMedals.get(GetMedals, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {})
        response = GetMedals.get(GetMedals, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetMedals.get(GetMedals, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), [])


class TestProfileOfFriends(TestCase):

    token1 = None
    token2 = None
    token3 = None
    
    def setUp(self) -> None:
        trainer:Trainer = Trainer.objects.create(first_name="Erik", last_name="Prescher", username="DerTrainer", email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('Passwort'.encode('utf8')).hexdigest()))
        user1:User = User.objects.create(first_name="Erik", last_name="Prescher", username="DeadlyFarts", trainer=trainer, email_address="prescher-erik@web.de", password=str(hashlib.sha3_256('passwd'.encode('utf8')).hexdigest()), avatar=5, motivation='Krise', xp=20)
        user2:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbad", trainer=trainer, email_address="test@bla.de", password=str(hashlib.sha3_256('passwdyo'.encode('utf8')).hexdigest()), avatar=2, motivation='Gute Tage', xp=5000)
        user3:User = User.objects.create(first_name="Jannis", last_name="Bauer", username="jbadV", trainer=trainer, email_address="test@bla.de", password=str(hashlib.sha3_256('passwdyo'.encode('utf8')).hexdigest()), avatar=4, motivation='Es lebe der Leichtsinn', xp=60000)
        Friends.objects.create(friend1=user1, friend2=user2, accepted=True)
        Friends.objects.create(friend1=user1, friend2=user3, accepted=False)
        self.token1 = JwToken.create_session_token(trainer.username, 'trainer')
        self.token2 = JwToken.create_session_token(user1.username, 'user')
        self.token3 = JwToken.create_session_token(user2.username, 'user')
        achievement:Achievement = Achievement.objects.create(name='streak', description='{"en": "get a streak"}')
        UserAchievedAchievement.objects.create(achievement=achievement, level=1, user=user2, date=time.time())

    def test(self):
        #valid
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'username': 'jbad'})
        response = GetProfileOfFriendView.post(GetProfileOfFriendView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data'), {
            'username': 'jbad',
            'level': UserHandler.calc_level(5000, 200)[0],
            'level_progress': UserHandler.calc_level(5000, 200)[1],
            'avatar': 2,
            'motivation': 'Gute Tage',
            'last_login': None,
            'days': 0,
            'flame_height': 0.0,
            'last_achievements': [{
                'name': 'streak',
                'icon': None
            }]
        })
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'username': 'DeadlyFarts'})
        response = GetProfileOfFriendView.post(GetProfileOfFriendView, request)
        self.assertTrue(response.data.get('success'))
        self.assertEquals(response.data.get('data'), {
            'username': 'DeadlyFarts',
            'level': 0,
            'level_progress': UserHandler.calc_level(20, 200)[1],
            'avatar': 5,
            'motivation': 'Krise',
            'last_login': None,
            'days': 0,
            'flame_height': 0.0,
            'last_achievements': []
        })
        #invalid
        #not friends
        request = ViewSupport.setup_request({'Session-Token': self.token3}, {'username': 'jbadV'})
        response = GetProfileOfFriendView.post(GetProfileOfFriendView, request)
        self.assertFalse(response.data.get('success'))
        #not accepted
        request = ViewSupport.setup_request({'Session-Token': self.token2}, {'username': 'jbadV'})
        response = GetProfileOfFriendView.post(GetProfileOfFriendView, request)
        self.assertFalse(response.data.get('success'))
        #trainer not allowed to
        request = ViewSupport.setup_request({'Session-Token': self.token1}, {'username': 'jbadV'})
        response = GetProfileOfFriendView.post(GetProfileOfFriendView, request)
        self.assertFalse(response.data.get('success'))
        #invalid token
        request = ViewSupport.setup_request({'Session-Token': 'invalid'}, {'username': 'jbadV'})
        response = GetProfileOfFriendView.post(GetProfileOfFriendView, request)
        self.assertFalse(response.data.get('success'))
        #missing arguments
        request = ViewSupport.setup_request({}, {})
        response = GetProfileOfFriendView.post(GetProfileOfFriendView, request)
        self.assertFalse(response.data.get('success'))
        self.assertEquals(response.data.get('data').get('header'), ['Session-Token'])
        self.assertEquals(response.data.get('data').get('data'), ['username'])