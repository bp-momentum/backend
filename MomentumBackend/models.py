from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User


class TrainingSchedule(models.Model):
    name = models.CharField(default="plan", max_length=50)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_data = models.FileField(null=True)
    visible = models.BooleanField(default=True)


class Account(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)

    ADMIN = 0
    TRAINER = 1
    PLAYER = 2

    USER_TYPE_CHOICES = (
        (ADMIN, 'admin'),
        (TRAINER, 'trainer'),
        (PLAYER, 'player'),
    )

    role = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES, null=True, blank=True)

    language = models.CharField(max_length=20, default="de")

    # player specific data
    trainer = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="+")
    plan = models.ForeignKey(
        TrainingSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    streak = models.IntegerField(default=0)
    xp = models.BigIntegerField(default=0)
    avatarHairStyle = models.IntegerField(default=0)
    avatarHairColor = models.IntegerField(default=0)
    avatarSkinColor = models.IntegerField(default=0)
    avatarEyeColor = models.IntegerField(default=0)
    motivation = models.TextField(max_length=1000, default="")


class Leaderboard(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    speed = models.IntegerField(default=0)
    intensity = models.IntegerField(default=0)
    cleanliness = models.IntegerField(default=0)
    executions = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["-score"])]


class Invite(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=50)
    email = models.CharField(max_length=50)


class Exercise(models.Model):
    id = models.IntegerField(primary_key=True)
    _description = models.TextField(default='{}')
    _expectation = models.TextField(default='[]')

    def get_description(self):
        dict_value = getattr(self, '_description_dict', None)
        if not dict_value:
            import json
            dict_value = json.loads(self._description)
            setattr(self, '_description_dict', dict_value)
        return dict_value

    def set_description(self, new_desc):
        import json
        self._description = json.dumps(new_desc)
        self._description_dict = dict(new_desc)

    def get_expectation(self):
        dict_value = getattr(self, '_expectation_dict', None)
        if not dict_value:
            import json
            dict_value = json.loads(self._expectation)
            setattr(self, '_expectation_dict', dict_value)
        return dict_value

    def set_expectation(self, new_desc):
        import json
        self._expectation = json.dumps(new_desc)
        self._expectation_dict = list(new_desc)
    description = property(get_description, set_description)
    video = models.TextField(null=True)
    title = models.CharField(max_length=255)
    expectation = property(get_expectation, set_expectation)


class ExerciseInPlan(models.Model):
    date = models.CharField(default="monday", max_length=15)
    sets = models.IntegerField(default=0)
    repeats_per_set = models.IntegerField(default=0)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    plan = models.ForeignKey(TrainingSchedule, on_delete=models.CASCADE)


class ExerciseExecution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(
        ExerciseInPlan, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True)


class SetStats(models.Model):
    exercise = models.ForeignKey(ExerciseExecution, on_delete=models.CASCADE)
    set_uuid = models.CharField(max_length=50)
    set_nr = models.IntegerField()
    # actual values
    speed = models.IntegerField(default=0)
    accuracy = models.IntegerField(default=0)
    cleanliness = models.IntegerField(default=0)


class PlayerExercisePreferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    open_instruction_default = models.BooleanField(default=False)
    speed = models.IntegerField(default=10)  # FPS
