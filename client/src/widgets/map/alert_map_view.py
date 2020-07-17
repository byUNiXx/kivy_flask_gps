from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy_garden.mapview import MapView
from kivy_garden.mapview import MapMarker
from kivy.app import App

from widgets.map.gps_pointer import GpsPointer


class AlertMapView(MapView):
    lista_anadidos = []
    lista_marker = []

    marcador = ObjectProperty(None, allownone=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(marcador=self.add_vehicle)
        self.delete = self.delete_vehicles

    def add_vehicle(self, mapa, marcador):

        if marcador[0] is not -1 and marcador[0] not in self.lista_anadidos:
            marker = MapMarker(lat=marcador[1], lon=marcador[2])
            mapa.add_widget(marker)
            mapa.lista_marker.append(marker)
            mapa.lista_anadidos.append(marcador[0])
            print("anadido")

    def delete_vehicles(self):
        for marker in self.lista_marker:
            self.remove_marker(marker)
        self.lista_anadidos.clear()
        self.marcador = (-1, -1)

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            print("mock variado")
            Clock.schedule_once(App.get_running_app().gps.change_mock_display, 0.1)
