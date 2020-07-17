import json
import time

from kivy.uix.popup import Popup
from kivy.uix.settings import SettingsWithSidebar
from kivymd.app import MDApp

from widgets.map.alert_map_view import AlertMapView
from helpers.apis.server import Server
from helpers.gps.gps import Gps
from widgets.base import Base
from widgets.popup import PopupPersonalizado


class MainApp(MDApp):
    seguir = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with open("settings.json", 'r') as json_file:
            self.settings = json.load(json_file)

        with open("persistence.json", 'r') as json_file:
            self.globals = json.load(json_file)

    def on_start(self):
        def on_add_phone_cb(request, results):
            print(request.resp_status)
            if request.resp_status == 201:
                print("add_phone_succ")
                self.globals["pid"] = results["data"]["pid"]
                self.globals["route"] = False
                self.seguir = True
                print(self.globals)
                estado = self.config.get("general", "notify_cars")
                Server.settings_helper_add("notify_cars", estado, True)
                estado = self.config.get("general", "notify_bikes")
                Server.settings_helper_add("notify_bikes", estado, True)
                estado = self.config.get("general", "notify_trucks")
                Server.settings_helper_add("notify_trucks", estado, True)
                self.gps = Gps()
                self.gps.run()
            else:
                popup = PopupPersonalizado("El servidor no responde")

                popupWindow = Popup(title="Error al conectarse al servidor", content=popup, size_hint=(None, None),
                                    size=(400, 400))

                popupWindow.open()

        # Conectarse al server
        Server("server/phone/", "POST", {'type': 'placeholder'}, on_add_phone_cb, on_add_phone_cb,
               on_add_phone_cb).execute()

    def on_stop(self):
        def on_del_phone_cb(request, results):
            print(request.resp_status)
            if request.resp_status == 200:
                print("del_phone_succ")
                print(results["data"])

                with open("persistence.json", 'w') as json_file:
                    json.dump({}, json_file)

                print("borrado global pid")
            elif request.resp_status == 404:
                print("del_phone_fallo")
                print(results)
            else:
                print("del_phone_fallo")
                print(results)
                quit()

        url = f"server/phone/{'-1' if not self.globals else self.globals['pid']}"
        Server(url, "DELETE", None, on_del_phone_cb, on_del_phone_cb, on_del_phone_cb).execute().wait()

    def build(self):
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        return Base()

    def build_config(self, config):
        config.setdefaults('inicio', {
            'inicio': True
        })
        config.setdefaults('general', {
            'vehicle_type': 'car',
            'notify_cars': False,
            'notify_bikes': False,
            'notify_trucks': False,
            'sound_notifications': False})

    def build_settings(self, settings):

        data = json.dumps(self.settings)

        settings.add_json_panel("Settings", self.config, data=data)

    def on_config_change(self, config, section, key, value):
        print(config, section, key, value)

        if key == "vehicle_type":
            Server(f"server/phone/{self.globals['pid']}?type=true", "PUT", {"type": value},
                   lambda request, results: print(request.resp_status),
                   lambda request, results: print(request.resp_status),
                   lambda request, results: print(request.resp_status)).execute()
        elif key == "sound_notifications":
            pass
        else:
            if value == "0":
                Server.settings_helper_del(key)
            elif value == "1":
                Server.settings_helper_add(key, value, False)


if __name__ == '__main__':
    MainApp().run()
