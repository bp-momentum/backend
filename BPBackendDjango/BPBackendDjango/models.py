from django.db import models
from django.db.models.deletion import CASCADE

class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    email_address = models.CharField(max_length=254, default="")
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="english")
    token_date = models.BigIntegerField(default=0)
    last_login = models.CharField(max_length=10, null=True)

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
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, default=0)
    email_address = models.CharField(max_length=254, default="")
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="english")
    plan = models.ForeignKey(TrainingSchedule, on_delete=models.SET_NULL, null=True)
    token_date = models.BigIntegerField(default=0)
    last_login = models.CharField(max_length=10, null=True)
    streak = models.IntegerField(default=0)
    xp = models.BigIntegerField(default=0)


class DoneExercises(models.Model):
    exercise = models.ForeignKey(ExerciseInPlan, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.BigIntegerField(default=0)


class Admin(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="english")
    token_date = models.BigIntegerField(default=0)


class Friends(models.Model):
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend1')
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend2')


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