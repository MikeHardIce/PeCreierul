import os;

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

Builder.load_file(os.path.join(os.path.dirname(__file__), 'trainscreen.kv'))

class TrainLessonScreen(Screen):

    lesson_id: int = -1

    pass