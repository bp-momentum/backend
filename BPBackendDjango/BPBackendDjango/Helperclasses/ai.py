import random
import math

class AIInterface():
    def call_ai(exercise, video, username):
        return DummyAI.dummy_function(exercise, video)


class DummyAI():
    def dummy_function(ex, video):
        return {
            'performance': math.ceil(random.random()*100+900),
            'speed': math.ceil(random.random()*100+900),
            'test': math.ceil(random.random()*100+900)
        }