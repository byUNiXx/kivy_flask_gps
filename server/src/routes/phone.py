import uuid

from dateutil.parser import isoparse
from flask import request, Blueprint, abort
from sqlalchemy.exc import IntegrityError

from models.phone import Moving, Phone
from models.response import ResponseJSON

phone = Blueprint('phone', __name__, url_prefix='/server/phone')


@phone.route('/', methods=['POST'])
def add_phone():
    if not request.json or 'type' not in request.json:
        abort(400)

    while True:
        try:
            device = Phone(str(uuid.uuid4())).save()
            break
        except IntegrityError as e:
            pass

    return ResponseJSON(True, device.serialize(), None).serialize(), 201


@phone.route('/<string:pid_phone>', methods=['DELETE'])
def delete_phone(pid_phone):

    device = Phone.query.get(pid_phone)

    if not device:
        return ResponseJSON(False, None, 'Does not exist').serialize(), 404

    device.delete()

    return ResponseJSON(True, None, None).serialize(), 200


@phone.route('/start_route/<string:pid_phone>', methods=['POST'])
def start_route(pid_phone):
    if not request.json or 'type' not in request.json or not pid_phone or \
            'utc' not in request.json:
        abort(400)

    data = request.json

    try:
        device = Moving(pid_phone, request.remote_addr, data['type'], data['utc'], None, None, None, None).save()

        return ResponseJSON(True, device.serialize(), None).serialize(), 201

    except IntegrityError as e:

        if str(e.orig) == "CHECK constraint failed: types":
            return ResponseJSON(False, None, 'Not added, invalid type').serialize(), 403
        else:
            return ResponseJSON(False, None, 'Not exist, invalid pid').serialize(), 404
    except ValueError:
        print("ValueError start_route")
        return ResponseJSON(False, None, 'Not exist, invalid pid').serialize(), 404


@phone.route('/stop_route/<string:pid_phone>', methods=['DELETE'])
def stop_route(pid_phone):
    device_m = Moving.query.get(pid_phone)

    if not device_m:
        return ResponseJSON(False, None, 'Does not exist').serialize(), 404

    device_m.delete()

    return ResponseJSON(True, None, None).serialize(), 200


@phone.route('/<string:pid_phone>', methods=['PUT'])
def update_phone(pid_phone):
    if len(request.args) == 0:
        abort(400)

    # Compruebo si existe en la bbdd
    device_m: Moving = Moving.query.get(pid_phone)

    if not device_m:
        return ResponseJSON(False, None, 'Does not exist').serialize(), 404

    # Actualiza pos
    if request.args.get('pos'):
        # Si no tiene alguno de los campos necesarios --> abort
        if not request.json or 'lat' not in request.json or 'lon' not in request.json\
                or 'alt' not in request.json or 'timestamp' not in request.json:
            abort(400)

        # Se comprueba si el timestamp del request es correcto
        try:
            request_timestamp = isoparse(request.json['timestamp'])
        except:
            return ResponseJSON(False, None, 'Invalid timestamp').serialize(), 403

        # Comparator of timestamps
        if device_m.timestamp is not None:

            actual_timestamp = isoparse(str(device_m.timestamp) + device_m.utc)

            # Si el timestamp del request es anterior al de la bbdd, no se añade
            if request_timestamp < actual_timestamp:
                return ResponseJSON(False, None, 'Invalid timestamp').serialize(), 403

        try:
            device_m.lat = request.json['lat']
            device_m.lon = request.json['lon']
            device_m.alt = request.json['alt']
            device_m.timestamp = request_timestamp
        except ValueError:
            return ResponseJSON(False, None, 'Invalid coords').serialize(), 403

    # Actualiza ip
    elif request.args.get('ip'):

        device_m.ip = request.remote_addr

    # Actualiza tipo
    elif request.args.get('type'):
        if not request.json or 'type' not in request.json:
            abort(400)

        device_m.type = request.json['type']

    # Actualiza utc
    elif request.args.get('utc'):
        if not request.json or 'utc' not in request.json:
            abort(400)

        device_m.utc = request.json['utc']

    # No se ha especificado nada en la query
    else:
        return ResponseJSON(False, None, 'No query params').serialize(), 405

    # Actualiza la BBDD, si el tipo es incorrecto lanza IntegrityError
    try:
        device_m.update()
    except IntegrityError as e:
        if str(e.orig) == "CHECK constraint failed: types":
            return ResponseJSON(False, None, 'Not added, invalid type').serialize(), 403

    return ResponseJSON(True, device_m.serialize(), None).serialize(), 200


@phone.route('/<string:pid_phone>', methods=['GET'])
def get_phone(pid_phone):

    device = Moving.query.get(pid_phone)

    # Obtiene el dispositivo de la BBDD, si no existe devuelve el error
    if not device:
        device = Phone.query.get(pid_phone)
        if not device:
            return ResponseJSON(False, None, "Does not exist").serialize(), 404

    # Se serializan los datos del dispositivo
    data = device.serialize()

    # Si se trata de un dispositivo sin ruta iniciada
    if isinstance(device, Phone):
        # Si el cliente quiere datos no disponibles en un dispositivo sin ruta iniciada, lanza el error
        if len(request.args) > 0:
            return ResponseJSON(False, None, "Invalid params for phone instance").serialize(), 405

    # Si el cliente quiere la posicion del dispositivo
    elif request.args.get('pos'):
        data.pop("ip")
        data.pop("type")
        data.pop("utc")

    # Si el cliente quiere la posicion del dipositivo
    elif request.args.get('type'):
        data.pop("ip")
        data.pop("utc")
        data.pop("lat")
        data.pop("lon")
        data.pop("alt")
        data.pop("timestamp")

    # Si el cliente quiere el utc del dipositivo
    elif request.args.get('utc'):
        data.pop("ip")
        data.pop("type")
        data.pop("lat")
        data.pop("lon")
        data.pop("alt")
        data.pop("timestamp")

    return ResponseJSON(True, data, None).serialize(), 200

# @phone.route('nearby/<string:pid_phone>', methods=['GET'])
# def get_nearby_phones(pid_phone):
#     if not request.json or "alarms" not in request.json:
#         abort(400)
#
#     device = Moving.query.get(pid_phone)
#
#     # Obtiene el dispositivo de la BBDD, si no existe devuelve el error
#     if not device:
#         device = Phone.query.get(pid_phone)
#         if not device:
#             return ResponseJSON(False, None, "Does not exist").serialize(), 404
#
#     # Si se trata de un dispositivo sin ruta iniciada
#     if isinstance(device, Phone):
#         return ResponseJSON(False, None, "Invalid params for phone instance").serialize(), 405
#
#     # Select phone_mov from moving where type= "car" or "truck" or "bike; Dependiendo de alarmas que se pasan en json
#     # Por cada moving hacer:
#     # geopy https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude/43211266#43211266
#     # Si distancia menos de x meter en variable
#     # Enviar al cliente
#
#     return ResponseJSON(True, data, None).serialize(), 200
