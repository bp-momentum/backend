from django.db import models


class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name =  models.CharField(max_length=50)
    username =  models.CharField(max_length=50)
    password =  models.CharField(max_length=255)
    email_address = models.CharField(max_length=254, default="")
    refresh_token = models.CharField(max_length=255, null=True)
 


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
    date = models.DateField(default="1970-01-01")
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



class DoneExercises(models.Model):
    exercise =  models.ForeignKey(Exercise, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.DateField(default="1970-01-01")

class Admin(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, null=True)

class Friends(models.Model):
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend1')
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend2')
