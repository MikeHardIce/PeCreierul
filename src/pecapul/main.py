from sqlalchemy import create_engine

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from pecreierul.app import PeCreierulBaseApp
from pecreierul.database import Base
from pecreierul.editscreen import EditLessonScreen
from pecreierul.menuscreen import PeCreierulMenuScreen
from pecreierul.trainer import Trainer

Window.top = 50
Window.left = 100
Window.size = (1600, 900)

class PeCreierulWindowManager(ScreenManager):
    pass

class PeCreierulApp(PeCreierulBaseApp):

    def build(self):
        self.engine = create_engine('sqlite:///my_database.db', echo=True)
    
        Base.metadata.create_all(self.engine)

        self.trainer = Trainer()
        self.manager = PeCreierulWindowManager()

        self.manager.add_widget(PeCreierulMenuScreen(name="main_menu"))
        self.manager.add_widget(EditLessonScreen(name="edit_lesson"))

        return self.manager

def main():
    PeCreierulApp().run()

if __name__ == '__main__':
    main()