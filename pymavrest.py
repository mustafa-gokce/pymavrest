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
parameter_count = []


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
        result = parameter_data[parameter_name]
    else:
        result = {}
    return flask.jsonify(result)


@application.errorhandler(code_or_exception=404)
def page_not_found(error):
    return flask.jsonify({})


def receive_telemetry(master, timeout, drop, white, black, param):
    global message_data, message_enumeration, parameter_data, parameter_count_total, parameter_count

    if timeout == 0:
        timeout = None

    if drop == 0:
        drop = None

    white_list = {"PARAM_VALUE"} if white == "" else {"PARAM_VALUE"} | {x for x in white.split(",")}
    black_list = {} if black == "" else {x for x in black.split(",")}

    if not param:
        black_list |= {"PARAM_VALUE"}

    while True:

        vehicle = utility.mavlink_connection(device=master)

        if param:
            vehicle.wait_heartbeat()
            vehicle.mav.param_request_list_send(vehicle.target_system, vehicle.target_component)

        while True:

            message_raw = vehicle.recv_match(blocking=True, timeout=timeout)

            if not message_raw:
                break

            message_dict = message_raw.to_dict()
            message_name = message_dict.pop("mavpackettype")

            if message_name in black_list:
                continue

            if len(white_list) > 1 and message_name not in white_list:
                continue

            if message_name == "PARAM_VALUE":
                parameter_data[message_dict["param_id"]] = message_dict["param_value"]
                parameter_count_total = message_dict["param_count"]
                parameter_count.append(message_dict["param_index"])
                continue

            if param and parameter_count_total != len(parameter_data):
                for i in range(parameter_count_total):
                    if i not in parameter_count:
                        vehicle.mav.param_request_read_send(vehicle.target_system, vehicle.target_component, b"", i)
                        break

            if message_name not in message_data.keys():
                message_data[message_name] = {}

            message_data[message_name] = {**message_data[message_name], **message_dict}
            message_id = message_raw.get_msgId()
            message_enumeration[message_name] = message_id
            time_monotonic = time.monotonic()
            time_now = time.time()

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
                message_data[message_name]["statistics"]["counter"] += 1
                message_data[message_name]["statistics"]["latency"] = time_monotonic - message_data[message_name]["statistics"]["last_monotonic"]
                message_data[message_name]["statistics"]["last"] = time_now
                message_data[message_name]["statistics"]["last_monotonic"] = time_monotonic
                message_data[message_name]["statistics"]["duration"] = message_data[message_name]["statistics"]["last_monotonic"] - message_data[message_name]["statistics"]["first_monotonic"]
                message_data[message_name]["statistics"]["instant_frequency"] = 1.0 / message_data[message_name]["statistics"]["latency"]
                message_data[message_name]["statistics"]["average_frequency"] = message_data[message_name]["statistics"]["counter"] / message_data[message_name]["statistics"]["duration"]

            if drop:
                for message_name in list(message_data.keys()):
                    if message_data[message_name]["statistics"]["latency"] > drop:
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
def main(host, port, master, timeout, drop, white, black, param):
    threading.Thread(target=receive_telemetry, args=(master, timeout, drop, white, black, param)).start()
    server = gevent.pywsgi.WSGIServer(listener=(host, port), application=application, log=application.logger)
    server.serve_forever()


if __name__ == "__main__":
    main()
