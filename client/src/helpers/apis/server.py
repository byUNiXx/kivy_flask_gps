import json

from kivy.app import App
from kivy.network.urlrequest import UrlRequest


class Server:

    def __init__(self, url, method, req_body, on_success, on_failure, on_error):
        self.url = "http://127.0.0.1:5000/" + url
        self.method = method
        self.req_body = req_body
        self.on_success = on_success
        self.on_error = on_error
        self.on_failure = on_failure

    def execute(self):
        return UrlRequest(url=self.url, on_success=self.on_success, on_failure=self.on_failure, on_error=self.on_error,
                          req_body=json.dumps(self.req_body), method=self.method,
                          req_headers={'Content-type': 'application/json'})

    @staticmethod
    def settings_helper_add(alarm_type, estado, wait):
        def on_add_phone_alarm_cb(request, results):
            if request.resp_status == 201:
                print("Alarma añadida al vehiculo correctamente")
            elif request.resp_status == 409:
                print("Alarma NO añadida al vehiculo 409")
            elif request.resp_status == 404:
                print("Alarma NO añadida al vehiculo 404")
                app.config.set("general", alarm_type, 0)
                print(results)
            else:
                print("Alarma NO añadida al vehiculo otro")
                app.config.set("general", alarm_type, 0)
                print(results)

        app = App.get_running_app()

        alarmas = {"notify_cars": 0, "notify_bikes": 1, "notify_trucks": 2}

        alarma = alarmas[alarm_type]

        if estado == "1":
            if wait:
                Server(f"server/vehicle/alarm?pid={app.globals['pid']}&aid={alarma}", "POST", None,
                       on_add_phone_alarm_cb, on_add_phone_alarm_cb, on_add_phone_alarm_cb).execute().wait()
            else:
                Server(f"server/vehicle/alarm?pid={app.globals['pid']}&aid={alarma}", "POST", None,
                       on_add_phone_alarm_cb, on_add_phone_alarm_cb, on_add_phone_alarm_cb).execute()

    @staticmethod
    def settings_helper_del(alarm_type):
        def on_del_phone_alarm_cb(request, results):
            if request.resp_status == 200:
                print("Alarma borrada del vehiculo correctamente")
            elif request.resp_status == 404:
                print("Alarma NO borrada del vehiculo 404")
                app.config.set("general", alarm_type, 1)
                print(results)
            else:
                print("Alarma NO borrada del vehiculo otro")
                app.config.set("general", alarm_type, 1)
                print(results)

        app = App.get_running_app()

        alarmas = {"notify_cars": 0, "notify_bikes": 1, "notify_trucks": 2}

        alarma = alarmas[alarm_type]

        Server(f"server/vehicle/alarm?pid={app.globals['pid']}&aid={alarma}", "DELETE", None,
               on_del_phone_alarm_cb, on_del_phone_alarm_cb, on_del_phone_alarm_cb).execute()

    @staticmethod
    def get_cercanos():
        mapa = App.get_running_app().root.ids.map

        lat = mapa.lat + 0.001
        lon = mapa.lon + 0.001

        return lat, lon
