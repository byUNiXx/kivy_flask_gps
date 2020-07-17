from server.src.models.alarm import Alarm


class TestFunctionalAlarm:

    def test_add_alarm_success(self, test_app):
        res = test_app.post('/server/alarm', json={
            'name': 'coche'
        })

        json = res.get_json()
        data = json["data"]

        alarm = Alarm.query.get(data['aid'])

        assert res.status_code == 201
        assert json["success"]
        assert json["error"] is None

        assert data["name"] == alarm.name == "coche"

    def test_delete_alarm_exists_success(self, test_app):
        alarm = Alarm("truck").save()

        res = test_app.delete(f'/server/alarm/{alarm.aid}')

        json = res.get_json()
        alarm = Alarm.query.get(alarm.aid)

        assert res.status_code == 200
        assert json["success"]
        assert json["error"] is None
        assert json["data"] is None

        assert alarm is None

    def test_delete_alarm_not_exists_fail(self, test_app):
        res = test_app.delete('/server/alarm/1')

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Does not exist'

    def test_update_alarm_not_exist_fail(self, test_app):
        res = test_app.put('/server/alarm/1?name=true')

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Does not exist'

    def test_update_alarm_name_success(self, test_app):
        alarm = Alarm("skate").save()

        res = test_app.put(f'/server/alarm/{alarm.aid}?name=true', json={"name": 'truck'})

        json = res.get_json()

        data = json["data"]
        alarm_db = Alarm.query.get(alarm.aid)

        assert res.status_code == 200
        assert json['success']
        assert json['error'] is None

        assert alarm_db.aid == alarm.aid == data["aid"]
        assert alarm_db.name == "truck" == data["name"]
        assert alarm_db.description is None
        assert data["description"] is None

    def test_update_alarm_description_success(self, test_app):
        alarm = Alarm("skate").save()

        res = test_app.put(f'/server/alarm/{alarm.aid}?desc=true',
                           json={"description": "Alarma para alertar de skates cercanos"})

        json = res.get_json()

        data = json["data"]
        alarm_db = Alarm.query.get(alarm.aid)

        assert res.status_code == 200
        assert json['success']
        assert json['error'] is None

        assert alarm_db.aid == alarm.aid == data["aid"]
        assert alarm_db.name == "skate" == data["name"]
        assert alarm_db.description == "Alarma para alertar de skates cercanos" == data["description"]

    def test_get_alarm_exists_success(self, test_app):
        alarm = Alarm("truck").save()
        alarm.description = "Alarma para alertar de camiones cercanos"
        alarm.update()

        res = test_app.get(f'/server/alarm/{alarm.aid}')

        json = res.get_json()
        data = json["data"]

        assert res.status_code == 200
        assert json["success"]
        assert json['error'] is None

        assert data["aid"] == alarm.aid
        assert data["name"] == "truck"
        assert data["description"] == "Alarma para alertar de camiones cercanos"

    def test_get_alarm_not_exists_fail(self, test_app):
        res = test_app.get('/server/alarm/1')

        json = res.get_json()

        assert res.status_code == 404
        assert not json["success"]
        assert json["data"] is None
        assert json['error'] == 'Does not exist'
