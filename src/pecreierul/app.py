from sqlalchemy import Engine

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from pecreierul.trainer import Trainer

class PeCreierulBaseApp(App):

    engine: Engine
    trainer: Trainer
    manager: ScreenManager


    

