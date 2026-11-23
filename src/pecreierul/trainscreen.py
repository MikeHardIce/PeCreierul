from __future__ import annotations

import os
import random
from typing import List, Tuple

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.graphics import Color, Line, Canvas
from sqlalchemy.orm import Session
from kivy.core.window import Window

from pecreierul.app import PeCreierulBaseApp
from pecreierul.training import TrainingSession, TrainingUnit

Builder.load_file(os.path.join(os.path.dirname(__file__), 'trainscreen.kv'))

class QuestionBox(BoxLayout):

    hint: Label
    backup: Widget

    def display_question(self, unit: TrainingUnit | None):
        if unit is not None:
            self.clear_widgets()
            if PeCreierulBaseApp.is_path(unit.question):
                self.create_image(unit.question)
            else:
                self.create_label(unit.question)

            self.prepate_hint_label(unit.hint)

    def show_hint(self):
        self.clear_widgets()
        self.add_widget(self.hint)

    def show_question(self):
        self.clear_widgets()
        self.add_widget(self.backup)

    def prepate_hint_label(self, text: str):
        self.hint = Label(
            text=text if text is not None else "",
            font_size=24,
            bold=True,
            text_size=(500, None),
            color=(0, 0, 0, 1))

    def create_label(self, text: str):
        label = Label(
            text=text,
            font_size=32,
            bold=True,
            text_size=(500, None),
            color=(0, 0, 0, 1))

        self.add_widget(label)
        self.backup = label

    def create_image(self, path: str):
        image = Image(
            source=path,
            allow_stretch=True,
            keep_ratio=True)

        self.add_widget(image)
        self.backup = image

class TextAnswerBox(BoxLayout):
    lesson_screen: TrainLessonScreen
    text_answer: TextInput = ObjectProperty(None)

    def focus(self, dt = 0):
        self.text_answer.focus = True

    def display(self, unit: TrainingUnit):
        self.text_answer.focus = True

    def on_enter_pressed(self):
        if self.text_answer.text is not None and len(self.text_answer.text) > 0:
            self.lesson_screen.on_answer_submitted(self.text_answer.text)

        self.text_answer.text = ""

class MultipleChoiceAnswerBox(BoxLayout):
    lesson_screen: TrainLessonScreen

    def display(self, unit: TrainingUnit):
        self.clear_widgets()
        answers_toggles: List[ToggleButton] = []
        for fake in unit.fake_answers:
            toggle = ToggleButton(text=fake, state="normal")
            toggle.bind(state=self.on_answer_selected)
            answers_toggles.append(toggle)

        toggle = ToggleButton(text=unit.answer, state="normal")
        toggle.bind(state=self.on_answer_selected)
        answers_toggles.append(toggle)

        random.shuffle(answers_toggles)

        for toggle in answers_toggles:
            self.add_widget(toggle)

    def on_answer_selected(self, instance, value):
        if value == "down":
            text = instance.text
            if text is not None and len(text) > 0:
                self.lesson_screen.on_answer_submitted(text)

class TrainLessonScreen(Screen):

    lesson_id: int = -1
    training_session: TrainingSession

    lesson_name: Label = ObjectProperty(None)
    answer_type_toggle: Switch = ObjectProperty(None)
    question_box: QuestionBox = ObjectProperty(None)
    text_answer_box: TextAnswerBox = ObjectProperty(None)
    correct_answer: Label = ObjectProperty(None)
    progress_stack: ProgressStacks = ObjectProperty(None)
    answer_container: BoxLayout = ObjectProperty(None)

    def on_multiple_choice_active(self, active):
        self.display_answer_container(self.training_session.current_unit, active)

    def display_answer_container(self, unit: TrainingUnit | None, active:bool = False):
        self.answer_container.clear_widgets()
        
        box = MultipleChoiceAnswerBox() if active else TextAnswerBox()

        if unit is not None:
            box.display(unit)

        box.lesson_screen = self

        self.answer_container.add_widget(box)

    def back(self):
        PeCreierulBaseApp.get_running_app().manager.current = "main_menu"

    def on_pre_enter(self, *args):

        self.answer_type_toggle.active = False
        base_app = PeCreierulBaseApp.get_running_app()

        with Session(base_app.engine) as session:
            lesson = base_app.repository.load_lesson_by_id(session, self.lesson_id)
            self.lesson_name.text = lesson.name
            number_of_sessions = len(lesson.lesson_terms) 
            number_of_sessions = 10 if number_of_sessions > 10 else number_of_sessions
            train: dict[str, Tuple[str,str]] = {}
            for lesson_term in random.sample(lesson.lesson_terms, k = number_of_sessions):
                train[lesson_term.term1.value] = lesson_term.term2.value, lesson_term.hint

        self.training_session = TrainingSession(train)
        self.progress_stack.draw(self.training_session)
        self.text_answer_box.lesson_screen = self

        unit = self.training_session.get_next()
        
        self.question_box.display_question(unit)

        self.display_answer_container(unit)

        Clock.schedule_once(self.text_answer_box.focus, 0)

    def on_answer_submitted(self, answer: str):
        unit: TrainingUnit | None = self.training_session.current_unit

        if not self.training_session.submit_answer(answer):
            self.correct_answer.text = unit.answer if unit is not None else ""
            def reset (dt):
                self.correct_answer.text = ""
            Clock.schedule_once(reset, 5)

        self.progress_stack.draw(self.training_session)

        unit = self.training_session.get_next()

        if unit is not None:
            self.question_box.display_question(unit)
            self.display_answer_container(unit, self.answer_type_toggle.active)
            Clock.schedule_once(self.text_answer_box.focus, .5)
        else:
            self.answer_container.clear_widgets()

    def on_enter(self, *args):
        Window.bind(on_key_down = self.on_key_down_global)
        Window.bind(on_key_up = self.on_key_up_global)


    def on_leave(self, *args):
        Window.unbind(on_key_down = self.on_key_down_global)
        Window.unbind(on_key_up = self.on_key_up_global)

    def on_key_up_global(self, window, keycode, *args):

        if keycode == 308:
            self.question_box.show_question()
            return True

        return False
    
    def on_key_down_global(self, window, keycode, *args):

        if keycode == 308:
            self.question_box.show_hint()
            return True

        return False

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