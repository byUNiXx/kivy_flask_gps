from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout

from helpers.apis.server import Server

Builder.load_string('''
#:include widgets/map/alert_map_view.kv
#:include widgets/popup.kv

<Base>:
    AlertMapView:
        id: map

    MDIconButton:
        id: navigation_button
        icon: 'assets/navigation.png'
        on_release: root.change_state_route()
        pos_hint: {"center_x": .08, "center_y": .08}
        user_font_size: "48sp"

    MDIconButton:
        id: settings_button
        icon: 'assets/settings.png'
        on_release: app.open_settings()
        pos_hint: {"center_x": .92, "center_y": .92}
        user_font_size: "48sp"
''')


class Base(FloatLayout):

    def change_state_route(self):
        def on_start_route_cb(request, results):
            if request.resp_status == 201:
                print("Ruta comenzada correctamente")
                app.globals["route"] = True
            elif request.resp_status == 403:
                print("Ruta no comenzada 403 tipo invalido")
                print(results)
            elif request.resp_status == 404:
                print("Ruta no comenzada PID invalido")
                print(results)
            else:
                print("Ruta no comenzada otro")
                print(results)

        def on_stop_route_cb(request, results):
            if request.resp_status == 200:
                print("Ruta acabada correctamente")
                app.globals["route"] = False
            elif request.resp_status == 404:
                print("Ruta no acabada PID invalido")
                print(results)
            else:
                print("Ruta no acabada otro")
                print(results)

        app = App.get_running_app()
        if not app.globals["route"]:
            print("Empiezo ruta")
            tipo = app.config.get("general", "vehicle_type")
            Server(f"server/phone/start_route/{app.globals['pid']}", "POST", {'type': tipo, 'utc': '+00:00'},
                   on_start_route_cb, on_start_route_cb, on_start_route_cb).execute()

        else:
            print("Acabo ruta")
            App.get_running_app().gps.mock = False
            App.get_running_app().root.ids.map.delete()

            Server(f"server/phone/stop_route/{app.globals['pid']}?pos=true", "DELETE", None,
                   on_stop_route_cb, on_stop_route_cb, on_stop_route_cb).execute()
