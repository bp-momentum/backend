import errno

from channels.generic.websocket import WebsocketConsumer
import time
import json
import threading
from .Helperclasses.ai import DummyAI, AIInterface
import random
import os

from .models import DoneExercises
from .settings import INTERN_SETTINGS
from .Helperclasses.jwttoken import JwToken


class SetConsumer(WebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.filename = None
        self.doing_set = False
        self.f_stop = None
        self.username = ""

        self.authenticated = False

        self.executions_per_set = 0
        self.sets = 0

        self.exercise = 0
        self.executions_done = 0
        self.current_set = 0
        self.current_set_execution = 0

        self.speed = 0
        self.intensity = 0
        self.cleanliness = 0

    def save_video(self, data):
        if not os.path.exists(os.path.join(INTERN_SETTINGS['video_dir'], self.username)):
            try:
                os.mkdir(os.path.join(INTERN_SETTINGS['video_dir'], self.username))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(os.path.join(INTERN_SETTINGS['video_dir'], self.username, self.filename)):
            mode = 'wb'
        else:
            mode = 'ab'

        with open(os.path.join(INTERN_SETTINGS['video_dir'], self.username, self.filename), mode) as f:
            f.write(data)
            f.close()

    def authenticate(self, session_token):
        token = JwToken.check_session_token(session_token['session_token'])
        if not token['valid']:
            self.send(text_data=json.dumps({
                'message_type': 'authenticate',
                'success': False,
                'description': "Token is not valid",
                'data': {}
            }))
            return
        self.authenticated = True
        info = token['info']
        self.username = info['username']
        self.send(text_data=json.dumps({
            'message_type': 'authenticate',
            'success': True,
            'description': "User is now authenticated",
            'data': {}
        }))

    def start_set(self, data):
        if not self.doing_set:
            self.filename = str(time.time()) + ".webm"
            self.f_stop = threading.Event()
            self.doing_set = True
            self.f(self.f_stop)
            self.send(text_data=json.dumps({
                'message_type': 'start_set',
                'success': True,
                'description': "The set is now started",
                'data': {}
            }))
        else:
            self.send(text_data=json.dumps({
                'message_type': 'start_set',
                'success': False,
                'description': "The set is already started",
                'data': {}
            }))

    def end_set(self, data):
        if self.doing_set:
            self.f_stop.set()
            self.doing_set = False
            self.send(text_data=json.dumps({
                'message_type': 'end_set',
                'success': True,
                'description': "The set is now ended",
                'data': {}
            }))
        else:
            self.send(text_data=json.dumps({
                'message_type': 'end_set',
                'success': False,
                'description': "Currently no set is started",
                'data': {}
            }))

    def ai_evaluation(self, data):
        if not self.doing_set:
            self.send(text_data=json.dumps({
                'success': False,
                'description': "The set must be started to send the video Stream",
                'data': {}
            }))
        self.save_video(data)
        AIInterface.call_ai(self.exercise, data, self.username)

    def initiate(self, data):
        self.exercise = data['exercise']

        exercise = DoneExercises.objects.get(date__gt=time.time() - 68400, exercise=self.exercise, user=self.username)

        if exercise.exists():
            self.executions_per_set = exercise.executions_per_set
            self.sets = exercise.exercise.sets

            self.executions_done = exercise.executions_done
            self.current_set = exercise.current_set
            self.current_set_execution = exercise.current_set_execution

            self.speed = exercise.speed
            self.intensity = exercise.intensity
            self.cleanliness = exercise.cleanliness
        else:
            self.executions_per_set = 0
            self.sets = 0

            self.exercise = 0
            self.executions_done = 0
            self.current_set = 0
            self.current_set_execution = 0

            self.speed = 0
            self.intensity = 0
            self.cleanliness = 0

        self.send(text_data=json.dumps({
            'message_type': 'init',
            'success': True,
            'description': "This is the current state",
            'data': {
                'current_set': self.current_set,
                'current_execution': self.current_set_execution,
                'speed': 0 if self.executions_done == 0 else self.speed / self.executions_done,
                'cleanliness': 0 if self.executions_done == 0 else self.cleanliness / self.executions_done,
                'intensity': 0 if self.executions_done == 0 else self.intensity / self.executions_done
            }
        }))

    def send_stats(self, ex_id):
        # calculating points
        if not self.doing_set:
            return
        a, b, c = DummyAI.dummy_function(ex=ex_id, video=None)
        intensity = b['intensity']
        speed = b['speed']
        cleanliness = b['cleanliness']

        self.intensity += intensity
        self.speed += speed
        self.cleanliness += cleanliness

        self.executions_done += 1
        self.current_set_execution += 1

        self.send(text_data=json.dumps({
            'success': True,
            'description': "This is the accuracy",
            'data': {
                'intensity': intensity,
                'speed': speed,
                'cleanliness': cleanliness,
                'x': 30,
                'y': 100,
            }
        }))

        if self.current_set_execution == self.executions_per_set:
            self.f_stop.set()
            self.doing_set = False
            self.current_set_execution = 0
            self.current_set += 1

            self.send(text_data=json.dumps({
                'message_type': 'end_set',
                'success': True,
                'description': "The set is now ended",
                'data': {}
            }))

        if self.current_set == self.sets + 1:
            self.send(text_data=json.dumps({
                'message_type': 'exercise_complete',
                'success': True,
                'description': "The set is now ended",
                'data': {}
            }))

    def f(self, f_stop):
        self.send_stats(1)
        if not f_stop.is_set():
            wait = random.randint(3, 8)
            threading.Timer(wait, self.f, [f_stop]).start()

    # On Connect
    def connect(self):
        self.filename = None
        self.doing_set = False
        self.accept()

    # On Disconnect
    def disconnect(self, close_code):
        try:
            self.f_stop.set()
        except:
            pass
        self.doing_set = False

    # On Receive
    def receive(self, text_data=None, bytes_data=None):

        # check if request has bytes_data
        if bytes_data is not None:
            self.ai_evaluation(bytes_data)

        # check if request hast text_data
        if text_data is not None:
            text_data_json = json.loads(text_data)
            m_type = text_data_json['message_type']
            data = text_data_json['data']

            if m_type == "authenticate":
                self.authenticate(data)
            elif not self.authenticated:
                self.send(text_data=json.dumps({
                    'message_type': 'authenticate',
                    'success': False,
                    'description': "You have to be authenticated",
                    'data': {}
                }))

            elif m_type == "start_set":
                self.start_set(data)

            elif m_type == "end_set":
                pass
                # self.end_set(data)

            elif m_type == "init":
                self.initiate(data)
