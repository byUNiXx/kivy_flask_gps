import uuid

from dateutil.parser import isoparse
from sqlalchemy.exc import IntegrityError

from server.src.models.phone import Phone, Moving


class TestFunctionalPhone:

    def test_add_phone_success(self, test_app):
        res = test_app.post('/server/phone', json={
            'type': 'car'
        })

        json = res.get_json()

        data = json["data"]
        phone_db = Phone.query.get(data['pid'])

        assert res.status_code == 201
        assert json['success']
        assert json['error'] is None

        assert len(data['pid']) == 36
        assert data['pid'] == phone_db.pid

    def test_delete_phone_exist_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()

        res = test_app.delete(f'/server/phone/{device.pid}')

        json = res.get_json()
        device = Phone.query.get(device.pid)

        assert res.status_code == 200
        assert json["success"]
        assert json["data"] is None
        assert json["error"] is None

        assert device is None

    def test_delete_phone_no_exist_fail(self, test_app):
        res = test_app.delete('/server/phone/197c92f1-ef0d-41b2-8192-1444b232a5fd')

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Does not exist'

    def test_delete_phone_with_moving_success(self, test_app):
        phone = Phone(str(uuid.uuid4())).save()
        phone = Moving(phone.pid, '85.47.41.69', 'car', '+00:00', None, None, None, None).save()

        res = test_app.delete(f'/server/phone/{phone.pid}')

        json = res.get_json()

        phone_db = Phone.query.get(phone.pid)
        phonem_db = Moving.query.get(phone.pid)

        assert res.status_code == 200
        assert json["success"]
        assert json["data"] is None
        assert json["error"] is None

        assert phone_db is None
        assert phonem_db is None

    def test_start_route_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()

        res = test_app.post(f'/server/phone/start_route/{device.pid}', json={
            'type': 'car', 'utc': '+12:00'
        })

        pid = device.pid

        json = res.get_json()
        data = json["data"]

        phone_db = Moving.query.get(pid)
        phone_db = phone_db.serialize()

        assert res.status_code == 201
        assert json['success']
        assert json['error'] is None

        assert phone_db["pid"] == pid == data["pid"]
        assert phone_db["type"] == 'car' == data["type"]
        assert phone_db["utc"] == '+12:00' == data["utc"]
        assert phone_db["ip"] == data["ip"] and phone_db["ip"] is not None
        assert phone_db["lat"] is None and data["lat"] is None
        assert phone_db["lon"] is None and data["lon"] is None
        assert phone_db["alt"] is None and data["alt"] is None
        assert phone_db["timestamp"] is None and data["timestamp"] is None

    def test_start_route_with_invalid_type_fail(self, test_app):
        device = Phone(str(uuid.uuid4())).save()

        res = test_app.post(f'/server/phone/start_route/{device.pid}', json={
            'type': 'invalid', 'utc': '+12:00'
        })

        json = res.get_json()
        phone_db = Moving.query.get(device.pid)

        assert res.status_code == 403
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Not added, invalid type'

        assert phone_db is None

    def test_start_route_with_not_added_phone_fail(self, test_app):
        res = test_app.post('/server/phone/start_route/197c52f1-ef0d-41b2-8192-1444b232a5fd', json={
            'type': 'car', 'utc': '+12:00'
        })

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Not exist, invalid pid'

    def test_stop_route_exists_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '85.47.41.69', 'car', '+00:00', 39.985748, -0.049478, 12.455,
               isoparse("20200607T032905Z")).save()

        res = test_app.delete(f'/server/phone/stop_route/{pid}')

        json = res.get_json()
        device = Phone.query.get(pid)
        device_m = Moving.query.get(pid)

        assert res.status_code == 200
        assert json['success']
        assert json["data"] is None
        assert json['error'] is None

        assert device.pid == pid
        assert device_m is None

    def test_stop_route_not_exists_fail_success(self, test_app):
        res = test_app.delete('/server/phone/stop_route/197c52f1-ef0d-41b2-8192-1444b232a5fd')

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Does not exist'

    def test_update_phone_not_exists_fail(self, test_app):
        res = test_app.put('/server/phone/197c92f1-ef0d-41b2-8192-1444b232a5fd?pos=true', json={
            'lat': -85.12, 'lon': 1740.001, 'alt': 12.4514, 'timestamp': '20200607T032905Z'
        })

        json = res.get_json()

        assert res.status_code == 404
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Does not exist'

    def test_update_phone_pos_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '85.47.41.69', 'car', '+00:00', None, None, None, None).save()

        res = test_app.put(f'/server/phone/{pid}?pos=true', json={
            'lat': 39.985748, 'lon': -0.049478, 'alt': 12.455, 'timestamp': '20200607T032905Z'
        })

        json = res.get_json()
        data = json["data"]

        phone_db = Moving.query.get(pid)
        phone_db = phone_db.serialize()

        assert res.status_code == 200
        assert json['success']
        assert json['error'] is None

        assert phone_db["pid"] == pid == data["pid"]
        assert phone_db["lat"] == 39.985748 == data["lat"]
        assert phone_db["lon"] == -0.049478 == data["lon"]
        assert phone_db["alt"] == 12.455 == data["alt"]
        assert phone_db["timestamp"] == "20200607T032905Z" == data["timestamp"]

        assert phone_db["type"] == "car" == data["type"]
        assert phone_db["utc"] == "+00:00" == data["utc"]
        assert phone_db["ip"] == '85.47.41.69' == data["ip"]

    def test_update_phone_pos_invalid_coords_fail(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        device = Moving(pid, '85.47.41.69', 'car', '+00:00', 39.985748, -0.049478, 12.455,
                        isoparse("20200607T032905Z")).save()

        res = test_app.put(f'/server/phone/{pid}?pos=true', json={
            'lat': -90.001, 'lon': 180.001, 'alt': 12.4514, 'timestamp': '20200607T042905Z'
        })

        json = res.get_json()

        phone_db = Moving.query.get(device.pid)
        phone_db = phone_db.serialize()

        assert res.status_code == 403
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Invalid coords'

        assert phone_db["pid"] == pid
        assert phone_db["lat"] == 39.985748
        assert phone_db["lon"] == -0.049478
        assert phone_db["alt"] == 12.455
        assert phone_db["timestamp"] == "20200607T032905Z"
        assert phone_db["type"] == "car"
        assert phone_db["utc"] == "+00:00"
        assert phone_db["ip"] == '85.47.41.69'

    def test_update_phone_pos_invalid_timestamp_fail(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '85.47.41.69', 'car', '+00:00', 39.985748, -0.049478, 12.455,
               isoparse("20200607T032905Z")).save()

        # Primero comprueba si falla al añadir un timestamp anterior al guardado en el sistema
        # Segundo comprueba si falla al añadir un timestamp invalido

        consultas = [test_app.put(f'/server/phone/{pid}?pos=true',
                                  json={'lat': -10.005, 'lon': 179.636, 'alt': 12.4515,
                                        'timestamp': '20200607T032805Z'}),
                     test_app.put(f'/server/phone/{pid}?pos=true', json={
                         'lat': -10.005, 'lon': 179.636, 'alt': 12.4515, 'timestamp': '20200607052905Z'
                     })]

        for x in range(len(consultas)):
            res = consultas[x]

            json = res.get_json()

            phone_db = Moving.query.get(pid)
            phone_db = phone_db.serialize()

            assert res.status_code == 403
            assert not json['success']
            assert json["data"] is None
            assert json['error'] == 'Invalid timestamp'

            assert phone_db["pid"] == pid
            assert phone_db["lat"] == 39.985748
            assert phone_db["lon"] == -0.049478
            assert phone_db["alt"] == 12.455
            assert phone_db["timestamp"] == "20200607T032905Z"
            assert phone_db["type"] == "car"
            assert phone_db["utc"] == "+00:00"
            assert phone_db["ip"] == '85.47.41.69'

    def test_update_phone_ip_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '-1', 'car', '+00:00', None, None, None, None).save()

        res = test_app.put(f'/server/phone/{pid}?ip=true')

        json = res.get_json()
        data = json["data"]

        assert res.status_code == 200
        assert json['success']
        assert json['error'] is None

        assert data["pid"] == pid
        assert data["lat"] is None
        assert data["lon"] is None
        assert data["alt"] is None
        assert data["timestamp"] is None
        assert data["type"] == "car"
        assert data["utc"] == "+00:00"
        assert data["ip"] != "-1"

    def test_update_phone_type_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        device = Moving(device.pid, '85.47.41.69', 'car', '+00:00', 39.985748, -0.049478, 12.455,
                        isoparse("20200607T032905Z")).save()

        pid = device.pid

        res = test_app.put(f'/server/phone/{pid}?type=true', json={'type': 'truck'})

        json = res.get_json()
        data = json["data"]

        phone_db = Moving.query.get(pid)
        phone_db = phone_db.serialize()

        assert res.status_code == 200
        assert json['success']
        assert json['error'] is None

        assert phone_db["pid"] == pid == data["pid"]
        assert phone_db["lat"] == 39.985748 == data["lat"]
        assert phone_db["lon"] == -0.049478 == data["lon"]
        assert phone_db["alt"] == 12.455 == data["alt"]
        assert phone_db["timestamp"] == "20200607T032905Z" == data["timestamp"]

        assert phone_db["type"] == "truck" == data["type"]
        assert phone_db["utc"] == "+00:00" == data["utc"]
        assert phone_db["ip"] == '85.47.41.69' == data["ip"]

    def test_update_phone_invalid_type_fail(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        device = Moving(device.pid, '85.47.41.69', 'car', '+00:00', None, None, None, None).save()

        pid = device.pid

        res = test_app.put(f'/server/phone/{pid}?type=true', json={'type': 'invalid'})

        json = res.get_json()

        phone_db = Moving.query.get(pid)
        phone_db = phone_db.serialize()

        assert res.status_code == 403
        assert not json['success']
        assert json["data"] is None
        assert json['error'] == 'Not added, invalid type'

        assert phone_db["pid"] == pid
        assert phone_db["lat"] is None
        assert phone_db["lon"] is None
        assert phone_db["alt"] is None
        assert phone_db["timestamp"] is None
        assert phone_db["type"] == "car"
        assert phone_db["utc"] == "+00:00"
        assert phone_db["ip"] == '85.47.41.69'

    def test_update_phone_utc_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        device = Moving(device.pid, '85.47.41.69', 'car', '+00:00', 39.985748, -0.049478, 12.455,
                        isoparse("20200607T032905Z")).save()

        pid = device.pid

        res = test_app.put(f'/server/phone/{pid}?utc=true', json={'utc': '-05:00'})

        json = res.get_json()
        data = json["data"]

        phone_db = Moving.query.get(pid)
        phone_db = phone_db.serialize()

        assert res.status_code == 200
        assert json['success']
        assert json['error'] is None

        assert phone_db["pid"] == pid == data["pid"]
        assert phone_db["lat"] == 39.985748 == data["lat"]
        assert phone_db["lon"] == -0.049478 == data["lon"]
        assert phone_db["alt"] == 12.455 == data["alt"]
        assert phone_db["timestamp"] == "20200607T032905Z" == data["timestamp"]

        assert phone_db["type"] == "car" == data["type"]
        assert phone_db["utc"] == "-05:00" == data["utc"]
        assert phone_db["ip"] == '85.47.41.69' == data["ip"]

    def test_get_phone_exists_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '85.48.41.69', 'skate', '+03:00', 39.985748, -0.049478, 12.455,
               isoparse("20200607T032905Z")).save()

        res = test_app.get(f'/server/phone/{pid}')

        json = res.get_json()
        data = json['data']

        assert res.status_code == 200
        assert json["success"]
        assert json['error'] is None

        assert data['pid'] == pid
        assert data["ip"] == '85.48.41.69'
        assert data['type'] == 'skate'
        assert data['utc'] == '+03:00'
        assert data['lat'] == 39.985748
        assert data['lon'] == -0.049478
        assert data['alt'] == 12.455
        assert data['timestamp'] == "20200607T032905Z"

        # Overkill, pero por si acaso
        while True:
            try:
                device = Phone(str(uuid.uuid4())).save()
                break
            except IntegrityError as e:
                pass

        # Get de un phone sin ruta
        pid = device.pid

        res = test_app.get(f'/server/phone/{pid}')

        json = res.get_json()
        data = json['data']

        assert res.status_code == 200
        assert json["success"]
        assert json['error'] is None

        assert data['pid'] == pid
        assert len(data) == 1

    def test_get_phone_no_exists_fail(self, test_app):
        res = test_app.get('/server/phone/197c92f1-ef0d-41b2-8192-1444b232a5fd')

        json = res.get_json()

        assert res.status_code == 404
        assert not json["success"]
        assert json["data"] is None
        assert json['error'] == 'Does not exist'

    def test_get_phone_pos_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '85.48.41.69', 'skate', '+03:00', 39.985748, -0.049478, 12.455,
               isoparse("20200607T032905Z")).save()

        res = test_app.get(f'/server/phone/{pid}?pos=true')

        json = res.get_json()
        data = json['data']

        assert res.status_code == 200
        assert json["success"]
        assert json['error'] is None

        assert len(data) == 5

        assert data['lat'] == 39.985748
        assert data['lon'] == -0.049478
        assert data['alt'] == 12.455
        assert data['timestamp'] == "20200607T032905Z"

    def test_get_phone_type_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '85.48.41.69', 'truck', '+03:00', 39.985748, -0.049478, 12.455,
               isoparse("20200607T032905Z")).save()

        res = test_app.get(f'/server/phone/{pid}?type=true')

        json = res.get_json()
        data = json['data']

        assert res.status_code == 200
        assert json["success"]
        assert json['error'] is None

        assert len(data) == 2
        assert data["pid"] == pid
        assert data['type'] == 'truck'

    def test_get_phone_utc_success(self, test_app):
        device = Phone(str(uuid.uuid4())).save()
        pid = device.pid
        Moving(pid, '85.48.41.69', 'skate', '-08:00', 39.985748, -0.049478, 12.455,
               isoparse("20200607T032905Z")).save()

        res = test_app.get(f'/server/phone/{pid}?utc=true')

        json = res.get_json()
        data = json['data']

        assert res.status_code == 200
        assert json["success"]
        assert json['error'] is None

        assert len(data) == 2
        assert data["pid"] == pid
        assert data['utc'] == '-08:00'
