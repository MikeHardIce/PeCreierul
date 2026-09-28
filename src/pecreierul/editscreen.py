import os
from typing import Dict, List, Tuple, cast
from sqlalchemy.orm import Session

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView

from pecreierul.app import PeCreierulBaseApp
from pecreierul.importer_exporter import ImporterExporter
from pecreierul.lesson_repository import LessonRepository
from pecreierul.database import LessonTerm, Tag, Lesson, Term

Builder.load_file(os.path.join(os.path.dirname(__file__), 'editscreen.kv'))

class AddTagBox(Button):
    def add_item(self):
        app = PeCreierulBaseApp.get_running_app()
        edit: EditLessonScreen = app.manager.get_screen("edit_lesson")

        tag = TagBox()
        tag.loaded = True
        edit.edit_tag_list.add_widget(tag, 1)

class AddItemBox(Button):

    default_tags: Tuple[str, str]

    def add_item(self):
        app = PeCreierulBaseApp.get_running_app()
        edit: EditLessonScreen = app.manager.get_screen("edit_lesson")

        with Session(app.engine) as session:
            tags = app.repository.load_all_tags(session)

            if self.default_tags is not None:
                edit.add_empty_termbox(tags, self.default_tags[0], self.default_tags[1])
            else:
                edit.add_empty_termbox(tags)


class TermBox(BoxLayout):
    lesson_term_id: int = -1
    loaded: bool = False
    pending_changes: bool = False

    sp_from: Spinner = ObjectProperty(None)
    text_from: TextInput = ObjectProperty(None)

    sp_to: Spinner = ObjectProperty(None)
    text_to: TextInput = ObjectProperty(None)

    btn_delete: Button = ObjectProperty(None)

    def on_text_input(self, *args):
        if self.loaded:
            app = PeCreierulBaseApp.get_running_app()

            edit: EditLessonScreen = app.manager.get_screen("edit_lesson")
            self.pending_changes = True
            edit.set_has_unsaved_changes()

    def on_pre_enter(self, *args):
        pass

    def get_selected_tags(self, session: Session, repository: LessonRepository) -> Tuple[List[Tag], Tag, Tag]:
        tags: List[Tag] = repository.load_all_tags(session)
        tag_from = cast(Tag, next(filter(lambda x: x.name == self.sp_from.text, tags), None))
        tag_to = cast(Tag, next(filter(lambda x: x.name == self.sp_to.text, tags), None))

        return tags, tag_from, tag_to

    def save_to_lesson(self, session: Session, repository: LessonRepository, lesson_id: int) -> Tuple[LessonTerm, bool]:
        if len(self.text_from.text) < 1 or len(self.text_to.text) < 1:
            self.text_to.focus = len(self.text_to.text) < 1
            self.text_from.focus = len(self.text_from.text) < 1
            return LessonTerm(), False

        lesson: Lesson = repository.load_lesson_by_id(session, lesson_id)
        _, tag_from, tag_to = self.get_selected_tags(session, repository)
        
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

            repository.save_lessons(session, [lesson])

            return lesson_term, is_update
        return LessonTerm(), False

    def on_enter_pressed(self):
        pass
        # app = PeCreierulBaseApp.get_running_app()
        
        # editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")
        # lesson_id = editLesson.lesson_id
        # with Session(app.engine) as session:
        #     try:
        #         repository: LessonRepository = app.repository
        #         tags, tag_from, tag_to = self.get_selected_tags(session, repository)
        #         lesson_term, is_update = self.save_to_lesson(session, repository, lesson_id)

        #         session.commit()

        #         self.lesson_term_id = lesson_term.id

        #         if not is_update:
        #             editLesson.add_empty_termbox(tags, tag_from.name, tag_to.name)

        #     except Exception as ex:
        #         print(ex)
        #         session.rollback()

    def delete_lesson_term(self):
        app = PeCreierulBaseApp.get_running_app()

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
    pending_changes: bool = False
    loaded: bool = False

    def on_text_input(self):
        if self.loaded:
            self.pending_changes = True
            app = PeCreierulBaseApp.get_running_app()
            edit: EditLessonScreen = app.manager.get_screen("edit_lesson")

            edit.set_has_unsaved_changes()

    def on_pre_enter(self, *args):
        self.btn_delete.disabled = self.tag_id < 0

    def on_enter_pressed(self):
        pass
        # app = PeCreierulBaseApp.get_running_app()

        # if len(self.text_tag.text) < 1:
        #     return

        # self.text_tag.background_color = (1, 1, 1, 1)
        # tag = Tag()
        # with Session(app.engine) as session:
        #     try:
        #         tag.name = self.text_tag.text
        #         if self.tag_id > -1:
        #             tag.id = self.tag_id

        #         app.repository.save_tag(session, tag)

        #         session.commit()

        #         if tag.id > -1:
        #             self.tag_id = tag.id

        #         editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")

        #         ##editLesson.edit_tag_list.add_widget(TagBox())

        #         editLesson.reload_all_lesson_data()
        #     except Exception as e:
        #         print(e)
        #         session.rollback()
        #         self.text_tag.background_color = (1, 0, 0, 1)

    def delete_tag(self):
        app = PeCreierulBaseApp.get_running_app()

        if self.tag_id < 0:
            return
        
        with Session(app.engine) as session:
            try:
                app.repository.delete_tag_by_id(session, self.tag_id)
                session.commit()

                editLesson: EditLessonScreen = app.manager.get_screen("edit_lesson")

                ##editLesson.edit_tag_list.remove_widget(self)

                editLesson.reload_all_lesson_data()

            except Exception as ex:
                print(ex)
                session.rollback()

class EditLessonScreen(Screen):
    
    lesson_id: int = -1
    unsaved_changes: bool = False

    edit_lesson_list: GridLayout = ObjectProperty(None)
    edit_tag_list: GridLayout = ObjectProperty(None)
    lesson_name: Label = ObjectProperty(None)
    lbl_unsaved_changes: Label = ObjectProperty(None)
    btn_save_changes: Button = ObjectProperty(None)

    def set_has_unsaved_changes(self):
        self.unsaved_changes = True
        self.lbl_unsaved_changes.text = "Unsaved Changes"
        self.btn_save_changes.disabled = False
        #self.lbl_unsaved_changes.opacity = 1

    def set_has_no_unsaved_changes(self):
        self.unsaved_changes = False
        self.lbl_unsaved_changes.text = ""
        self.btn_save_changes.disabled = True
        #self.lbl_unsaved_changes.opacity = 0

    def on_import_pressed(self):
        content = BoxLayout(orientation="vertical")
        chooser = FileChooserListView()

        btn_select = Button(text="Import", size_hint_y= .15)
        chooser.path = os.path.dirname(__file__)
        content.add_widget(chooser)
        content.add_widget(btn_select)

        popup = Popup(title="Select a lesson file", content=content, size_hint=(0.9, 0.9))

        def import_lesson(btn):
            
            if chooser.selection and len(chooser.selection) > 0 and os.path.isfile(chooser.selection[0]):
                print("Importing Lesson")
                app = PeCreierulBaseApp.get_running_app()
                with Session(app.engine) as session:
                    lesson = app.repository.load_lesson_by_id(session, self.lesson_id)
                    tags: Dict[str, Tag] = {}

                    for tag in app.repository.load_all_tags(session):
                        tags[tag.name] = tag
                    
                    ImporterExporter.import_lesson(lesson, tags, chooser.selection[0])
                    app.repository.save_lessons(session, [lesson])
                    session.commit()

            popup.dismiss()

            self.reload_all_lesson_data()

        
        btn_select.bind(on_release= import_lesson) # type: ignore

        popup.open()

    def on_export_pressed(self):
        def is_dir(directory, filename):
            return os.path.isdir(os.path.join(directory, filename))
        
        content = BoxLayout(orientation="vertical")
        chooser = FileChooserListView(dirselect=True)
        chooser.filters = [is_dir]
        btn_select = Button(text="Export", size_hint_y= .15)
        chooser.path = os.path.dirname(__file__)
        content.add_widget(chooser)
        content.add_widget(btn_select)

        popup = Popup(title="Choose a folder the lesson should be exported to", content=content, size_hint=(0.9, 0.9))

        def export_lesson(btn):
            
            if chooser.selection and len(chooser.selection) > 0 and os.path.isdir(chooser.selection[0]):
                print("Exporting Lesson")
                app = PeCreierulBaseApp.get_running_app()
                with Session(app.engine) as session:
                    lesson = app.repository.load_lesson_by_id(session, self.lesson_id)
                    
                    ImporterExporter.export_lesson(lesson, os.path.join(chooser.selection[0], f"{lesson.name}.csv"))

            popup.dismiss()

        btn_select.bind(on_release= export_lesson) # type: ignore

        popup.open()

    def save_changes(self):
        app = PeCreierulBaseApp.get_running_app()
        with Session(app.engine) as session:
            for box in self.edit_tag_list.children:
                if isinstance(box, TagBox):
                    box = cast(TagBox, box)

                    if box.pending_changes:
                        is_new = box.tag_id is None or box.tag_id < 0

                        tag = Tag(id= box.tag_id, name=box.text_tag.text)
                        if is_new:
                            tag = Tag(name=box.text_tag.text)

                        app.repository.save_tag(session, tag)
            
            for box in self.edit_lesson_list.children:
                if isinstance(box, TermBox):
                    box = cast(TermBox, box)

                    if box.pending_changes:
                        box.save_to_lesson(session, app.repository, self.lesson_id)
           
            session.commit()

        self.reload_all_lesson_data()
            
        self.set_has_no_unsaved_changes()

    def back(self):
        
        app = PeCreierulBaseApp.get_running_app()
        
        app.manager.current = "main_menu"

    def reload_all_lesson_data(self):
        app = PeCreierulBaseApp.get_running_app()
        
        self.edit_lesson_list.clear_widgets()
        self.edit_tag_list.clear_widgets()

        with Session(app.engine) as session:
            lesson: Lesson = app.repository.load_lesson_by_id(session, self.lesson_id)
            tags: List[Tag] = app.repository.load_all_tags(session)
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

                box.loaded = True
                self.edit_lesson_list.add_widget(box)

            for tag in tags:
                box = TagBox()
                box.text_tag.text = tag.name
                box.tag_id = tag.id
                box.loaded = True
                self.edit_tag_list.add_widget(box)

            #self.add_empty_termbox(tags, last_from_tag, last_to_tag)
            button_add = AddItemBox()
            button_add.default_tags = last_from_tag, last_to_tag
            self.edit_lesson_list.add_widget(button_add)

        self.edit_tag_list.add_widget(AddTagBox())
        #self.edit_tag_list.add_widget(TagBox())

    def on_pre_enter(self, *args):
        self.reload_all_lesson_data()
        

    def add_empty_termbox (self, tags: List[Tag], default_from_tag: str = "", default_to_tag: str = ""):
        box = TermBox()
        box.sp_from.values = [x.name for x in tags]
        box.sp_to.values = [x.name for x in tags]

        if default_from_tag is not None:
            box.sp_from.text = default_from_tag

        if default_to_tag is not None:
            box.sp_to.text = default_to_tag

        box.loaded = True
        
        self.edit_lesson_list.add_widget(box, 1)

    # def on_enter(self, *args):
    #     Window.bind(on_key_down= self.global_on_key_down)

    # def on_leave(self, *args):
    #     Window.unbind(on_key_down= self.global_on_key_down)

    def global_on_key_down(self, window, key, *args):

        #filter(lambda w: w., self.edit_lesson_list.children)
        #widget = Window.focus_behavior
        # if key in (13, 271):
        #     app = PeCreierulBaseApp.get_running_app()
        #     with Session(app.engine) as session:
        #         for box in self.edit_lesson_list.children:
        #             if isinstance(box, TermBox):
        #                 box = cast(TermBox, box)

        #                 if box.pending_changes:
        #                     box.save_to_lesson(session, app.repository, self.lesson_id)

        #         session.commit()

        #     self.reload_all_lesson_data()
                
        #     self.set_has_no_unsaved_changes()
        #     return True

        return False