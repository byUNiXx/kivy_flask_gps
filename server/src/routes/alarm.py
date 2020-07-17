from flask import request, Blueprint, abort

from models.alarm import Alarm
from models.response import ResponseJSON

alarm_routes = Blueprint("alarm", __name__, url_prefix="/server/alarm")


@alarm_routes.route("/", methods=["POST"])
def add_alarm():
    if not request.json or 'name' not in request.json:
        abort(400)

    alarm = Alarm(request.json["name"]).save()

    return ResponseJSON(True, alarm.serialize(), None).serialize(), 201


@alarm_routes.route("/<int:aid_alarm>", methods=["DELETE"])
def delete_alarm(aid_alarm):

    alarm = Alarm.query.get(aid_alarm)

    if not alarm:
        return ResponseJSON(False, None, "Does not exist").serialize(), 404

    alarm.delete()

    return ResponseJSON(True, None, None).serialize(), 200


@alarm_routes.route("/<int:aid_alarm>", methods=["PUT"])
def update_alarm(aid_alarm):
    if len(request.args) == 0 or not request.args.get("name") and not request.args.get("desc"):
        abort(400)

    alarm = Alarm.query.get(aid_alarm)

    if not alarm:
        return ResponseJSON(False, None, "Does not exist").serialize(), 404

    if request.args.get("name"):
        if not request.json or "name" not in request.json:
            abort(400)

        alarm.name = request.json["name"]

    elif request.args.get("desc"):
        if not request.json or "description" not in request.json:
            abort(400)

        alarm.description = request.json["description"]

    alarm.update()

    return ResponseJSON(True, alarm.serialize(), None).serialize(), 200


@alarm_routes.route("/<int:aid_alarm>", methods=["GET"])
def get_alarm(aid_alarm):
    alarm = Alarm.query.get(aid_alarm)

    if not alarm:
        return ResponseJSON(False, None, "Does not exist").serialize(), 404

    return ResponseJSON(True, alarm.serialize(), None).serialize(), 200
