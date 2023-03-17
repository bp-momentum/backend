import datetime
import errno
import json
import os
from threading import Timer
import uuid

import socketio
from django.utils.timezone import make_aware
from channels.generic.websocket import WebsocketConsumer

from .Helperclasses.jwttoken import JwToken
from .models import (ExerciseExecution, ExerciseInPlan, SetStats, User)
from .settings import CONFIGURATION



# What even is all this?
# 
# A diagram detailing the communication between the frontend, the backend, and the AI can be found here: https://github.com/bp-momentum/documentation/blob/main/API/component_communication.svg
# 
# One socket per set (expected) -> Closing the socket before the set is done will result in the progress of that set being lost / overwritten.
# One socket per set, a procID is send after the last repetition to identify the results. The AI will stop processing if no procID is sent before the socket is closed.

class SetConsumer(WebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.username = None # username of the user is authenticated
        self.exercise = None # exercise that is currently done if initiated

        # internal variables
        self.execution = None
        self.current_set = -1
        self.current_repetition = -1
        self.ai = None

    # ==================== HELPER FUNCTIONS ====================

    def error_response(self, message_type, description):
        self.send(
            text_data=json.dumps(
                {
                    "message_type": message_type,
                    "success": False,
                    "description": description,
                    "data": {},
                }
            )
        )


    def success_response(self, message_type, description, data={}):
        self.send(
            text_data=json.dumps(
                {
                    "message_type": message_type,
                    "success": True,
                    "description": description,
                    "data": data,
                }
            )
        )


    def live_feedback(self, data):
        # send live feedback to frontend
        self.send(
            text_data=json.dumps(
                {
                    "message_type": "live_feedback",
                    "success": True,
                    "description": "Live feedback",
                    "data": data,
                }
            )
        )

    # in this method the incoming video stream will be saved
    def save_video(self, data_bytes):
        # TODO(WARNING): Currently saves images as jpg, not as video

        # check if videos should be saved
        if CONFIGURATION["video_dir"] == None:
            return
        
        folderName = os.path.join(CONFIGURATION["video_dir"], self.username, self.set_uuid)
        fileName = os.path.join(folderName, self.last_image + ".jpg")

        # check if the user folder was already created else mkdir
        if not os.path.exists(folderName):
            try:
                os.mkdir(folderName)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(fileName, "wb") as f:
            f.write(data_bytes)
            f.close()


    def create_ai_instance(self):
        ai = socketio.Client()
        ai.on("live_feedback", self.live_feedback)
        ai.connect(CONFIGURATION["ai_url"])
        ai.emit("set_exercise_id", {
                      "exercise": self.exercise.exercise.id})
        return ai


    # ==================== FRONTEND MESSAGE HANDLERS ====================

    def authenticate(self, session_token):
        # check if token is valid
        token = JwToken.check_session_token(session_token["session_token"])
        if not token["valid"]:
            self.error_response("authenticate", "Token is not valid")
            return

        # check if account_type is user
        if not token["info"]["account_type"] == "user":
            self.error_response("authenticate", "Only users can exercise")
            return

        # set connection as authenticated and connections user info
        self.username = token["info"]["username"]

        self.success_response("authenticate", "User is now authenticated")


    def initiate(self, data):
        # save, which exercise is done
        exercise = data["exercise"]

        user = User.objects.get(username=self.username)

        # load exercise info from database
        try:
            self.exercise: ExerciseInPlan = ExerciseInPlan.objects.get(
                id=exercise)
        except:
            self.initiated = False
            self.close()
            return
        self.sets = self.exercise.sets
        self.repetitions = self.exercise.repeats_per_set

        # load already done exercises in this week
        query = ExerciseExecution.objects.filter(
            date__gt=make_aware(datetime.datetime.now() - datetime.timedelta(days=7)),
            exercise=self.exercise.exercise.id,
            user=user,
        )

        # when exercise was already started, load info
        if query.exists():
            self.execution: ExerciseExecution = query[0]
        else:
            self.execution = ExerciseExecution(user=user, exercise=self.exercise)
            self.execution.save()

        # get current set and repetition
        query = SetStats.objects.filter(exercise=self.execution)
        if query.exists():
            self.current_set = query.latest("set").set
        else:
            self.current_set = 0

        self.current_repetition = 0

        # current state of the exercise will be returned
        self.success_response(
            "init",
            "This is the current state",
            {
                "current_set": self.current_set,
            })


    def start_set(self):
        # create a (new) repetition handler
        self.ai = self.create_ai_instance()
        self.set_uuid = uuid.uuid4()
        self.last_image = 0
        self.success_response("start_set", "The set is now started")


    def end_repetition(self):
        if self.ai is None:
            self.error_response("end_repetition", "Nothing to end")
            return

        # relay end_repetition to ai
        self.ai.emit("end_repetition")

        self.success_response(
            "end_repetition",
            "The repetition ended",
            )


    def end_set(self):
        if self.ai is None:
            print("WARNING: AI went missing.")
            self.error_response("end_repetition", "Nothing to end")
            return

        # 1. create set stats object
        set_stats = SetStats(
            exercise = self.execution,
            set_uuid = self.set_uuid,
            set_nr = self.current_set,
            )
        set_stats.save()

        # 2. send set stats uuid to ai
        self.ai.emit("end_set", {
            "set_uuid": str(self.set_uuid),
            })
        
        # 3. schedule closing of ai connection after 5 seconds
        self.ai.close_timer = Timer(5, self.ai.disconnect)
        self.ai.close_timer.start()

        self.success_response(
            "end_set",
            "The set ended",
            )


    def handleIncomingVideo(self, data):
        # guard to prevent sending video if not doing exercise
        if not self.exercise or not hasattr(self, "uuid"):
            self.error_response("", "The set must be started to send the video Stream")
            return

        self.save_video(data)

        # send video to ai
        if self.ai != None and self.ai.connected:
            self.ai.emit("send_video", data)


    # On Connect
    def connect(self):
        self.accept()


    # On Disconnect
    def disconnect(self, _):
        if self.ai:
            self.ai.disconnect()


    # Momentum Frontend -> Backend
    def receive(self, text_data=None, bytes_data=None):
        
        # bytes_data is a single frame of the video stream
        # if an image is sent, redirect it to the ai
        if bytes_data is not None:
            self.handleIncomingVideo(bytes_data)

        # guard that check if request has text_data
        if text_data is None:
            return

        # parse text_data
        text_data_json = json.loads(text_data)
        m_type = text_data_json["message_type"]
        data = text_data_json.get("data")

        # check if authenticating
        if m_type == "authenticate":
            self.authenticate(data)
            return

        # guard that check if request has been authenticated
        if not self.username:
            self.error_response("authenticate", "You have to be authenticated")
            return

        # check if initializing
        if m_type == "init":
            self.initiate(data)
            return

        # guard that check if request has been initiated
        if not self.exercise:
            self.error_response("init", "You have to first initialise")
            return

        # start the set
        if m_type == "start_set":
            self.start_set()
            return

        # end one repetition
        if m_type == "end_repetition":
            self.end_repetition()
            return

        # end the set
        if m_type == "end_set":
            pass
            self.end_set()
