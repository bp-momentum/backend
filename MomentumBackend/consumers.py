import errno
from .Helperclasses.handlers import ExerciseHandler, LeaderboardHandler, UserHandler

from channels.generic.websocket import WebsocketConsumer
import time
import json
import threading
from .Helperclasses.ai import DummyAI, AIInterface
import random
import os

from .models import (
    DoneExercises,
    User,
    ExerciseInPlan,
    Leaderboard,
    UserMedalInExercise,
)
from .settings import CONFIGURATION
from .Helperclasses.jwttoken import JwToken


class SetConsumer(WebsocketConsumer):
    def __init__(self):
        super().__init__()

        self.points = 0
        # initialising the new connection
        self.filename = None
        self.doing_set = False
        self.username = ""
        self.user = None

        self.authenticated = False
        self.initiated = False

        # initialising new exercise will be overwritten after init when exercise could be loaded
        self.executions_per_set = 0
        self.sets = 0

        self.exercise = 0
        self.executions_done = 0
        self.current_set = 0
        self.current_set_execution = 0

        self.speed = 0
        self.intensity = 0
        self.cleanliness = 0

        self.done_exercise_entry = None
        self.completed = False

        self.exinplan = None

    # in this method the incoming video stream will be saved
    def save_video(self, data_bytes):
        if not os.path.exists(
            os.path.join(CONFIGURATION["video_dir"], self.username)
        ):
            # check if the user folder was already created else mkdir
            try:
                os.mkdir(os.path.join(CONFIGURATION["video_dir"], self.username))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # add new video blob to the file
        if not os.path.exists(
            os.path.join(CONFIGURATION["video_dir"], self.username, self.filename)
        ):
            mode = "wb"
        else:
            mode = "ab"

        with open(
            os.path.join(CONFIGURATION["video_dir"], self.username, self.filename),
            mode,
        ) as f:
            f.write(data_bytes)
            f.close()

    def authenticate(self, session_token):

        # check if token is valid
        token = JwToken.check_session_token(session_token["session_token"])
        if not token["valid"]:
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "authenticate",
                        "success": False,
                        "description": "Token is not valid",
                        "data": {},
                    }
                )
            )
            return

        # check if account_type is user
        if not token["info"]["account_type"] == "user":
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "authenticate",
                        "success": False,
                        "description": "Only a user can do an exercise",
                        "data": {},
                    }
                )
            )
            return

        # set connection as authenticated
        self.authenticated = True

        # set connections user info
        info = token["info"]
        self.username = info["username"]
        self.user: User = User.objects.get(username=self.username)

        self.send(
            text_data=json.dumps(
                {
                    "message_type": "authenticate",
                    "success": True,
                    "description": "User is now authenticated",
                    "data": {},
                }
            )
        )

    def start_set(self, data):

        # check if user is already doing a set
        # when not start new thread
        if not self.doing_set:
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "start_set",
                        "success": True,
                        "description": "The set is now started",
                        "data": {},
                    }
                )
            )
            self.filename = str(time.time()) + ".webm"
            self.doing_set = True

        else:
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "start_set",
                        "success": False,
                        "description": "The set is already started",
                        "data": {},
                    }
                )
            )

    def end_set(self, data):
        # check if user is doing a set, if so and the set !!! is currently disabled and has to be changed when enabled!!
        if self.doing_set:
            self.doing_set = False
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "end_set",
                        "success": True,
                        "description": "The set is now ended",
                        "data": {},
                    }
                )
            )
        else:
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "end_set",
                        "success": False,
                        "description": "Currently no set is started",
                        "data": {},
                    }
                )
            )

    def initiate(self, data):
        # save, which exercise is done
        self.exercise = data["exercise"]
        self.initiated = True

        # load exercise info from database
        self.exinplan: ExerciseInPlan = ExerciseInPlan.objects.get(id=self.exercise)
        self.sets = self.exinplan.sets
        self.executions_per_set = self.exinplan.repeats_per_set

        # load already done exercises in this week
        query = DoneExercises.objects.filter(
            date__gt=time.time() - 518400, exercise=self.exercise, user=self.user.id
        )

        # when exercise was already started, load info
        if query.exists():
            self.done_exercise_entry: DoneExercises = query[0]
            self.executions_done = self.done_exercise_entry.executions_done
            self.current_set = self.done_exercise_entry.current_set
            self.current_set_execution = self.done_exercise_entry.current_set_execution

            self.speed = self.done_exercise_entry.speed
            self.intensity = self.done_exercise_entry.intensity
            self.cleanliness = self.done_exercise_entry.cleanliness
            self.completed = self.done_exercise_entry.completed

        else:
            # if not started already  initialise
            self.done_exercise_entry = None

            self.exercise = 0
            self.executions_done = 0
            self.current_set = 0
            self.current_set_execution = 0

            self.speed = 0
            self.intensity = 0
            self.cleanliness = 0

        # current state of the exercise will be returned
        self.send(
            text_data=json.dumps(
                {
                    "message_type": "init",
                    "success": True,
                    "description": "This is the current state",
                    "data": {
                        "current_set": self.current_set,
                        "current_execution": self.current_set_execution,
                        "speed": 0
                        if self.executions_done == 0
                        else self.speed / self.executions_done,
                        "cleanliness": 0
                        if self.executions_done == 0
                        else self.cleanliness / self.executions_done,
                        "intensity": 0
                        if self.executions_done == 0
                        else self.intensity / self.executions_done,
                        "completed": self.completed,
                    },
                }
            )
        )

    def send_stats(self, intensity, speed, cleanliness, coordinates):
        # send stats emulates the ai when sending info after a single execution
        # calculating points
        if not self.doing_set:
            return

        self.intensity += intensity
        self.speed += speed
        self.cleanliness += cleanliness

        self.executions_done += 1
        self.current_set_execution += 1

        self.send(
            text_data=json.dumps(
                {
                    "message_type": "statistics",
                    "success": True,
                    "description": "This is the accuracy",
                    "data": {
                        "intensity": intensity,
                        "speed": speed,
                        "cleanliness": cleanliness,
                        "coordinates": coordinates,
                    },
                }
            )
        )

        type = 0

        # end set when set is done
        if self.current_set_execution == self.executions_per_set:
            self.doing_set = False
            self.current_set_execution = 0
            self.current_set += 1

            type += 1

        # end exercise when exercise is done
        if self.current_set == self.sets:
            self.doing_set = False
            type += 1
            self.current_set -= 1

            # save in Leaderboard
            self.points = (
                0
                if self.executions_per_set == 0
                else int(
                    (self.speed + self.intensity + self.cleanliness)
                    / (self.sets * self.executions_per_set * 3)
                )
            )

            # add medal
            if not UserMedalInExercise.objects.filter(
                user=self.user, exercise=self.exinplan.exercise
            ).exists():
                UserMedalInExercise.objects.create(
                    user=self.user, exercise=self.exinplan.exercise
                )
            umix: UserMedalInExercise = UserMedalInExercise.objects.get(
                user=self.user, exercise=self.exinplan.exercise
            )
            gained_medal = ""
            if self.points >= 90:  # gold
                umix.gold += 1
                gained_medal = "gold"
            elif self.points >= 75:  # silver
                umix.silver += 1
                gained_medal = "silver"
            elif self.points >= 50:  # bronze
                umix.bronze += 1
                gained_medal = "bronze"
            umix.save(force_update=True)

            self.completed = True
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "exercise_complete",
                        "success": True,
                        "description": "The exercise is now ended",
                        "data": {
                            "speed": 0
                            if self.executions_done == 0
                            else self.speed / self.executions_done,
                            "cleanliness": 0
                            if self.executions_done == 0
                            else self.cleanliness / self.executions_done,
                            "intensity": 0
                            if self.executions_done == 0
                            else self.intensity / self.executions_done,
                            "medal": gained_medal,
                        },
                    }
                )
            )

            # add streak when this was the last exercise today
            if ExerciseHandler.check_if_last_exercise(self.user):
                self.user.streak += 1
                self.user.save(force_update=True)

            p = (
                0
                if self.executions_per_set == 0
                else int((self.speed + self.intensity + self.cleanliness) / 3)
            )
            leaderboard_entry: Leaderboard = Leaderboard.objects.get(user=self.user.id)

            leaderboard_entry.speed += self.speed
            leaderboard_entry.intensity += self.intensity
            leaderboard_entry.cleanliness += self.cleanliness
            leaderboard_entry.executions += self.executions_done

            exs_to_do = 0
            if self.user.plan is not None:
                plan_data = ExerciseInPlan.objects.filter(plan=self.user.plan.id)
                for ex in plan_data:
                    exs_to_do += ex.repeats_per_set * ex.sets

            leaderboard_entry.score = (
                leaderboard_entry.speed
                + leaderboard_entry.intensity
                + leaderboard_entry.cleanliness
            ) / (3 * exs_to_do)

            leaderboard_entry.save(force_update=True)
            UserHandler.add_xp(
                self.user,
                (
                    (self.speed + self.intensity + self.cleanliness)
                    / (3 * self.executions_done)
                )
                * (min(self.user.streak, 10) + 1),
            )

        # send set information
        if type == 1:
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "end_set",
                        "success": True,
                        "description": "The set is now ended",
                        "data": {
                            "speed": 0
                            if self.executions_done == 0
                            else self.speed / self.executions_done,
                            "cleanliness": 0
                            if self.executions_done == 0
                            else self.cleanliness / self.executions_done,
                            "intensity": 0
                            if self.executions_done == 0
                            else self.intensity / self.executions_done,
                        },
                    }
                )
            )

    def ai_evaluation(self, data):

        if not self.doing_set:
            self.send(
                text_data=json.dumps(
                    {
                        "success": False,
                        "description": "The set must be started to send the video Stream",
                        "data": {},
                    }
                )
            )

        # self.save_video(data)
        # check stats or info
        feedback = AIInterface.call_ai(self.exercise, data)

        if feedback["feedback"] == "statistics":
            # load ai data
            intensity = feedback["stats"]["intensity"]
            speed = feedback["stats"]["speed"]
            cleanliness = feedback["stats"]["cleanliness"]
            coordinates = feedback["coordinates"]

            self.send_stats(intensity, speed, cleanliness, coordinates)

        elif feedback["feedback"] == "information":
            self.send(
                text_data=json.dumps(
                    {
                        "message_type": "information",
                        "success": True,
                        "description": "This is a information",
                        "data": {
                            "information": feedback["info"][self.user.language],
                        },
                    }
                )
            )

    # start new thread
    def start_ai_call(self, data):
        t = threading.Thread(
            target=SetConsumer.ai_evaluation,
            args=(
                self,
                data,
            ),
        )
        t.daemon = True
        t.start()

    # On Connect
    def connect(self):
        LeaderboardHandler.reset_leaderboard()
        self.filename = None
        self.doing_set = False
        self.accept()

    # On Disconnect
    def disconnect(self, close_code):
        self.doing_set = False

        # save current state in database

        if self.initiated:
            if self.done_exercise_entry is None:
                DoneExercises.objects.create(
                    exercise=self.exinplan,
                    user=self.user,
                    points=self.points,
                    date=time.time(),
                    executions_done=self.executions_done,
                    current_set=self.current_set,
                    current_set_execution=self.current_set_execution,
                    speed=self.speed,
                    intensity=self.intensity,
                    cleanliness=self.cleanliness,
                    completed=self.completed,
                )
            else:

                self.done_exercise_entry.executions_done = self.executions_done
                self.done_exercise_entry.current_set = self.current_set
                self.done_exercise_entry.current_set_execution = (
                    self.current_set_execution
                )

                self.done_exercise_entry.speed = self.speed
                self.done_exercise_entry.intensity = self.intensity
                self.done_exercise_entry.cleanliness = self.cleanliness
                self.done_exercise_entry.points = self.points
                self.done_exercise_entry.completed = self.completed
                self.done_exercise_entry.save(force_update=True)

    # On Receive
    def receive(self, text_data=None, bytes_data=None):

        # check if request has bytes_data
        if bytes_data is not None:
            # send bytes to ai
            self.start_ai_call(bytes_data)

        # check if request hast text_data
        if text_data is not None:
            text_data_json = json.loads(text_data)
            m_type = text_data_json["message_type"]
            data = text_data_json["data"]

            # check if authenticing else if authenticated
            if m_type == "authenticate":
                self.authenticate(data)
            elif not self.authenticated:
                self.send(
                    text_data=json.dumps(
                        {
                            "message_type": "authenticate",
                            "success": False,
                            "description": "You have to be authenticated",
                            "data": {},
                        }
                    )
                )
            # check if initialising else check if initialised
            elif m_type == "init":
                self.initiate(data)
            elif not self.initiated:
                self.send(
                    text_data=json.dumps(
                        {
                            "message_type": "init",
                            "success": False,
                            "description": "You have to first initialise",
                            "data": {},
                        }
                    )
                )

            # check if already completed
            elif self.completed:
                self.send(
                    text_data=json.dumps(
                        {
                            "message_type": "exercise_complete",
                            "success": False,
                            "description": "You already completed this Exercise",
                            "data": {},
                        }
                    )
                )

            # start the set
            elif m_type == "start_set":
                self.start_set(data)

            # end the set

            elif m_type == "end_set":
                pass
                # self.end_set(data)
