from channels.generic.websocket import WebsocketConsumer

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

from .Helperclasses.ai import AIInterface, DummyAI


class ChatConsumer(WebsocketConsumer):
    async def send_stats(self, ex_id):
        while self.doing_set:
            # calculating points
            a, b, c = DummyAI.dummy_function(ex=ex_id, video=None)
            intensity = b['intensity']
            speed = b['speed']
            cleanliness = b['cleanliness']
            await self.send(text_data=json.dumps({
                'success': True,
                'description': "These are the current stats of this set",
                'data': {
                    'intensity': intensity,
                    'speed': speed,
                    'cleanliness': cleanliness
                }
            }))

    def connect(self):
        self.doing_set = False
        self.accept()

    def disconnect(self, close_code):
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
            AIInterface.call_ai(exercise, video)

        elif m_type == "start_set":
            self.send_stats(1)
            self.doing_set = True

        elif m_type == "end_set":
            self.doing_set = False