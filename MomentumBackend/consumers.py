import base64
import datetime
import json
import os
from pathlib import Path
from threading import Timer
import uuid
import threading
import subprocess

import socketio
from django.utils.timezone import make_aware
from channels.generic.websocket import WebsocketConsumer

# from .Helperclasses.jwttoken import JwToken
from .models import (ExerciseExecution, ExerciseInPlan, SetStats, User)
from .settings import CONFIGURATION

# from channels.db import database_sync_to_async
# TODO: use this decorator to make the database calls async


# What even is all this?
#
# A diagram detailing the communication between the frontend, the backend, and the AI can be found here: https://github.com/bp-momentum/documentation/blob/main/API/component_communication.svg
#
# One socket per set (expected) -> Closing the socket before the set is done will result in the progress of that set being lost / overwritten.
# One socket per set, a procID is send after the last repetition to identify the results. The AI will stop processing if no procID is sent before the socket is closed.

class Recorder(threading.Thread):
    def __init__(self, output_name: str):
        self.p = None
        self.output_name = output_name
        threading.Thread.__init__(self)

    def run(self):
        self.p = subprocess.Popen(self.generate_recorder_command(),
                                  shell=False,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)

    def generate_recorder_command(self):
        return ('ffmpeg',  # (WARN) ffmpeg must be in path
                '-f', 'image2pipe',  # tell ffmpeg to expect a "pipe format"
                '-vcodec', 'mjpeg',  # that contains mjpeg encoded images
                '-r', '10',  # TODO: adjust FPS
                '-i', '-',  # The input comes from a pipe
                # use the h.264 codec (open source implementation)
                '-vcodec', 'libx264',
                '-crf', '25',  # quality, 0-51, where 0 is best
                # pixel format (needed here for compatibility)
                '-pix_fmt', 'yuv420p',
                self.output_name)

    # in this method the incoming video stream will be saved
    def save_video(self, data_bytes):
        data_bytes = data_bytes.decode("utf8").split(",")[1]
        data_bytes = base64.b64decode(data_bytes)
        self.p.stdin.write(data_bytes)

    def stop(self):
        self.p.stdin.close()
        self.join()


class SetConsumer(WebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.exercise = None  # exercise that is currently done if initiated

        # internal variables
        self.execution = None
        self.current_set = -1
        self.current_repetition = -1
        self.ai = None
        self.recorder = None

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

    def create_ai_instance(self):
        ai = socketio.Client()
        ai.on("live_feedback", self.live_feedback)
        ai.connect(CONFIGURATION["ai_url"])
        ai.emit("set_exercise_id", {
            "exercise": self.exercise.exercise.id})
        return ai

    # ==================== FRONTEND MESSAGE HANDLERS ====================

    def initiate(self, data):
        # save, which exercise is done
        exercise = data["exercise"]

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
            date__gt=make_aware(datetime.datetime.now() -
                                datetime.timedelta(days=7)),
            exercise=self.exercise.exercise.id,
            user=self.scope["user"],
        )

        # when exercise was already started, load info
        if query.exists():
            self.execution: ExerciseExecution = query[0]
        else:
            self.execution = ExerciseExecution(
                user=self.scope["user"], exercise=self.exercise)
            self.execution.save()

        # get current set and repetition
        query = SetStats.objects.filter(exercise=self.execution)
        if query.exists():
            self.current_set = query.latest("set_nr").set_nr
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
        if CONFIGURATION["video_dir"] != None:
            # TODO: figure out if cwd is really the way to go
            record_dir = os.path.join(
                os.getcwd(), CONFIGURATION["video_dir"], self.scope["user"].username)
            record_name = os.path.join(record_dir, f"{str(self.set_uuid)}.mkv")
            # create directory if it does not exist
            if not os.path.exists(record_dir):
                Path(record_dir).mkdir(parents=True, exist_ok=True)
            self.recorder = Recorder(record_name)
            self.recorder.start()
        self.success_response("start_set", "The set is now started")

    def end_repetition(self):
        if self.ai is None:
            self.error_response("end_repetition", "Nothing to end")
            return

        # relay end_repetition to ai
        self.ai.emit("end_repetition", {})

        self.success_response(
            "end_repetition",
            "The repetition ended",
        )

    def end_set(self):
        if self.ai is None:
            print("WARNING: AI went missing.")
            self.error_response("end_repetition", "Nothing to end")
            return

        if self.recorder is not None:
            self.recorder.stop()

        # 1. create set stats object
        set_stats = SetStats(
            exercise=self.execution,
            set_uuid=self.set_uuid,
            set_nr=self.current_set,
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
        if not self.exercise or not hasattr(self, "set_uuid"):
            self.error_response(
                "", "The set must be started to send the video Stream")
            return

        if self.recorder is not None:
            self.recorder.save_video(data)

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
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            self.error_response("authenticate", "You have to be logged in.")
            return

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
