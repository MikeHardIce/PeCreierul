from __future__ import annotations

import os
import random
from typing import List, cast;

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics import Color, Line, Canvas
from sqlalchemy.orm import Session

from pecreierul.app import PeCreierulBaseApp
from pecreierul.training import TrainingSession, TrainingUnit

Builder.load_file(os.path.join(os.path.dirname(__file__), 'trainscreen.kv'))

class TrainLessonScreen(Screen):

    lesson_id: int = -1
    training_session: TrainingSession

    lesson_name: Label = ObjectProperty(None)
    text_question_box: Label = ObjectProperty(None)
    text_answer_box: TextAnswerBox = ObjectProperty(None)
    progress_stack: ProgressStacks = ObjectProperty(None)

    def back(self):
        PeCreierulBaseApp.get_running_app().manager.current = "main_menu"

    def on_pre_enter(self, *args):

        base_app = PeCreierulBaseApp.get_running_app()

        with Session(base_app.engine) as session:
            lesson = base_app.repository.load_lesson_by_id(session, self.lesson_id)
            self.lesson_name.text = lesson.name
            number_of_sessions = len(lesson.lesson_terms) 
            number_of_sessions = 10 if number_of_sessions > 10 else number_of_sessions
            train: dict[str, str] = {}
            for lesson_term in random.choices(lesson.lesson_terms, k = number_of_sessions):
                train[lesson_term.term1.value] = lesson_term.term2.value

        self.training_session = TrainingSession(train)
        self.progress_stack.draw(self.training_session)
        self.text_answer_box.lesson_screen = self

        unit = self.training_session.get_next()

        if unit is not None:
            self.text_question_box.text = unit.question

        Clock.schedule_once(self.text_answer_box.focus, 0)

    def on_answer_submitted(self, answer: str):
        self.training_session.submit_answer(answer)
        self.progress_stack.draw(self.training_session)

        unit = self.training_session.get_next()

        if unit is not None:
            self.text_question_box.text = unit.question
            Clock.schedule_once(self.text_answer_box.focus, .5)
        else:
            self.text_answer_box.disable()     

class TextAnswerBox(BoxLayout):
    lesson_screen: TrainLessonScreen
    text_answer: TextInput = ObjectProperty(None)

    def focus(self, dt = 0):
        self.text_answer.focus = True

    def disable(self):
        self.text_answer.readonly = True

    def on_enter_pressed(self):
        if self.text_answer.text is not None and len(self.text_answer.text) > 0:
            self.lesson_screen.on_answer_submitted(self.text_answer.text)

        self.text_answer.text = ""

class MultipleChoiceAnswerBox(BoxLayout):
    pass

class ProgressStacks(Widget):
    canvas: Canvas

    def draw(self, session: TrainingSession):
        offset_x = 200
        offset_y = 50
        self.canvas.clear()
        with self.canvas:
            
            Color(0, 0, 0, 1)
            for index_x in range(0, len(session.stacks) + 1):
                x = offset_x + index_x * 60
                Line(points= [x, offset_y + 0, x, offset_y + 200], width = 1)


            Color(0.2, 0.8, 0.2, 1)
            for index_x, number_tiles in enumerate(session.get_current_distribution()):
                for pos in range(number_tiles):
                    x = offset_x + index_x * 60
                    Line(points = [x + 7, offset_y + 10 * (pos + 1), x + 53, offset_y +  10 * (pos + 1)], width=2)