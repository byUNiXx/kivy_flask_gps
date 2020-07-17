import uuid

from dateutil.parser import isoparse

from server.src.extensions import db
from server.src.models.alarm import Alarm
from server.src.models.phone import Phone
from server.src.models.phone_alarm import PhoneAlarm


class TestFunctionalPhoneAlarm:

    def test_add_phone_alarm_success(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()
        alarm = Alarm("car").save()

        res = test_app.post(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}")

        json = res.get_json()

        phone_alarm = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid)
        data = json["data"]

        assert res.status_code == 201
        assert json["success"]
        assert json['error'] is None
        assert data['pid'] == phone.pid
        assert data['aid'] == alarm.aid
        assert data['status'] is None
        assert data['timestamp'] is None

        assert phone_alarm is not None

    def test_add_phone_alarm_already_exists(self, test_app):
        alarm = Alarm("skate").save()
        phone = Phone(str(uuid.uuid4())).save()

        test_app.post(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}")
        res = test_app.post(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}")

        json = res.get_json()

        assert res.status_code == 409
        assert not json["success"]
        assert json['data'] is None
        assert json['error'] == 'Phone_alarm does already exist'

    def test_add_phone_not_exists_alarm_fail(self, test_app):
        alarm = Alarm("truck").save()

        res = test_app.post(f"/server/vehicle/alarm?pid=197c92f1-ef0d-41b2-8192-1444b232a5fd&aid={alarm.aid}")

        json = res.get_json()

        assert res.status_code == 404
        assert not json["success"]
        assert json['data'] is None
        assert json['error'] == 'Phone does not exist'

    def test_add_phone_alarm_not_exists_fail(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.post(f"/server/vehicle/alarm?pid={phone.pid}&aid=1")

        json = res.get_json()

        assert res.status_code == 404
        assert not json["success"]
        assert json['data'] is None
        assert json['error'] == 'Alarm does not exist'

    def test_delete_phone_alarm_success(self, test_app):
        alarm = Alarm("truck").save()
        phone = Phone(str(uuid.uuid4())).save()

        phone_alarm = PhoneAlarm()
        phone_alarm.alarm = alarm
        phone_alarm.phone = phone

        phone.alarms.append(phone_alarm)
        phone.save()

        res = test_app.delete(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}")

        json = res.get_json()

        phone_alarm = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid).all()

        assert res.status_code == 200
        assert json['success']
        assert json["data"] is None
        assert json['error'] is None

        assert not phone_alarm

    def test_delete_phone_not_exists_alarm_fail(self, test_app):
        alarm = Alarm("truck").save()

        res = test_app.delete(f"/server/vehicle/alarm?pid=197c92f1-ef0d-41b2-8192-1444b232a5fd&aid={alarm.aid}")

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Phone does not exist'

    def test_delete_phone_alarm_not_exists_fail(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.delete(f"/server/vehicle/alarm?pid={phone.pid}&aid=1")

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Alarm does not exist'

    def test_delete_phone_alarm_no_relation_fail(self, test_app):
        alarm = Alarm("truck").save()
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.delete(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}")

        json = res.get_json()

        phone_alarm = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid).all()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Phone_alarm does not exist'

        assert not phone_alarm

    def test_update_phone_alarm_success(self, test_app):
        alarm = Alarm("car").save()
        phone = Phone(str(uuid.uuid4())).save()

        phone_alarm = PhoneAlarm()

        phone_alarm.alarm = alarm
        phone_alarm.phone = phone
        phone.alarms.append(phone_alarm)
        phone_alarm.save()

        res = test_app.put(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}", json={
            "timestamp": "20200607T032905Z", "status": True
        })

        json = res.get_json()
        data = json["data"]

        phone_alarm_db = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid).all()
        phone_alarm_db = phone_alarm_db.pop().serialize()

        assert res.status_code == 200
        assert json['success']
        assert json['error'] is None

        assert data["pid"] == phone_alarm.phone_id == phone_alarm_db["pid"]
        assert data["aid"] == phone_alarm.alarm_id == phone_alarm_db["aid"]
        assert data["status"]
        assert phone_alarm_db["status"]
        assert data["timestamp"] == "20200607T032905Z" == phone_alarm_db["timestamp"]

    def test_update_phone_not_exists_alarm_fail(self, test_app):
        alarm = Alarm("car").save()

        res = test_app.put(f"/server/vehicle/alarm?pid=197c92f1-ef0d-41b2-8192-1444b232a5fd&aid={alarm.aid}", json={
            "timestamp": "20200607T032905Z", "status": True
        })

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == "Phone does not exist"

    def test_update_phone_alarm_not_exists_fail(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.put(f"/server/vehicle/alarm?pid={phone.pid}&aid=1", json={
            "timestamp": "20200607T032905Z", "status": True
        })

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == "Alarm does not exist"

    def test_update_phone_alarm_no_relation_fail(self, test_app):
        alarm = Alarm("car").save()
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.put(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}", json={
            "timestamp": "20200607T032905Z", "status": True
        })

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == "Phone_Alarm does not exist"

    def test_update_phone_alarm_invalid_timestamp_fail(self, test_app):
        alarm = Alarm("car").save()
        phone = Phone(str(uuid.uuid4())).save()

        phone_alarm = PhoneAlarm()

        phone_alarm.alarm = alarm
        phone_alarm.phone = phone
        phone.alarms.append(phone_alarm)
        phone_alarm.save()

        res = test_app.put(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}", json={
            "timestamp": "20200607032905Z", "status": True
        })

        json = res.get_json()

        assert res.status_code == 403
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == "Invalid timestamp"

    def test_get_phone_alarm_success(self, test_app):
        alarm = Alarm("car").save()
        phone = Phone(str(uuid.uuid4())).save()

        phone_alarm = PhoneAlarm()
        phone_alarm.timestamp = isoparse("20200607T032905Z")
        phone_alarm.status = True
        phone_alarm.alarm = alarm
        phone_alarm.phone = phone

        phone.alarms.append(phone_alarm)
        phone.save()

        res = test_app.get(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}")

        json = res.get_json()

        assert res.status_code == 200
        assert json["success"]
        assert json["error"] is None

        data = json["data"]

        assert data["pid"] == phone.pid
        assert data["aid"] == alarm.aid
        assert data["timestamp"] == "20200607T032905Z"
        assert data["status"]

    def test_get_phone_not_exists_alarm_fail(self, test_app):
        alarm = Alarm("skate").save()

        res = test_app.get(f"/server/vehicle/alarm?pid=197c92f1-ef0d-41b2-8192-1444b232a5fd&aid={alarm.aid}")

        json = res.get_json()

        assert res.status_code == 404
        assert not json["success"]
        assert json["data"] is None
        assert json['error'] == 'Phone does not exist'

    def test_get_phone_alarm_not_exists_fail(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.get(f"/server/vehicle/alarm?pid={phone.pid}&aid=1")

        json = res.get_json()

        assert res.status_code == 404
        assert not json["success"]
        assert json["data"] is None
        assert json['error'] == 'Alarm does not exist'

    def test_get_phone_alarm_no_relation_fail(self, test_app):
        alarm = Alarm("truck").save()
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.get(f"/server/vehicle/alarm?pid={phone.pid}&aid={alarm.aid}")

        json = res.get_json()

        phone_alarm = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid).all()

        assert res.status_code == 404
        assert not json["success"]
        assert json['data'] is None
        assert json['error'] == 'Phone_Alarm does not exist'
        assert not phone_alarm

    def test_get_all_phone_alarm_success(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()

        boolean = True

        for x in range(2):
            alarm = Alarm("car").save()

            phone_alarm = PhoneAlarm()
            phone_alarm.alarm = alarm
            phone_alarm.phone = phone

            phone_alarm.timestamp = isoparse("20200607T032905Z")
            phone_alarm.status = boolean

            phone.alarms.append(phone_alarm)

            boolean = not boolean

        phone.save()

        res = test_app.get(f"/server/vehicle/alarm?pid={phone.pid}")

        json = res.get_json()
        data = json["data"]

        assert res.status_code == 200
        assert json["success"]
        assert json["error"] is None

        assert len(data) == 2

        phone_alarm = data.pop(0)

        assert phone_alarm["pid"] is not None
        assert phone_alarm["aid"] is not None
        assert phone_alarm["timestamp"] == "20200607T032905Z"
        assert phone_alarm["status"]

        phone_alarm = data.pop(0)

        assert phone_alarm["pid"] is not None
        assert phone_alarm["aid"] is not None
        assert phone_alarm["timestamp"] == "20200607T032905Z"
        assert not phone_alarm["status"]

    def test_get_all_phone_alarms_fail(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()

        res = test_app.get(f"/server/vehicle/alarm?pid={phone.pid}")

        json = res.get_json()

        assert res.status_code == 404
        assert not json["success"]
        assert json["data"] is None
        assert json["error"] == "This pid does not have any phone_alarm"
