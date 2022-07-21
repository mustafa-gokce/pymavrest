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

telemetry_data = {}
message_enumeration = {}


@application.route(rule="/get/message/all", methods=["GET"])
def get_all():
    global telemetry_data
    return flask.jsonify(telemetry_data)


@application.route(rule="/get/message/<string:message_name>", methods=["GET"])
def get_message_with_name(message_name):
    global telemetry_data
    if message_name in telemetry_data:
        result = telemetry_data[message_name]
    else:
        result = {}
    return flask.jsonify(result)


@application.route(rule="/get/message/<int:message_id>", methods=["GET"])
def get_message_with_id(message_id):
    global telemetry_data, message_enumeration
    if message_id in message_enumeration.values():
        message_name = list(message_enumeration.keys())[list(message_enumeration.values()).index(message_id)]
        if message_name in telemetry_data:
            result = telemetry_data[message_name]
        else:
            result = {}
    else:
        result = {}
    return flask.jsonify(result)


@application.errorhandler(code_or_exception=404)
def page_not_found(error):
    return flask.jsonify({})


def receive_telemetry(master, timeout, drop, white, black):
    global telemetry_data, message_enumeration

    if timeout == 0:
        timeout = None

    if drop == 0:
        drop = None

    white_list = [] if white == "" else white.split(",")
    black_list = [] if black == "" else black.split(",")

    while True:

        vehicle = utility.mavlink_connection(device=master)

        while True:

            message_raw = vehicle.recv_match(blocking=True, timeout=timeout)

            if not message_raw:
                break

            message_dict = message_raw.to_dict()
            message_name = message_dict.pop("mavpackettype")

            if message_name in black_list:
                continue

            if len(white_list) > 0 and message_name not in white_list:
                continue

            if message_name not in telemetry_data.keys():
                telemetry_data[message_name] = {}

            telemetry_data[message_name] = {**telemetry_data[message_name], **message_dict}
            message_id = message_raw.get_msgId()
            message_enumeration[message_name] = message_id
            time_monotonic = time.monotonic()
            time_now = time.time()

            if "statistics" not in telemetry_data[message_name].keys():
                telemetry_data[message_name]["statistics"] = {}
                telemetry_data[message_name]["statistics"]["counter"] = 1
                telemetry_data[message_name]["statistics"]["latency"] = 0
                telemetry_data[message_name]["statistics"]["first"] = time_now
                telemetry_data[message_name]["statistics"]["first_monotonic"] = time_monotonic
                telemetry_data[message_name]["statistics"]["last"] = time_now
                telemetry_data[message_name]["statistics"]["last_monotonic"] = time_monotonic
                telemetry_data[message_name]["statistics"]["duration"] = 0
                telemetry_data[message_name]["statistics"]["instant_frequency"] = 0
                telemetry_data[message_name]["statistics"]["average_frequency"] = 0
            else:
                telemetry_data[message_name]["statistics"]["counter"] += 1
                telemetry_data[message_name]["statistics"]["latency"] = time_monotonic - telemetry_data[message_name]["statistics"]["last_monotonic"]
                telemetry_data[message_name]["statistics"]["last"] = time_now
                telemetry_data[message_name]["statistics"]["last_monotonic"] = time_monotonic
                telemetry_data[message_name]["statistics"]["duration"] = telemetry_data[message_name]["statistics"]["last_monotonic"] - telemetry_data[message_name]["statistics"]["first_monotonic"]
                telemetry_data[message_name]["statistics"]["instant_frequency"] = 1.0 / telemetry_data[message_name]["statistics"]["latency"]
                telemetry_data[message_name]["statistics"]["average_frequency"] = telemetry_data[message_name]["statistics"]["counter"] / telemetry_data[message_name]["statistics"]["duration"]

            if drop:
                for message_name in list(telemetry_data.keys()):
                    if telemetry_data[message_name]["statistics"]["latency"] > drop:
                        telemetry_data.pop(message_name)


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
def main(host, port, master, timeout, drop, white, black):
    threading.Thread(target=receive_telemetry, args=(master, timeout, drop, white, black)).start()
    server = gevent.pywsgi.WSGIServer(listener=(host, port), application=application, log=application.logger)
    server.serve_forever()


if __name__ == "__main__":
    main()
