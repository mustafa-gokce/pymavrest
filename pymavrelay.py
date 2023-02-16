#!/usr/bin/python

import gevent.monkey

# patch the modules for asynchronous work
gevent.monkey.patch_all()

import click
import gevent.pywsgi
import flask
import flask_cors
import requests
import threading
import time

# set the default socket options
requests.packages.urllib3.connection.HTTPConnection.default_socket_options = [(6, 3, 1)]
requests.packages.urllib3.connection.HTTPConnection.socket_options = [(6, 3, 1)]

# create a flask application
application = flask.Flask(import_name="pymavrelay")

# enable CORS
flask_cors.CORS(app=application)

# global variables to store server state
all_data = {}
input_host = ""
input_port = 0
output_host = ""
output_port = 0
frequency = 1
timeout = 4


# get all data
@application.route(rule="/get/all", methods=["GET"])
def get_all():
    global all_data
    return flask.jsonify(all_data)


# get version data
@application.route(rule="/get/version", methods=["GET"])
def get_version():
    global all_data
    return flask.jsonify(all_data.get("version", {}))


# get time data
@application.route(rule="/get/statistics", methods=["GET"])
def get_statistics():
    global all_data
    return flask.jsonify(all_data.get("statistics", {}))


# get all messages
@application.route(rule="/get/message/all", methods=["GET"])
def get_message_all():
    global all_data
    return flask.jsonify(all_data.get("message", {}))


# get a message by name
@application.route(rule="/get/message/<string:message_name>", methods=["GET"])
def get_message_with_name(message_name):
    global all_data
    return flask.jsonify({message_name: all_data.get("message", {}).get(message_name, {})})


# get a field of a message with message name
@application.route(rule="/get/message/<string:message_name>/<string:field_name>", methods=["GET"])
def get_message_field_with_name(message_name, field_name):
    global all_data
    return flask.jsonify({field_name: all_data.get("message", {}).get(message_name, {}).get(field_name, {})})


# get all parameters
@application.route(rule="/get/parameter/all", methods=["GET"])
def get_parameter_all():
    global all_data
    return flask.jsonify(all_data.get("parameter", {}))


# get a parameter by name
@application.route(rule="/get/parameter/<string:parameter_name>", methods=["GET"])
def get_parameter_with_name(parameter_name):
    global all_data
    return flask.jsonify({parameter_name: all_data.get("parameter", {}).get(parameter_name, {})})


# get all flight plan
@application.route(rule="/get/plan/all", methods=["GET"])
def get_plan_all():
    global all_data
    return flask.jsonify(all_data.get("plan", {}))


# get a flight plan command by index
@application.route(rule="/get/plan/<int:plan_index>", methods=["GET"])
def get_plan_with_index(plan_index):
    global all_data
    plan_data = all_data.get("plan", [])
    if 0 <= plan_index < len(plan_data):
        item_data = plan_data[plan_index]
    else:
        item_data = {}
    return flask.jsonify(item_data)


# get all fence
@application.route(rule="/get/fence/all", methods=["GET"])
def get_fence_all():
    global all_data
    return flask.jsonify(all_data.get("fence", {}))


# get a fence item by index
@application.route(rule="/get/fence/<int:fence_index>", methods=["GET"])
def get_fence_with_index(fence_index):
    global all_data
    fence_data = all_data.get("fence", [])
    if 0 <= fence_index < len(fence_data):
        item_data = fence_data[fence_index]
    else:
        item_data = {}
    return flask.jsonify(item_data)


# get all rally
@application.route(rule="/get/rally/all", methods=["GET"])
def get_rally_all():
    global all_data
    return flask.jsonify(all_data.get("rally", {}))


# get a rally item by index
@application.route(rule="/get/rally/<int:rally_index>", methods=["GET"])
def get_rally_with_index(rally_index):
    global all_data
    rally_data = all_data.get("rally", [])
    if 0 <= rally_index < len(rally_data):
        item_data = rally_data[rally_index]
    else:
        item_data = {}
    return flask.jsonify(item_data)


# get all custom data
@application.route(rule="/get/custom/all", methods=["GET"])
def get_custom_all():
    global all_data
    return flask.jsonify(all_data.get("custom", {}))


# get a key value pair with key
@application.route(rule="/get/custom/<string:key>", methods=["GET"])
def get_key_value_pair_with_key(key):
    global all_data
    return flask.jsonify({key: all_data.get("custom", {}).get(key, {})})


# post all data
@application.route(rule="/<path:endpoint>", methods=["POST"])
def post_all(endpoint):
    global input_host, input_port, timeout
    payload = flask.request.json
    result = {}
    try:
        result = requests.post(url=f"http://{input_host}:{input_port}/{endpoint}", json=payload, timeout=timeout).json()
    except Exception as e:
        pass
    return flask.jsonify(result)


# deal with the malicious requests
@application.errorhandler(code_or_exception=404)
def page_not_found(error):
    return flask.jsonify({})


# receive from remote API
def receive():
    global all_data, input_host, input_port, frequency, timeout
    while True:
        try:
            all_data = requests.get(url=f"http://{input_host}:{input_port}/get/all", timeout=timeout).json()
        except Exception as e:
            pass
        time.sleep(1.0 / frequency)


@click.command()
@click.option("--host_in", type=click.STRING, required=True, help="Input IP address.")
@click.option("--port_in", type=click.IntRange(min=0, max=65535), required=True, help="Input port number.")
@click.option("--host_out", type=click.STRING, required=True, help="Output IP address.")
@click.option("--port_out", type=click.IntRange(min=0, max=65535), required=True, help="Output port number.")
@click.option("--freq", default=1, type=click.IntRange(min=0, clamp=True), required=False, help="Fetch frequency.")
@click.option("--wait", default=4, type=click.IntRange(min=0, clamp=True), required=False, help="Wait for API.")
def main(host_in, port_in, host_out, port_out, freq, wait):

    # configure the flask application
    global input_host, input_port, output_host, output_port, frequency, timeout
    input_host = host_in
    input_port = port_in
    output_host = host_out
    output_port = port_out
    frequency = freq
    timeout = wait

    # start telemetry receiver thread
    threading.Thread(target=receive).start()

    # create server
    server = gevent.pywsgi.WSGIServer(listener=(host_out, port_out), application=application, log=application.logger)

    # run server
    server.serve_forever()


# main entry point
if __name__ == "__main__":
    # run main function
    main()
