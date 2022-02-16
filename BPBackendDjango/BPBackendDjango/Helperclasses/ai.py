import random
import math

class AIInterface():
    @staticmethod
    def call_ai(exercise, video, username):
        #TODO assign result user
        #expecting (success, results, feedback)
        return DummyAI.dummy_function(exercise, video)


class DummyAI:
    @staticmethod
    def dummy_function(ex, video):
        return True, {
            'intensity': math.ceil(random.random()*10000)/200 + 50,
            'speed': math.ceil(random.random()*10000)/200 + 50,
            'cleanliness': math.ceil(random.random()*10000)/200 + 50
        }, "This is your indivual feedback, these values are random generated."