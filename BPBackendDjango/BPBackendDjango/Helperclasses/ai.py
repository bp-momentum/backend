import random
import math
import time


last_call = None


class AIInterface:

    @staticmethod
    def call_ai(exercise, video) -> dict:
        global last_call

        if last_call is None:
            last_call = time.time()

        ai_back = {
            "feedback": "None"
        }
        if time.time() - last_call > 3:
            last_call = time.time()
            rand = random.random()
            if rand < 0.85:

                ai_back = {
                    "feedback": "statistics",
                    "stats": DummyAI.dummy_function(exercise, video),
                    "coordinates": {
                        "x": random.randint(30, 400),
                        "y": random.randint(30, 400)
                    }

                }
            else:
                error_list = [
                    {"en": "No person could be found in livestream",
                    "de": "Es konnte keine Person im video gefunden werden"},
                    {"en": "It seems to be too dark",
                    "de": "Es scheint zu dunkel zu sein"},
                    {"en": "It is not possible recognize an execution",
                    "de": "Es konnte keine Ausführung einer Übung erkannt werden"}
                ]
                ai_back = {
                    "feedback": "information",
                    "info": random.choice(error_list)
                }
        return ai_back


class DummyAI:
    @staticmethod
    def dummy_function(ex, video) -> dict:

        return {
            'intensity': math.ceil(random.random()*10000)/200 + 50,
            'speed': math.ceil(random.random()*10000)/200 + 50,
            'cleanliness': math.ceil(random.random()*10000)/200 + 50
        }
