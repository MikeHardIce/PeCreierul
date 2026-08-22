import os
from typing import List, Optional, cast

from sqlalchemy.orm import Session
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder

from pecreierul.app import PeCreierulBaseApp
from pecreierul.lesson_repository import LessonRepository
from pecreierul.database import LessonTerm, Tag, Lesson, Term


Builder.load_file(os.path.join(os.path.dirname(__file__), 'editscreen.kv'))

class AddItemBox(Button):
    pass

class TermBox(BoxLayout):
    lesson_term_id: int = -1
    sp_from: Spinner = ObjectProperty(None)
    text_from: TextInput = ObjectProperty(None)

    sp_to: Spinner = ObjectProperty(None)
    text_to: TextInput = ObjectProperty(None)

    btn_delete: Button = ObjectProperty(None)

    def on_pre_enter(self, *args):
        pass

    def on_enter_pressed(self):
        app: PeCreierulBaseApp | None = App.get_running_app()

        if app is None:
            return
        
        if len(self.text_from.text) < 1 or len(self.text_to.text) < 1:
            self.text_to.focus = len(self.text_to.text) < 1
            self.text_from.focus = len(self.text_from.text) < 1
            return
        
        editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")
        lesson_id = editLesson.lesson_id
        with Session(app.engine) as session:
            try:
                repository: LessonRepository = app.repository
                lesson: Lesson = repository.load_lesson_by_id(session, lesson_id)
                tags: List[Tag] = app.repository.load_all_tags(session)
                tag_from = next(filter(lambda x: x.name == self.sp_from.text, tags), None)
                tag_to = next(filter(lambda x: x.name == self.sp_to.text, tags), None)
                
                if tag_from is not None and tag_to is not None:

                    lesson_term = next(filter(lambda x: x.id == self.lesson_term_id, lesson.lesson_terms), None)

                    is_update = lesson_term is not None

                    if is_update:
                        lesson_term.term1.value = self.text_from.text
                        lesson_term.term2.value = self.text_to.text

                        if lesson_term.term1.tag.id != tag_from.id:
                            lesson_term.term1.tag = tag_from

                        if lesson_term.term2.tag_id != tag_to.id:
                            lesson_term.term2.tag = tag_to
                        
                    else:
                        lesson_term = LessonTerm(term1 = Term(value=self.text_from.text, tag=tag_from), term2 = Term(value = self.text_to.text, tag = tag_to))

                        lesson.lesson_terms.append(lesson_term)

                    app.repository.save_lessons(session, [lesson])

                    session.commit()

                    self.lesson_term_id = lesson_term.id

                    if not is_update:
                        editLesson.add_empty_termbox(tags, tag_from.name, tag_to.name)

            except Exception as ex:
                print(ex)
                session.rollback()

    def delete_lesson_term(self):
        app: PeCreierulBaseApp | None = App.get_running_app()

        if app is None:
            return
        
        editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")
        lesson_id = editLesson.lesson_id
        with Session(app.engine) as session:
            try:
                repository: LessonRepository = app.repository
                lesson: Lesson = repository.load_lesson_by_id(session, lesson_id)

                to_be_deleted = next(filter(lambda x: x.id == self.lesson_term_id, lesson.lesson_terms), None)

                if to_be_deleted is not None:
                    lesson.lesson_terms.remove(to_be_deleted)
                    repository.save_lessons(session, [lesson])
                
                session.commit()

                editLesson.edit_lesson_list.remove_widget(self)

            except Exception as ex:
                print(ex)
                session.rollback()

class TagBox(BoxLayout):
    text_tag: TextInput = ObjectProperty(None)
    btn_delete: Button = ObjectProperty(None)
    tag_id: int = -1

    def on_pre_enter(self, *args):
        self.btn_delete.disabled = self.tag_id < 0

    def on_enter_pressed(self):
        app: PeCreierulBaseApp | None = App.get_running_app()

        if app is None or len(self.text_tag.text) < 1:
            return

        self.text_tag.background_color = (1, 1, 1, 1)
        tag = Tag()
        with Session(app.engine) as session:
            try:
                tag.name = self.text_tag.text
                if self.tag_id > -1:
                    tag.id = self.tag_id

                app.repository.save_tag(session, tag)

                session.commit()

                if tag.id > -1:
                    self.tag_id = tag.id

                editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")

                ##editLesson.edit_tag_list.add_widget(TagBox())

                editLesson.on_pre_enter()
            except Exception as e:
                print(e)
                session.rollback()
                self.text_tag.background_color = (1, 0, 0, 1)

    def delete_tag(self):
        app: PeCreierulBaseApp | None = App.get_running_app()

        if app is None or self.tag_id < 0:
            return
        
        with Session(app.engine) as session:
            try:
                app.repository.delete_tag_by_id(session, self.tag_id)
                session.commit()

                editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")

                ##editLesson.edit_tag_list.remove_widget(self)

                editLesson.on_pre_enter()

            except Exception as ex:
                print(ex)
                session.rollback()

class EditLessonScreen(Screen):
    
    lesson_id: int = -1
    edit_lesson_list: GridLayout = ObjectProperty(None)
    edit_tag_list: GridLayout = ObjectProperty(None)
    lesson_name: Label = ObjectProperty(None)

    app: PeCreierulBaseApp | None

    def back(self):
        
        if self.app is None:
            return
        
        self.app.manager.current = "main_menu"

    def on_pre_enter(self, *args):
        
        self.app  = App.get_running_app()

        if self.app is None:
            return

        self.edit_lesson_list.clear_widgets()
        self.edit_tag_list.clear_widgets()

        with Session(self.app.engine) as session:
            lesson: Lesson = self.app.repository.load_lesson_by_id(session, self.lesson_id)
            tags: List[Tag] = self.app.repository.load_all_tags(session)
            self.lesson_name.text = lesson.name

            last_from_tag = ""
            last_to_tag = ""
            for lesson_term in lesson.lesson_terms:
                box = TermBox()
                box.lesson_term_id = lesson_term.id
                box.sp_from.values = [x.name for x in tags]
                box.sp_from.text = lesson_term.term1.tag.name
                last_from_tag = lesson_term.term1.tag.name

                box.text_from.text = lesson_term.term1.value

                box.sp_to.values = [x.name for x in tags]
                box.sp_to.text = lesson_term.term2.tag.name
                last_to_tag = lesson_term.term2.tag.name
                box.text_to.text = lesson_term.term2.value

                self.edit_lesson_list.add_widget(box)

            for tag in tags:
                box = TagBox()
                box.text_tag.text = tag.name
                box.tag_id = tag.id

                self.edit_tag_list.add_widget(box)

            self.add_empty_termbox(tags, last_from_tag, last_to_tag)

        self.edit_tag_list.add_widget(TagBox())

    def add_empty_termbox (self, tags: List[Tag], default_from_tag: str = "", default_to_tag: str = ""):
        box = TermBox()
        box.sp_from.values = [x.name for x in tags]
        box.sp_to.values = [x.name for x in tags]

        if default_from_tag is not None:
            box.sp_from.text = default_from_tag

        if default_to_tag is not None:
            box.sp_to.text = default_to_tag
        
        self.edit_lesson_list.add_widget(box)
