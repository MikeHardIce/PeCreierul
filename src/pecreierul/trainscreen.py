import os;

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from pecreierul.app import PeCreierulBaseApp

Builder.load_file(os.path.join(os.path.dirname(__file__), 'trainscreen.kv'))

class TrainLessonScreen(Screen):

    lesson_id: int = -1

    app: PeCreierulBaseApp | None

    def back(self):

        if self.app is None:
            return

        self.app.manager.current = "main_menu"

    def on_pre_enter(self, *args):

        self.app = App.get_running_app()

class TextAnswerBox(BoxLayout):
    pass

class MultipleChoiceAnswerBox(BoxLayout):
    pass