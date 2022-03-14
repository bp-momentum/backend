import random
import math
import time


last_call = time.time()


class AIInterface:

    @staticmethod
    def call_ai(exercise, video) -> dict:
        print("got")
        global last_call
        ai_back = {}
        if time.time() - last_call > 3:
            rand = random.random()
            if rand > 95:

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
