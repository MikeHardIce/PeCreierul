
from __future__ import annotations

import os
from typing import cast
from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from sqlalchemy.orm import Session

from pecreierul.app import PeCreierulBaseApp
from pecreierul.database import Lesson
from pecreierul.editscreen import EditLessonScreen
from pecreierul.trainscreen import TrainLessonScreen

Builder.load_file(os.path.join(os.path.dirname(__file__), 'menuscreen.kv'))

class NewLessonPopUp(ModalView):

    grid: LessonGrid
    input: TextInput = ObjectProperty(None)

    def create_lesson(self):
        if not self.input.text.strip() == "":

            app: PeCreierulBaseApp | None = App.get_running_app()
        
            if app is None:
                return

            with Session(app.engine) as session:
                lesson = Lesson()
                lesson.name = self.input.text
                lesson.description = ""
                app.repository.save_lessons(session,[lesson])
                session.commit()
                self.grid.add_lesson_box(lesson)

        self.dismiss()

class LessonBox(BoxLayout):
    lesson_name = ObjectProperty(None)
    lesson_id: int

    grid: GridLayout

    def start_training(self):
        app: PeCreierulBaseApp | None = App.get_running_app()

        if app is None:
            return

        train_lesson: TrainLessonScreen = app.manager.get_screen("train_lesson")

        train_lesson.lesson_id = self.lesson_id

        app.manager.current = "train_lesson"

    def edit_lesson(self):
        app: PeCreierulBaseApp | None = App.get_running_app()
        
        if app is None:
            return
        
        editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")

        editLesson.lesson_id = self.lesson_id

        app.manager.current = "edit_lesson"

    def delete_lesson(self):
        app: PeCreierulBaseApp | None = App.get_running_app()
        
        if app is None:
            return

        with Session(app.engine) as session:
            lesson = app.repository.load_lesson_by_id(session, self.lesson_id)
            if len(lesson.lesson_terms) < 1:
                app.repository.delete_lessons(session, [lesson])
                session.commit()

        self.grid.remove_widget(self)

class AddLessonBox(Button):
    pass

class LessonGrid(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_lessons, 0)

    def load_lessons(self, dt):
        app: PeCreierulBaseApp | None = cast(PeCreierulBaseApp, App.get_running_app())
        
        if app is None:
            return

        with Session(app.engine) as session:
            lessons = app.repository.load_all_lessons(session)

            # clean up all shown lesson boxes
            for wdg in self.children:
                if isinstance(wdg, LessonBox):
                    self.remove_widget(wdg)

            for lesson in lessons:
                self.add_lesson_box(lesson)

    def add_lesson_box(self, lesson: Lesson):
        box = LessonBox()
        box.lesson_name.text = lesson.name
        box.lesson_id = lesson.id
        box.grid = self
        self.add_widget(box,1)

    def create_lesson(self):
        pop = NewLessonPopUp()
        pop.grid = self
        pop.open()

    
class LessonPanel(ScrollView):
    lesson_grid = ObjectProperty(None)

class PeCreierulMenu(AnchorLayout):
    pass

class PeCreierulMenuScreen(Screen):
    pass