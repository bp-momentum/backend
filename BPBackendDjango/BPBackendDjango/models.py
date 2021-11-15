from django.db import models


class User(models.Models):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    trainer = models.ForeignKey(Trainer, on_delete=models.SETNULL)

class Trainer(models.Models):
    first_name = models.CharField(max_length=50)
    last_name =  models.CharField(max_length=50)
    username =  models.CharField(max_length=50)
    password =  models.CharField(max_length=255)
    
class TrainingSchedule(models.Models):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    plan_data = models.FileField()

class Exercise(models.Models):
    description = models.TextField()
    video = models.PathField()
    title = models.CharField(max_length=255)
    activated = models.NullBooleanField()

class Team(models.Models):
    team_name = models.CharField(max_length=255)

class ExerciseInPlan(models.Models):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    plan = models.ForeignKey(TrainingSchedule, on_delete=models.CASCADE)

class DoneExercises(models.Models):
    exercise =  models.ForeignKey(Exercise, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.DateField()

class Friends(models.Models):
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE)
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE)

    

