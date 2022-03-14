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
                ai_back = {
                    "feedback": "information",
                    "info": "No person could be found in livestream"
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
