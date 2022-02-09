from django.db import models
from django.db.models.deletion import CASCADE

class Location(models.Model):
    street = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=12)
    country = models.CharField(max_length=64)
    city = models.CharField(max_length=128)
    house_nr = models.CharField(max_length=12)
    address_addition = models.CharField(max_length=128, default='')


class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, editable=True)
    password = models.CharField(max_length=255)
    email_address = models.CharField(max_length=254, default="")
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="en")
    token_date = models.BigIntegerField(default=0)
    last_login = models.CharField(max_length=10, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    academia = models.CharField(max_length=128, default='')
    telephone = models.CharField(max_length=32, default='')


class TrainingSchedule(models.Model):
    name = models.CharField(default="plan", max_length=50)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    plan_data = models.FileField(null=True)


class Exercise(models.Model):
    description = models.TextField(default="")
    video = models.FilePathField(null=True)
    title = models.CharField(max_length=255)
    activated = models.BooleanField(default=True)


class Team(models.Model):
    team_name = models.CharField(max_length=255)


class ExerciseInPlan(models.Model):
    date = models.CharField(default="monday", max_length=15)
    sets = models.IntegerField(default=0)
    repeats_per_set = models.IntegerField(default=0)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    plan = models.ForeignKey(TrainingSchedule, on_delete=models.CASCADE)


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, editable=True)
    password = models.CharField(max_length=255)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, default=0)
    email_address = models.CharField(max_length=254, default="")
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="en")
    plan = models.ForeignKey(TrainingSchedule, on_delete=models.SET_NULL, null=True)
    token_date = models.BigIntegerField(default=0)
    last_login = models.CharField(max_length=10, null=True)
    first_login = models.CharField(max_length=10, default="01-01-1970", editable=False)
    streak = models.IntegerField(default=0)
    xp = models.BigIntegerField(default=0)
    avatar = models.IntegerField(max_length=5, default=0)
    motivation = models.TextField(max_length=1000, default='')


class DoneExercises(models.Model):
    exercise = models.ForeignKey(ExerciseInPlan, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.BigIntegerField(default=0)


class Admin(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, editable=True)
    password = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="en")
    token_date = models.BigIntegerField(default=0)


class Friends(models.Model):
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend1')
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend2')
    since = models.DateField(null=True)
    accepted = models.BooleanField(default=False)


class Achievement(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(default="")
    hidden = models.BooleanField(default=False)
    

class UserAchievedAchievement(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    #date = models.BigIntegerField(default=0) #not useful at the moment

class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    score = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["-score"])]


class OpenToken(models.Model):
    token = models.CharField(max_length=512)
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    creator = models.CharField(max_length=50)