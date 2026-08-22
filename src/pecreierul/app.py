from __future__ import annotations

from typing import cast

from sqlalchemy import Engine

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from pecreierul.lesson_repository import LessonRepository

class PeCreierulBaseApp(App):

    engine: Engine
    repository: LessonRepository
    manager: ScreenManager

    @staticmethod
    def get_running_app() -> PeCreierulBaseApp:
        return cast(PeCreierulBaseApp, App.get_running_app())

    

