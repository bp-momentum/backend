from channels.generic.websocket import WebsocketConsumer

import json
import threading
from .Helperclasses.ai import DummyAI
import random


class ChatConsumer(WebsocketConsumer):
    def send_stats(self, ex_id):
        # calculating points
        if not self.doing_set:
            return
        a, b, c = DummyAI.dummy_function(ex=ex_id, video=None)
        intensity = b['intensity']
        speed = b['speed']
        cleanliness = b['cleanliness']
        self.send(text_data=json.dumps({
            'success': True,
            'description': "This is the accuracy",
            'data': {
                'intensity': intensity,
                'speed': speed,
                'cleanliness': cleanliness
            }
        }))

    def f(self, f_stop):
        self.send_stats(1)
        if not f_stop.is_set():
            wait = random.randint(3, 8)
            threading.Timer(wait, self.f, [f_stop]).start()

    def connect(self):
        self.doing_set = False
        self.accept()

    def disconnect(self, close_code):
        try:
            self.f_stop.set()
        except:
            pass
        self.doing_set = False
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        m_type = text_data_json['message_type']
        data = text_data_json['data']

        if m_type == "video_stream":

            exercise = data['exercise']
            video = data['video']

            if not self.doing_set:
                self.send(text_data=json.dumps({
                    'success': False,
                    'description': "The set must be started to send the video Stream",
                    'data': {}
                }))
            # AIInterface.call_ai(exercise, video, "user")

        elif m_type == "start_set":
            if not self.doing_set:
                self.f_stop = threading.Event()
                self.doing_set = True
                self.f(self.f_stop)

        elif m_type == "end_set":
            if self.doing_set:
                self.f_stop.set()
            self.doing_set = False



