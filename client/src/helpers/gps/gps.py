import datetime
import threading
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy_garden.mapview.clustered_marker_layer import Marker
from kivymd.uix.dialog import MDDialog

from plyer import gps

from client.src.helpers.apis.server import Server
from client.src.widgets.map.alert_map_view import AlertMapView
from widgets.popup import PopupPersonalizado


class Gps:
    mock = False

    def run(self):
        if platform == "android":

            from android.permissions import Permission, request_permissions

            def permissions(permission, results):
                if all([res for res in results]):
                    gps.configure(on_location=self.update_pos_android, on_status=self.permission_status)
                    gps.start(minTime=2000, minDistance=0)
                else:
                    popup = PopupPersonalizado(
                        "Se necesitan permisos de localizacion para disfrutar de los servicios de esta aplicación")

                    popupWindow = Popup(title="Error permisos de localizacion", content=popup, size_hint=(None, None),
                                        size=(400, 400))

                    popupWindow.open()

            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.ACCESS_FINE_LOCATION], permissions)
            app = App.get_running_app()
            app.globals["android"] = True
            Clock.schedule_interval(self.update_pos_android, 3)
        else:
            app = App.get_running_app()
            app.globals["android"] = False
            print(app.globals)
            Clock.schedule_interval(self.update_pos_windows, 3)

    def permission_status(self, general_status, status_message):
        if general_status == "provider-enabled":
            pass
        else:
            popup = MDDialog(title="GPS Permissions Error", text="This applications needs GPS permissions")
            popup.size_hint = [.8, .8]
            popup.pos_hint = {"center_x:": .5, "center_y": .5}
            popup.open()

    def change_mock_display(self, dt):
        print("cambio mock")
        self.mock = not self.mock

    def update_pos_android(self, *args, **kwargs):
        mapa = App.get_running_app().root.ids.map

        lat = kwargs['lat']
        lon = kwargs['lon']

        gps_pointer = mapa.ids.pointer
        gps_pointer.lat = lat
        gps_pointer.lon = lon

        mapa.center_on(lat, lon)

        app = App.get_running_app()

        if app.globals["route"]:
            t = threading.Thread(name="daemon_android", target=partial(self.api_calls, app, lat, lon, self.mock))
            t.setDaemon(True)
            print("Va a empezar el hilo daemon_android")
            t.start()

    def update_pos_windows(self, dt):
        mapa = App.get_running_app().root.ids.map
        lat = mapa.lat
        lon = mapa.lon
        gps_pointer = mapa.ids.pointer

        gps_pointer.lat = lat
        gps_pointer.lon = lon

        app = App.get_running_app()

        if app.globals["route"]:
            t = threading.Thread(name="daemon_windows", target=partial(self.api_calls, app, lat, lon, self.mock))
            t.setDaemon(True)
            print("Va a empezar el hilo daemon_windows")
            t.start()

    @staticmethod
    def api_calls(app, lat, lon, mock):

        def on_update_pos_cb(request, results):
            if request.resp_status == 200:
                print("Pos actualizada correctamente")
            elif request.resp_status == 403:
                print("Pos no actualizada 403")
                print(results)
            elif request.resp_status == 404:
                print("Pos no actualizada PID invalido")
                print(results)
            else:
                print("Pos no actualizada otro")
                print(results)

        def on_get_phone_alarm_cb(args, request, results):
            if request.resp_status == 200:
                print("Alarmas obtenidas correctamente")
                args["alarm"] = False
                print(results)
            elif request.resp_status == 404:
                print("No existen alarmas, 404")
                print(results)
            else:
                print("Get alarmas fail otro")
                print(results)

        # Envio posicion al servidor
        # Compruebo alarma
        # Pido al servidor vehiculos cerca mios
        # Añado markers
        local_thread_vars = threading.local()
        local_thread_vars.data = {}

        print(lat, lon)
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"

        Server(f"server/phone/{app.globals['pid']}?pos=true", "PUT", {'lat': lat, 'lon': lon, 'alt': -9999,
                                                                      'timestamp': timestamp},
               on_update_pos_cb, on_update_pos_cb, on_update_pos_cb).execute().wait()

        Server(f"server/vehicle/alarm?pid={app.globals['pid']}", "GET", None,
               partial(on_get_phone_alarm_cb, local_thread_vars.data),
               partial(on_get_phone_alarm_cb, local_thread_vars.data),
               partial(on_get_phone_alarm_cb, local_thread_vars.data)).execute().wait()

        if "alarm" in local_thread_vars.data and local_thread_vars.data["alarm"] or mock:
            # Hacer mock en api helper que sea getCercanos, donde en un futuro ira el bueno
            # En ese mock devolver una lista de posicion
            # De esa lista coger la posicion y ponerla en el mapa
            # Probar a compilar con bulldozer
            # Al final activar sonido if settings sonido then sonido

            if App.get_running_app().config.get("general", "notify_cars") == "1":
                mapa = App.get_running_app().root.ids.map
                lat, lon = Server.get_cercanos()
                mapa.marcador = (1, lat, lon)
                print("Mock activado")
