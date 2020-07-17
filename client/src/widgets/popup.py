from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout


class PopupPersonalizado(FloatLayout):
    descripcion = StringProperty()

    def __init__(self, descripcion, **kwargs):
        super().__init__(**kwargs)
        self.descripcion = descripcion

    def close(self):
        quit()
