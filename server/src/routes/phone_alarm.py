from dateutil.parser import isoparse
from flask import request, Blueprint, abort
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.alarm import Alarm
from models.phone import Phone
from models.phone_alarm import PhoneAlarm
from models.response import ResponseJSON

phone_alarm_routes = Blueprint("phone_alarm", __name__, url_prefix="/server/vehicle/alarm")


@phone_alarm_routes.route("/", methods=["POST"])
def add_phone_alarm():
    if request.args.get("pid") is None or request.args.get("aid") is None:
        abort(400)

    phone = Phone.query.get(request.args.get("pid"))
    alarm = Alarm.query.get(request.args.get("aid"))

    if not phone:
        return ResponseJSON(False, None, "Phone does not exist").serialize(), 404
    if not alarm:
        return ResponseJSON(False, None, "Alarm does not exist").serialize(), 404

    phone_alarm = PhoneAlarm()

    phone_alarm.alarm = alarm
    phone_alarm.phone = phone

    try:
        phone.alarms.append(phone_alarm)
        phone.save()
    except IntegrityError:
        return ResponseJSON(False, None, "Phone_alarm does already exist").serialize(), 409

    return ResponseJSON(True, phone_alarm.serialize(), None).serialize(), 201


@phone_alarm_routes.route("/", methods=["DELETE"])
def delete_phone_alarm():
    if request.args.get("pid") is None or request.args.get("aid") is None:
        abort(400)

    phone = Phone.query.get(request.args.get("pid"))
    alarm = Alarm.query.get(request.args.get("aid"))

    if not phone:
        return ResponseJSON(False, None, "Phone does not exist").serialize(), 404
    if not alarm:
        return ResponseJSON(False, None, "Alarm does not exist").serialize(), 404

    phone_alarm = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid).all()

    if not phone_alarm:
        return ResponseJSON(False, None, "Phone_alarm does not exist").serialize(), 404

    phone.alarms.remove(phone_alarm.pop())
    phone.save()

    return ResponseJSON(True, None, None).serialize(), 200


@phone_alarm_routes.route("/", methods=["PUT"])
def update_phone_alarm():
    if request.args.get("pid") is None or request.args.get("aid") is None or not request.json["timestamp"] \
            or not request.json["status"]:
        abort(400)

    phone = Phone.query.get(request.args.get("pid"))
    alarm = Alarm.query.get(request.args.get("aid"))

    if not phone:
        return ResponseJSON(False, None, "Phone does not exist").serialize(), 404
    if not alarm:
        return ResponseJSON(False, None, "Alarm does not exist").serialize(), 404

    phone_alarm_list = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid).all()

    if not phone_alarm_list:
        return ResponseJSON(False, None, "Phone_Alarm does not exist").serialize(), 404

    phone_alarm = phone_alarm_list.pop()
    phone.alarms.remove(phone_alarm)

    try:
        request_timestamp = isoparse(request.json['timestamp'])
    except:
        return ResponseJSON(False, None, 'Invalid timestamp').serialize(), 403

    phone_alarm.timestamp = request_timestamp
    phone_alarm.status = request.json["status"]

    phone.alarms.append(phone_alarm)
    phone.save()

    return ResponseJSON(True, phone_alarm.serialize(), None).serialize(), 200


@phone_alarm_routes.route("/", methods=["GET"])
def get_phone_alarm():
    if request.args.get("pid") is None or request.args.get("aid") is None and request.args.get("pid") is None:
        abort(400)

    phone = Phone.query.get(request.args.get("pid"))

    if not phone:
        return ResponseJSON(False, None, "Phone does not exist").serialize(), 404

    if not request.args.get("aid"):
        phone_alarms = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid).all()

        if not phone_alarms:
            return ResponseJSON(False, None, "This pid does not have any phone_alarm").serialize(), 404

        serialized_list = []

        for phone_alarm in phone_alarms:
            serialized_list.append(phone_alarm.serialize())

        return ResponseJSON(True, serialized_list, None).serialize(), 200

    else:
        alarm = Alarm.query.get(request.args.get("aid"))

        if not alarm:
            return ResponseJSON(False, None, "Alarm does not exist").serialize(), 404

        phone_alarm = db.session.query(PhoneAlarm).filter_by(phone_id=phone.pid, alarm_id=alarm.aid).all()

        if not phone_alarm:
            return ResponseJSON(False, None, "Phone_Alarm does not exist").serialize(), 404

        return ResponseJSON(True, phone_alarm.pop().serialize(), None).serialize(), 200
