from django.db import models


class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name =  models.CharField(max_length=50)
    username =  models.CharField(max_length=50)
    password =  models.CharField(max_length=255)
 
    
class TrainingSchedule(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    plan_data = models.FileField()

class Exercise(models.Model):
    description = models.TextField()
    video = models.FilePathField()
    title = models.CharField(max_length=255)
    activated = models.BooleanField()

class Team(models.Model):
    team_name = models.CharField(max_length=255)

class ExerciseInPlan(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    plan = models.ForeignKey(TrainingSchedule, on_delete=models.CASCADE)

class DoneExercises(models.Model):
    exercise =  models.ForeignKey(Exercise, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.DateField()

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True)
    o_auth_token = models.CharField(max_length=255)
    token_time = models.DateTimeField()

class Friends(models.Model):
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend1')
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend2')
