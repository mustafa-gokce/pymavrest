#!/usr/bin/python

import gevent.monkey

gevent.monkey.patch_all()

import time
import threading
import click
import pymavlink.mavutil as utility
import gevent.pywsgi
import flask

application = flask.Flask(import_name="pymavrest")

message_data = {}
message_enumeration = {}
parameter_data = {}
parameter_count_total = 0
parameter_count = set()
plan_data = []
plan_count_total = 0
plan_count = set()


@application.route(rule="/get/message/all", methods=["GET"])
def get_message_all():
    global message_data
    return flask.jsonify(message_data)


@application.route(rule="/get/message/<string:message_name>", methods=["GET"])
def get_message_with_name(message_name):
    global message_data
    if message_name in message_data.keys():
        result = message_data[message_name]
    else:
        result = {}
    return flask.jsonify(result)


@application.route(rule="/get/message/<int:message_id>", methods=["GET"])
def get_message_with_id(message_id):
    global message_data, message_enumeration
    if message_id in message_enumeration.values():
        message_name = list(message_enumeration.keys())[list(message_enumeration.values()).index(message_id)]
        if message_name in message_data.keys():
            result = message_data[message_name]
        else:
            result = {}
    else:
        result = {}
    return flask.jsonify(result)


@application.route(rule="/get/message/<string:message_name>/<string:field_name>", methods=["GET"])
def get_message_field_with_name(message_name, field_name):
    global message_data
    if message_name in message_data.keys():
        if field_name in message_data[message_name].keys():
            result = {field_name: message_data[message_name][field_name]}
        else:
            result = {}
    else:
        result = {}
    return flask.jsonify(result)


@application.route(rule="/get/message/<int:message_id>/<string:field_name>", methods=["GET"])
def get_message_field_with_id(message_id, field_name):
    global message_data, message_enumeration
    if message_id in message_enumeration.values():
        message_name = list(message_enumeration.keys())[list(message_enumeration.values()).index(message_id)]
        if message_name in message_data.keys():
            if field_name in message_data[message_name].keys():
                result = {field_name: message_data[message_name][field_name]}
            else:
                result = {}
        else:
            result = {}
    else:
        result = {}
    return flask.jsonify(result)


@application.route(rule="/get/parameter/all", methods=["GET"])
def get_parameter_all():
    global parameter_data
    return flask.jsonify(parameter_data)


@application.route(rule="/get/parameter/<string:parameter_name>", methods=["GET"])
def get_parameter_with_name(parameter_name):
    global parameter_data
    if parameter_name in parameter_data.keys():
        result = {parameter_name: parameter_data[parameter_name]}
    else:
        result = {}
    return flask.jsonify(result)


@application.route(rule="/get/plan/all", methods=["GET"])
def get_plan_all():
    global plan_data
    return flask.jsonify(plan_data)


@application.route(rule="/get/plan/<int:plan_index>", methods=["GET"])
def get_plan_with_index(plan_index):
    global plan_data
    result = {}
    for mission_item in plan_data:
        if mission_item["seq"] == plan_index:
            result = mission_item
            break
    return flask.jsonify(result)


@application.errorhandler(code_or_exception=404)
def page_not_found(error):
    return flask.jsonify({})


def receive_telemetry(master, timeout, drop, white, black, param, plan):
    global message_data, message_enumeration
    global parameter_data, parameter_count_total, parameter_count
    global plan_data, plan_count_total, plan_count

    if timeout == 0:
        timeout = None

    if drop == 0:
        drop = None

    white_list = {"PARAM_VALUE", "MISSION_COUNT", "MISSION_ITEM_INT", "MISSION_ACK"}
    white_list = white_list if white == "" else white_list | {x for x in white.split(",")}
    black_list = set() if black == "" else {x for x in black.split(",")}

    if not param:
        black_list |= {"PARAM_VALUE"}

    if not plan:
        black_list |= {"MISSION_COUNT", "MISSION_ITEM_INT", "MISSION_ACK"}

    while True:

        vehicle = utility.mavlink_connection(device=master)

        if param or plan:
            vehicle.wait_heartbeat()

        if param:
            vehicle.mav.param_request_list_send(vehicle.target_system, vehicle.target_component)

        if plan:
            vehicle.mav.mission_request_list_send(vehicle.target_system, vehicle.target_component)

        while True:

            message_raw = vehicle.recv_match(blocking=True, timeout=timeout)

            if not message_raw:
                break

            message_dict = message_raw.to_dict()
            message_name = message_dict.pop("mavpackettype")

            time_monotonic = time.monotonic()
            time_now = time.time()

            if message_name in black_list:
                continue

            if len(white) > 1 and message_name not in white_list:
                continue

            if message_name == "PARAM_VALUE":
                if message_dict["param_id"] not in parameter_data.keys():
                    parameter_data[message_dict["param_id"]] = {}
                parameter_data[message_dict["param_id"]]["value"] = message_dict["param_value"]
                parameter_count_total = message_dict["param_count"]
                parameter_count.add(message_dict["param_index"])

                if "statistics" not in parameter_data[message_dict["param_id"]].keys():
                    parameter_data[message_dict["param_id"]]["statistics"] = {}
                    parameter_data[message_dict["param_id"]]["statistics"]["counter"] = 1
                    parameter_data[message_dict["param_id"]]["statistics"]["latency"] = 0
                    parameter_data[message_dict["param_id"]]["statistics"]["first"] = time_now
                    parameter_data[message_dict["param_id"]]["statistics"]["first_monotonic"] = time_monotonic
                    parameter_data[message_dict["param_id"]]["statistics"]["last"] = time_now
                    parameter_data[message_dict["param_id"]]["statistics"]["last_monotonic"] = time_monotonic
                    parameter_data[message_dict["param_id"]]["statistics"]["duration"] = 0
                    parameter_data[message_dict["param_id"]]["statistics"]["instant_frequency"] = 0
                    parameter_data[message_dict["param_id"]]["statistics"]["average_frequency"] = 0

                else:
                    latency = time_monotonic - parameter_data[message_dict["param_id"]]["statistics"]["last_monotonic"]
                    first_monotonic = parameter_data[message_dict["param_id"]]["statistics"]["first_monotonic"]
                    duration = time_monotonic - first_monotonic
                    instant_frequency = 1.0 / latency if latency != 0.0 else 0.0
                    counter = parameter_data[message_dict["param_id"]]["statistics"]["counter"]
                    average_frequency = counter / duration if duration != 0.0 else 0.0
                    parameter_data[message_dict["param_id"]]["statistics"]["counter"] += 1
                    parameter_data[message_dict["param_id"]]["statistics"]["latency"] = latency
                    parameter_data[message_dict["param_id"]]["statistics"]["last"] = time_now
                    parameter_data[message_dict["param_id"]]["statistics"]["last_monotonic"] = time_monotonic
                    parameter_data[message_dict["param_id"]]["statistics"]["duration"] = duration
                    parameter_data[message_dict["param_id"]]["statistics"]["instant_frequency"] = instant_frequency
                    parameter_data[message_dict["param_id"]]["statistics"]["average_frequency"] = average_frequency

                continue

            if param and parameter_count_total != len(parameter_data):
                for i in range(parameter_count_total):
                    if i not in parameter_count:
                        vehicle.mav.param_request_read_send(vehicle.target_system, vehicle.target_component, b"", i)
                        break

            if message_name == "MISSION_ACK":
                if message_dict["type"] == 0 and message_dict["mission_type"] == 0:
                    plan_data = []
                    plan_count = set()
                    vehicle.mav.mission_request_list_send(vehicle.target_system, vehicle.target_component)

                continue

            if message_name == "MISSION_COUNT":
                if message_dict["mission_type"] == 0:
                    plan_count_total = message_dict["count"]
                    vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, 0)

                continue

            if message_name == "MISSION_ITEM_INT":
                if message_dict["seq"] not in plan_count:
                    message_dict["statistics"] = {}
                    message_dict["statistics"]["counter"] = 1
                    message_dict["statistics"]["latency"] = 0
                    message_dict["statistics"]["first"] = time_now
                    message_dict["statistics"]["first_monotonic"] = time_monotonic
                    message_dict["statistics"]["last"] = time_now
                    message_dict["statistics"]["last_monotonic"] = time_monotonic
                    message_dict["statistics"]["duration"] = 0
                    message_dict["statistics"]["instant_frequency"] = 0
                    message_dict["statistics"]["average_frequency"] = 0
                    plan_data.append(message_dict)
                    plan_count.add(message_dict["seq"])

                    if message_dict["seq"] < plan_count_total - 1:
                        seq = message_dict["seq"] + 1
                        vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, seq)

                continue

            if plan and plan_count_total != len(plan_count):
                for i in range(plan_count_total):
                    if i not in plan_count:
                        vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, i)
                        break

            if message_name not in message_data.keys():
                message_data[message_name] = {}

            message_data[message_name] = {**message_data[message_name], **message_dict}
            message_id = message_raw.get_msgId()
            message_enumeration[message_name] = message_id

            if "statistics" not in message_data[message_name].keys():
                message_data[message_name]["statistics"] = {}
                message_data[message_name]["statistics"]["counter"] = 1
                message_data[message_name]["statistics"]["latency"] = 0
                message_data[message_name]["statistics"]["first"] = time_now
                message_data[message_name]["statistics"]["first_monotonic"] = time_monotonic
                message_data[message_name]["statistics"]["last"] = time_now
                message_data[message_name]["statistics"]["last_monotonic"] = time_monotonic
                message_data[message_name]["statistics"]["duration"] = 0
                message_data[message_name]["statistics"]["instant_frequency"] = 0
                message_data[message_name]["statistics"]["average_frequency"] = 0

            else:
                latency = time_monotonic - message_data[message_name]["statistics"]["last_monotonic"]
                first_monotonic = message_data[message_name]["statistics"]["first_monotonic"]
                duration = time_monotonic - first_monotonic
                instant_frequency = 1.0 / latency if latency != 0.0 else 0.0
                counter = message_data[message_name]["statistics"]["counter"]
                average_frequency = counter / duration if duration != 0.0 else 0
                message_data[message_name]["statistics"]["counter"] += 1
                message_data[message_name]["statistics"]["latency"] = latency
                message_data[message_name]["statistics"]["last"] = time_now
                message_data[message_name]["statistics"]["last_monotonic"] = time_monotonic
                message_data[message_name]["statistics"]["duration"] = duration
                message_data[message_name]["statistics"]["instant_frequency"] = instant_frequency
                message_data[message_name]["statistics"]["average_frequency"] = average_frequency

            if drop:
                for message_name in list(message_data.keys()):
                    if time_monotonic - message_data[message_name]["statistics"]["last_monotonic"] > drop:
                        message_data.pop(message_name)


@click.command()
@click.option("--host", default="127.0.0.1", type=click.STRING, required=False,
              help="Pymavrest server IP address.")
@click.option("--port", default=2609, type=click.IntRange(min=0, max=65535), required=False,
              help="Pymavrest server port number.")
@click.option("--master", default="udpin:127.0.0.1:14550", type=click.STRING, required=False,
              help="Standard MAVLink connection string.")
@click.option("--timeout", default=5.0, type=click.FloatRange(min=0, clamp=True), required=False,
              help="Try to reconnect after this seconds when no message is received, zero means do not reconnect")
@click.option("--drop", default=5.0, type=click.FloatRange(min=0, clamp=True), required=False,
              help="Drop non-periodic messages after this seconds, zero means do not drop.")
@click.option("--white", default="", type=click.STRING, required=False,
              help="Comma separated white list to filter messages, empty means all messages are in white list.")
@click.option("--black", default="", type=click.STRING, required=False,
              help="Comma separated black list to filter messages.")
@click.option("--param", default=True, type=click.BOOL, required=False,
              help="Fetch parameters.")
@click.option("--plan", default=True, type=click.BOOL, required=False,
              help="Fetch plan.")
def main(host, port, master, timeout, drop, white, black, param, plan):
    threading.Thread(target=receive_telemetry, args=(master, timeout, drop, white, black, param, plan)).start()
    server = gevent.pywsgi.WSGIServer(listener=(host, port), application=application, log=application.logger)
    server.serve_forever()


if __name__ == "__main__":
    main()
