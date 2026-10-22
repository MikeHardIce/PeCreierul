from __future__ import annotations

import os
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

    @staticmethod
    def is_path(path: str) -> bool:
        return os.path.isfile(os.path.join(os.getcwd(), path)) 

    

