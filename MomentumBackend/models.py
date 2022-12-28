from django.db import models
from django.db.models.deletion import CASCADE
from django.forms import BooleanField


class Location(models.Model):
    street = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=12)
    country = models.CharField(max_length=64)
    city = models.CharField(max_length=128)
    house_nr = models.CharField(max_length=12)
    address_addition = models.CharField(max_length=128, default="")


class Trainer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, editable=True, unique=True)
    password = models.CharField(max_length=255)
    email_address = models.CharField(max_length=254, default="")
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="de")
    token_date = models.BigIntegerField(default=0)
    last_login = models.CharField(max_length=10, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    academia = models.CharField(max_length=128, default="")
    telephone = models.CharField(max_length=32, default="")


class TrainingSchedule(models.Model):
    name = models.CharField(default="plan", max_length=50)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    plan_data = models.FileField(null=True)
    visable = models.BooleanField(default=True)


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


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, editable=True, unique=True)
    password = models.CharField(max_length=255)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, default=0)
    email_address = models.CharField(max_length=254, default="")
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="de")
    plan = models.ForeignKey(TrainingSchedule, on_delete=models.SET_NULL, null=True)
    token_date = models.BigIntegerField(default=0)
    last_login = models.CharField(max_length=10, null=True)
    first_login = models.CharField(max_length=10, default="1970-01-01", editable=False)
    streak = models.IntegerField(default=0)
    xp = models.BigIntegerField(default=0)
    avatarHairStyle = models.IntegerField(default=0)
    avatarHairColor = models.IntegerField(default=0)
    avatarSkinColor = models.IntegerField(default=0)
    avatarEyeColor = models.IntegerField(default=0)
    motivation = models.TextField(max_length=1000, default="")


class DoneExercises(models.Model):
    exercise = models.ForeignKey(ExerciseInPlan, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.BigIntegerField(default=0)
    current_set = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    intensity = models.IntegerField(default=0)
    cleanliness = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)


class NoInstructionExercises(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Admin(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, editable=True, unique=True)
    password = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=20, default="de")
    token_date = models.BigIntegerField(default=0)


class Friends(models.Model):
    friend1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend1")
    friend2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend2")
    accepted = models.BooleanField(default=False)


class Achievement(models.Model):
    name = models.CharField(max_length=50, unique=True)
    _title = models.TextField(default='{}')
    def get_title(self):
        dict_value = getattr(self, '_title_dict', None)
        if not dict_value:
            import json
            dict_value = json.loads(self._title)
            setattr(self, '_title_dict', dict_value)
        return dict_value
    def set_title(self, new_title):
        import json
        self._title = json.dumps(new_title)
        self._title_dict = dict(new_title)
    title = property(get_title, set_title)
    _description = models.TextField(default='{}')
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
    description = property(get_description, set_description)
    hidden = models.BooleanField(default=False)
    icon = models.TextField(default="{ }")


class UserAchievedAchievement(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    date = models.BigIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["-date"])]


class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    speed = models.IntegerField(default=0)
    intensity = models.IntegerField(default=0)
    cleanliness = models.IntegerField(default=0)
    executions = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["-score"])]


class OpenToken(models.Model):
    token = models.CharField(max_length=512)
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    creator = models.CharField(max_length=50)


class UserMedalInExercise(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    gold = models.IntegerField(default=0)
    silver = models.IntegerField(default=0)
    bronze = models.IntegerField(default=0)
    exercise = models.ForeignKey(Exercise, on_delete=CASCADE)
