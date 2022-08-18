#!/usr/bin/python

import gevent.monkey

# patch the modules for asynchronous work
gevent.monkey.patch_all()

import time
import threading
import click
import pymavlink.mavutil as utility
import pymavlink.dialects.v20.all as dialect
import gevent.pywsgi
import flask
import jsonschema

# create a flask application
application = flask.Flask(import_name="pymavrest")

# global variables
vehicle = None
vehicle_connected = False
message_data = {}
message_enumeration = {}
parameter_data = {}
parameter_count_total = 0
parameter_count = set()
plan_data = []
plan_count_total = 0
plan_count = set()
fence_data = []
fence_count_total = 0
fence_count = set()
rally_data = []
rally_count_total = 0
rally_count = set()
custom_data = {}
send_plan_data = []

# COMMAND_LONG schema for validation
schema_command_long = {
    "type": "object",
    "properties": {
        "target_system": {"type": "integer", "minimum": 0, "maximum": 255},
        "target_component": {"type": "integer", "minimum": 0, "maximum": 255},
        "command": {"type": "integer", "minimum": 0, "maximum": 65535},
        "confirmation": {"type": "integer", "minimum": 0, "maximum": 255},
        "param1": {"type": "number"},
        "param2": {"type": "number"},
        "param3": {"type": "number"},
        "param4": {"type": "number"},
        "param5": {"type": "number"},
        "param6": {"type": "number"},
        "param7": {"type": "number"}
    },
    "required": ["target_system", "target_component", "command", "confirmation",
                 "param1", "param2", "param3", "param4", "param5", "param6", "param7"]
}

# COMMAND_INT schema for validation
schema_command_int = {
    "type": "object",
    "properties": {
        "target_system": {"type": "integer", "minimum": 0, "maximum": 255},
        "target_component": {"type": "integer", "minimum": 0, "maximum": 255},
        "frame": {"type": "integer", "minimum": 0, "maximum": 255},
        "command": {"type": "integer", "minimum": 0, "maximum": 65535},
        "current": {"type": "integer", "minimum": 0, "maximum": 255},
        "autocontinue": {"type": "integer", "minimum": 0, "maximum": 255},
        "param1": {"type": "number"},
        "param2": {"type": "number"},
        "param3": {"type": "number"},
        "param4": {"type": "number"},
        "x": {"type": "integer"},
        "y": {"type": "integer"},
        "z": {"type": "number"}
    },
    "required": ["target_system", "target_component", "frame", "command", "current", "autocontinue",
                 "param1", "param2", "param3", "param4", "x", "y", "z"]
}

# PARAM_SET schema for validation
schema_param_set = {
    "type": "object",
    "properties": {
        "target_system": {"type": "integer", "minimum": 0, "maximum": 255},
        "target_component": {"type": "integer", "minimum": 0, "maximum": 255},
        "param_id": {"type": "string", "minLength": 1, "maxLength": 16},
        "param_value": {"type": "number"},
        "param_type": {"type": "integer", "minimum": 0, "maximum": 255}
    },
    "required": ["target_system", "target_component", "param_id", "param_value", "param_type"]
}

# custom key value pair schema for validation
schema_key_value = {
    "type": "object",
    "properties": {
        "key": {"type": "string"},
        "value": {"type": ["number", "string", "boolean", "null"]}
    },
    "required": ["key", "value"]
}

# plan upload schema for validation
schema_plan = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "target_system": {"type": "integer", "minimum": 0, "maximum": 255},
            "target_component": {"type": "integer", "minimum": 0, "maximum": 255},
            "seq": {"type": "integer", "minimum": 0, "maximum": 65535},
            "frame": {"type": "integer", "minimum": 0, "maximum": 255},
            "command": {"type": "integer", "minimum": 0, "maximum": 65535},
            "current": {"type": "integer", "minimum": 0, "maximum": 255},
            "autocontinue": {"type": "integer", "minimum": 0, "maximum": 255},
            "param1": {"type": "number"},
            "param2": {"type": "number"},
            "param3": {"type": "number"},
            "param4": {"type": "number"},
            "x": {"type": "integer"},
            "y": {"type": "integer"},
            "z": {"type": "number"},
            "mission_type": {"type": "integer", "minimum": 0, "maximum": 255}
        },
        "required": ["target_system", "target_component", "seq", "frame", "command", "current", "autocontinue",
                     "param1", "param2", "param3", "param4", "x", "y", "z", "mission_type"]
    },
    "minItems": 1,
    "maxItems": 65535
}


# get all messages
@application.route(rule="/get/message/all", methods=["GET"])
def get_message_all():
    # get all messages
    global message_data

    # expose the response
    return flask.jsonify(message_data)


# get a message by name
@application.route(rule="/get/message/<string:message_name>", methods=["GET"])
def get_message_with_name(message_name):
    # get all messages
    global message_data

    # check if the message is received
    if message_name in message_data.keys():

        # expose the message
        result = {message_name: message_data[message_name]}

    # message not received yet
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get a message by id
@application.route(rule="/get/message/<int:message_id>", methods=["GET"])
def get_message_with_id(message_id):
    # get all messages and message id numbers
    global message_data, message_enumeration

    # check if the there is a message with requested id
    if message_id in message_enumeration.values():

        # get message name with message id
        message_name = list(message_enumeration.keys())[list(message_enumeration.values()).index(message_id)]

        # check if the message is received
        if message_name in message_data.keys():

            # expose the message
            result = {message_name: message_data[message_name]}

        # message not received yet
        else:

            # create empty response
            result = {}

    # there is no message with requested id
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get a field of a message with message name
@application.route(rule="/get/message/<string:message_name>/<string:field_name>", methods=["GET"])
def get_message_field_with_name(message_name, field_name):
    # get all messages
    global message_data

    # check if the message is received
    if message_name in message_data.keys():

        # check if the message has the requested field name
        if field_name in message_data[message_name].keys():

            # expose the field name and field value
            result = {field_name: message_data[message_name][field_name]}

        # message does not have the requested field name
        else:

            # create empty response
            result = {}

    # message not received yet
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get a field of a message with message id
@application.route(rule="/get/message/<int:message_id>/<string:field_name>", methods=["GET"])
def get_message_field_with_id(message_id, field_name):
    # get all messages and message id numbers
    global message_data, message_enumeration

    # check if the there is a message with requested id
    if message_id in message_enumeration.values():

        # get message name with message id
        message_name = list(message_enumeration.keys())[list(message_enumeration.values()).index(message_id)]

        # check if the message is received
        if message_name in message_data.keys():

            # check if the message has the requested field name
            if field_name in message_data[message_name].keys():

                # expose the field name and field value
                result = {field_name: message_data[message_name][field_name]}

            # message does not have the requested field name
            else:

                # create empty response
                result = {}

        # message not received yet
        else:

            # create empty response
            result = {}

    # there is no message with requested id
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get all parameters
@application.route(rule="/get/parameter/all", methods=["GET"])
def get_parameter_all():
    # get all parameters
    global parameter_data

    # expose the response
    return flask.jsonify(parameter_data)


# get a parameter by name
@application.route(rule="/get/parameter/<string:parameter_name>", methods=["GET"])
def get_parameter_with_name(parameter_name):
    # get all parameters
    global parameter_data

    # check if the parameter is received
    if parameter_name in parameter_data.keys():

        # expose the parameter name and value
        result = {parameter_name: parameter_data[parameter_name]}

    # parameter not received yet
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# get all flight plan
@application.route(rule="/get/plan/all", methods=["GET"])
def get_plan_all():
    # get entire plan
    global plan_data

    # expose the response
    return flask.jsonify(plan_data)


# get a flight plan command by index
@application.route(rule="/get/plan/<int:plan_index>", methods=["GET"])
def get_plan_with_index(plan_index):
    # get entire plan
    global plan_data

    # create empty response
    result = {}

    # find the requested flight plan command by index
    for mission_item in plan_data:
        if mission_item["seq"] == plan_index:
            result = mission_item
            break

    # expose the response
    return flask.jsonify(result)


# get all fence
@application.route(rule="/get/fence/all", methods=["GET"])
def get_fence_all():
    # get entire fence
    global fence_data

    # expose the response
    return flask.jsonify(fence_data)


# get a fence item by index
@application.route(rule="/get/fence/<int:fence_index>", methods=["GET"])
def get_fence_with_index(fence_index):
    # get entire fence
    global fence_data

    # create empty response
    result = {}

    # find the requested fence item by index
    for fence_item in fence_data:
        if fence_item["idx"] == fence_index:
            result = fence_item
            break

    # expose the response
    return flask.jsonify(result)


# get all rally
@application.route(rule="/get/rally/all", methods=["GET"])
def get_rally_all():
    # get entire rally
    global rally_data

    # expose the response
    return flask.jsonify(rally_data)


# get a rally item by index
@application.route(rule="/get/rally/<int:rally_index>", methods=["GET"])
def get_rally_with_index(rally_index):
    # get entire rally
    global rally_data

    # create empty response
    result = {}

    # find the requested rally item by index
    for rally_item in rally_data:
        if rally_item["idx"] == rally_index:
            result = rally_item
            break

    # expose the response
    return flask.jsonify(result)


# get all custom data
@application.route(rule="/get/custom/all", methods=["GET"])
def get_custom_all():
    # get all custom data
    global custom_data

    # expose the response
    return flask.jsonify(custom_data)


# get a key value pair with key
@application.route(rule="/get/custom/<string:key>", methods=["GET"])
def get_key_value_pair_with_key(key):
    # get all custom data
    global custom_data

    # check if the key exists
    if key in custom_data.keys():

        # expose the key value pair
        result = {key: custom_data[key]}

    # key does not exist
    else:

        # create empty response
        result = {}

    # expose the response
    return flask.jsonify(result)


# post command long message to vehicle
@application.route(rule="/post/command_long", methods=["POST"])
def post_command_long():
    # get global variables
    global vehicle, vehicle_connected
    global schema_command_long

    # get the request
    request = flask.request.json

    # create response and add vehicle presence to response
    response = {"command": "COMMAND_LONG", "connected": vehicle_connected, "valid": False, "sent": False}

    # try to validate the request
    try:

        # validate the request
        jsonschema.validate(instance=request, schema=schema_command_long)

        # validation is successful
        response["valid"] = True

    # instance is invalid
    except jsonschema.exceptions.ValidationError:
        pass

    # check vehicle connection and message validation
    if response["connected"] and response["valid"]:
        # send command message to the vehicle
        vehicle.mav.command_long_send(target_system=request["target_system"],
                                      target_component=request["target_component"],
                                      command=request["command"],
                                      confirmation=request["confirmation"],
                                      param1=request["param1"],
                                      param2=request["param2"],
                                      param3=request["param3"],
                                      param4=request["param4"],
                                      param5=request["param5"],
                                      param6=request["param6"],
                                      param7=request["param7"])

        # message sent to vehicle
        response["sent"] = True

    # expose the response
    return flask.jsonify(response)


# post command int message to vehicle
@application.route(rule="/post/command_int", methods=["POST"])
def post_command_int():
    # get global variables
    global vehicle, vehicle_connected
    global schema_command_int

    # get the request
    request = flask.request.json

    # create response and add vehicle presence to response
    response = {"command": "COMMAND_INT", "connected": vehicle_connected, "valid": False, "sent": False}

    # try to validate the request
    try:

        # validate the request
        jsonschema.validate(instance=request, schema=schema_command_int)

        # validation is successful
        response["valid"] = True

    # instance is invalid
    except jsonschema.exceptions.ValidationError:
        pass

    # check vehicle connection and message validation
    if response["connected"] and response["valid"]:
        # send command message to the vehicle
        vehicle.mav.command_int_send(target_system=request["target_system"],
                                     target_component=request["target_component"],
                                     frame=request["frame"],
                                     command=request["command"],
                                     current=request["current"],
                                     autocontinue=request["autocontinue"],
                                     param1=request["param1"],
                                     param2=request["param2"],
                                     param3=request["param3"],
                                     param4=request["param4"],
                                     x=request["x"],
                                     y=request["y"],
                                     z=request["z"])

        # message sent to vehicle
        response["sent"] = True

    # expose the response
    return flask.jsonify(response)


# post parameter set message to vehicle
@application.route(rule="/post/param_set", methods=["POST"])
def post_param_set():
    # get global variables
    global vehicle, vehicle_connected
    global schema_param_set

    # get the request
    request = flask.request.json

    # create response and add vehicle presence to response
    response = {"command": "PARAM_SET", "connected": vehicle_connected, "valid": False, "sent": False}

    # try to validate the request
    try:

        # validate the request
        jsonschema.validate(instance=request, schema=schema_param_set)

        # validation is successful
        response["valid"] = True

    # instance is invalid
    except jsonschema.exceptions.ValidationError:
        pass

    # check vehicle connection and message validation
    if response["connected"] and response["valid"]:
        # send parameter set message to the vehicle
        vehicle.mav.param_set_send(target_system=request["target_system"],
                                   target_component=request["target_component"],
                                   param_id=bytes(request["param_id"].encode("utf8")),
                                   param_value=request["param_value"],
                                   param_type=request["param_type"])

        # message sent to vehicle
        response["sent"] = True

    # expose the response
    return flask.jsonify(response)


# post plan to vehicle
@application.route(rule="/post/plan", methods=["POST"])
def post_plan():
    # get global variables
    global vehicle, vehicle_connected
    global send_plan_data, schema_plan

    # get the request
    request = flask.request.json

    # create response and add vehicle presence to response
    response = {"command": "MISSION_ITEM_INT", "connected": vehicle_connected, "valid": False, "sent": False}

    # try to validate the request
    try:

        # validate the request
        jsonschema.validate(instance=request, schema=schema_plan)

        # validation is successful
        response["valid"] = True

    # instance is invalid
    except jsonschema.exceptions.ValidationError:
        pass

    # check message validation
    if response["valid"]:

        # calculate plan length and valid indexes
        plan_length = len(request)
        valid_indexes = [i + 1 for i in range(plan_length)]

        # get indexes inside the request
        requested_indexes = [mission_item["seq"] for mission_item in request]

        # check indexes and set validation
        for valid_index in valid_indexes:
            if valid_index not in requested_indexes:
                response["valid"] = False
                break

    # check message validation
    if response["valid"]:

        # check below field values are consistent between plan items
        for field in ["target_system", "target_component", "mission_type"]:
            field_values = [item[field] for item in request]
            if len(set(field_values)) != 1:
                response["valid"] = False
                break

    # check message validation
    if response["valid"]:

        # check mission types for each item
        for item in request:
            if item["mission_type"] != dialect.MAV_MISSION_TYPE_MISSION:
                response["valid"] = False
                break

    # check vehicle connection and message validation
    if response["connected"] and response["valid"]:
        # set outgoing plan data
        send_plan_data = request

        # send MISSION_COUNT message
        vehicle.mav.mission_write_partial_list_send(target_system=request[0]["target_system"],
                                                    target_component=request[0]["target_component"],
                                                    start_index=1,
                                                    end_index=len(request),
                                                    mission_type=request[0]["mission_type"])

        # message sent to vehicle
        response["sent"] = True

    # expose the response
    return flask.jsonify(response)


# post key value pair to api
@application.route(rule="/post/custom", methods=["POST"])
def post_key_value_pair():
    # get global variables
    global custom_data
    global schema_key_value

    # get the request
    request = flask.request.json

    # create response
    response = {"command": "CUSTOM_SET", "valid": False, "sent": False}

    # try to validate the request
    try:

        # validate the request
        jsonschema.validate(instance=request, schema=schema_key_value)

        # validation is successful
        response["valid"] = True

    # instance is invalid
    except jsonschema.exceptions.ValidationError:
        pass

    # check key is not equal to string all
    if response["valid"]:
        if request["key"] == "all":
            response["valid"] = False

    # check message validation
    if response["valid"]:
        # create or update key value pair
        custom_data[request["key"]] = request["value"]

        # message sent to api
        response["sent"] = True

    # expose the response
    return flask.jsonify(response)


# deal with the malicious requests
@application.errorhandler(code_or_exception=404)
def page_not_found(error):
    # expose an empty response
    return flask.jsonify({})


# connect to vehicle and parse messages
def receive_telemetry(master, timeout, drop, white, black, param, plan, fence, rally):
    # get global variables
    global vehicle, vehicle_connected
    global message_data, message_enumeration
    global parameter_data, parameter_count_total, parameter_count
    global plan_data, plan_count_total, plan_count
    global fence_data, fence_count_total, fence_count
    global rally_data, rally_count_total, rally_count
    global send_plan_data

    # zero time out means do not time out
    if timeout == 0:
        timeout = None

    # zero drop means do not drop non-periodic messages
    if drop == 0:
        drop = None

    # create white list set used in non-periodic parameter and flight plan related messages
    white_list = {"PARAM_VALUE", "MISSION_COUNT", "MISSION_ITEM_INT", "MISSION_ACK", "MISSION_REQUEST", "FENCE_POINT",
                  "RALLY_POINT"}

    # parse white list based on user requirements
    white_list = white_list if white == "" else white_list | {x for x in white.split(",")}

    # parse black list based on user requirements
    black_list = set() if black == "" else {x for x in black.split(",")}

    # user did not request to populate parameter values
    if not param:
        # add parameter value message to black list
        black_list |= {"PARAM_VALUE"}

    # user did not request to populate flight plan items
    if not plan:
        # add flight plan related messages to black list
        black_list |= {"MISSION_COUNT", "MISSION_ITEM_INT", "MISSION_ACK", "MISSION_REQUEST"}

    # user did not request to populate fence
    if not fence:
        # add fence related messages to black list
        black_list |= {"FENCE_POINT"}

    # user did not request to populate rally
    if not rally:
        # add rally related messages to black list
        black_list |= {"RALLY_POINT"}

    # infinite connection loop
    while True:

        # reset connection flag
        vehicle_connected = False

        # connect to vehicle
        vehicle = utility.mavlink_connection(device=master)

        # user requested to populate parameter list or flight plan
        if param or plan:
            # wait until vehicle connection is assured
            vehicle.wait_heartbeat()

            # set connection flag
            vehicle_connected = True

        # user requested to populate parameter list
        if param:
            # request parameter list from vehicle
            vehicle.mav.param_request_list_send(vehicle.target_system, vehicle.target_component)

        # user requested to populate flight plan
        if plan:
            # request flight plan from vehicle
            vehicle.mav.mission_request_list_send(vehicle.target_system, vehicle.target_component)

        # infinite message parsing loop
        while True:

            # wait a message from vehicle until specified timeout
            message_raw = vehicle.recv_match(blocking=True, timeout=timeout)

            # do not proceed to message parsing if no message received from vehicle within specified time
            if not message_raw:
                # reset connection flag
                vehicle_connected = False

                # close the vehicle
                vehicle.close()

                # break the inner loop
                break

            # set connection flag
            vehicle_connected = True

            # convert raw message to dictionary
            message_dict = message_raw.to_dict()

            # get and pop message name from message dictionary
            message_name = message_dict.pop("mavpackettype")

            # do not proceed if message is in the black list
            if message_name in black_list:
                continue

            # do not proceed if message is not in the white list
            if len(white) > 1 and message_name not in white_list:
                continue

            # get timestamps
            time_monotonic = time.monotonic()
            time_now = time.time()

            # create a message field in message data if this ordinary message not populated before
            if message_name not in message_data.keys():
                message_data[message_name] = {}

            # update message fields with new fetched data
            message_data[message_name] = {**message_data[message_name], **message_dict}

            # get message id of this message
            message_id = message_raw.get_msgId()

            # add message id of this message to message enumeration list
            message_enumeration[message_name] = message_id

            # this message is populated for the first time
            if "statistics" not in message_data[message_name].keys():

                # initiate statistics data for this message
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

            # this message was populated before
            else:

                # update statistics data for this message
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

            # message that request a plan item
            if message_name == "MISSION_REQUEST":

                # check if this message requests a plan item
                if message_dict["mission_type"] == dialect.MAV_MISSION_TYPE_MISSION:

                    # find the plan item
                    for item in send_plan_data:

                        # found the plan item
                        if item["seq"] == message_dict["seq"]:
                            # do not go to next item because found it
                            break

                    # did not find the item
                    else:

                        # skip the message sent routine
                        continue

                    # send MISSION_ITEM_INT message to the vehicle
                    vehicle.mav.mission_item_int_send(target_system=item["target_system"],
                                                      target_component=item["target_component"],
                                                      seq=item["seq"],
                                                      frame=item["frame"],
                                                      command=item["command"],
                                                      current=item["current"],
                                                      autocontinue=item["autocontinue"],
                                                      param1=item["param1"],
                                                      param2=item["param2"],
                                                      param3=item["param3"],
                                                      param4=item["param4"],
                                                      x=item["x"],
                                                      y=item["y"],
                                                      z=item["z"],
                                                      mission_type=item["mission_type"])

                # do not proceed further
                continue

            # message contains a parameter value
            if message_name == "PARAM_VALUE":

                # create a parameter space to parameter data if not exist
                if message_dict["param_id"] not in parameter_data.keys():
                    parameter_data[message_dict["param_id"]] = {}

                # get the parameter value
                parameter_data[message_dict["param_id"]]["value"] = message_dict["param_value"]

                # update total parameter count
                parameter_count_total = message_dict["param_count"]

                # add parameter index to parameter count list to not request this parameter value again
                parameter_count.add(message_dict["param_index"])

                # this parameter is populated for the first time
                if "statistics" not in parameter_data[message_dict["param_id"]].keys():

                    # initiate statistics data for this parameter
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

                # this parameter was populated before
                else:

                    # update statistics data for this parameter
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

                # update fence count
                if message_dict["param_id"] == "FENCE_TOTAL":
                    # clear fence related variables
                    fence_data = []
                    fence_count = set()
                    fence_count_total = int(message_dict["param_value"])

                    # request first fence item from vehicle
                    vehicle.mav.fence_fetch_point_send(vehicle.target_system, vehicle.target_component, 0)

                # update rally count
                elif message_dict["param_id"] == "RALLY_TOTAL":
                    # clear rally related variables
                    rally_data = []
                    rally_count = set()
                    rally_count_total = int(message_dict["param_value"])

                    # request first rally item from vehicle
                    vehicle.mav.rally_fetch_point_send(vehicle.target_system, vehicle.target_component, 0)

                # do not proceed further
                continue

            # there are still unpopulated parameter values so request them
            if param and parameter_count_total != len(parameter_data):
                for i in range(parameter_count_total):
                    if i not in parameter_count:
                        vehicle.mav.param_request_read_send(vehicle.target_system, vehicle.target_component, b"", i)
                        break

            # message means flight plan on the vehicle has changed
            if message_name == "MISSION_ACK":

                # this acknowledgement is for flight plan
                if message_dict["mission_type"] == 0:

                    # mission plan is accepted
                    if message_dict["type"] == 0:

                        # clear flight plan related variables
                        plan_data = []
                        plan_count = set()
                        plan_count_total = 0

                        # request total flight plan command count
                        vehicle.mav.mission_request_list_send(vehicle.target_system, vehicle.target_component)

                    # mission plan is not accepted so resend it
                    else:

                        # send plan data is empty
                        if len(send_plan_data) < 1:
                            # do not proceed further
                            continue

                        # send MISSION_COUNT message
                        vehicle.mav.mission_write_partial_list_send(
                            target_system=send_plan_data[0]["target_system"],
                            target_component=send_plan_data[0]["target_component"],
                            start_index=1,
                            end_index=len(send_plan_data),
                            mission_type=send_plan_data[0]["mission_type"])

                # do not proceed further
                continue

            # message contains total flight plan items on the vehicle
            if message_name == "MISSION_COUNT":

                # check this count is for flight plan
                if message_dict["mission_type"] == 0:
                    # clear flight plan related variables
                    plan_data = []
                    plan_count = set()
                    plan_count_total = message_dict["count"]

                    # request first flight plan command from vehicle
                    vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, 0)

                # do not proceed further
                continue

            # message contains a flight plan item
            if message_name == "MISSION_ITEM_INT":

                # check this flight plan command was not populated before
                if message_dict["seq"] not in plan_count:

                    # initiate statistics data for this flight plan command
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

                    # add flight plan command to plan data
                    plan_data.append(message_dict)

                    # add flight plan command to plan count list to no request this again
                    plan_count.add(message_dict["seq"])

                    # request the next flight plan commands if there are any
                    if message_dict["seq"] < plan_count_total - 1:
                        seq = message_dict["seq"] + 1
                        vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, seq)

                # do not proceed further
                continue

            # there are still unpopulated flight plan commands so request them
            if plan and plan_count_total != len(plan_count):
                for i in range(plan_count_total):
                    if i not in plan_count:
                        vehicle.mav.mission_request_int_send(vehicle.target_system, vehicle.target_component, i)
                        break

            # message contains a fence item
            if message_name == "FENCE_POINT":

                # check this fence item was not populated before
                if message_dict["idx"] not in fence_count:

                    # initiate statistics data for this fence item
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

                    # add fence item to fence data
                    fence_data.append(message_dict)

                    # add fence item to fence count list to no request this again
                    fence_count.add(message_dict["idx"])

                    # request the next fence item if there are any
                    if message_dict["idx"] < fence_count_total - 1:
                        idx = message_dict["idx"] + 1
                        vehicle.mav.fence_fetch_point_send(vehicle.target_system, vehicle.target_component, idx)

                # do not proceed further
                continue

            # there are still unpopulated fence items so request them
            if fence and fence_count_total != len(fence_count):
                for i in range(fence_count_total):
                    if i not in fence_count:
                        vehicle.mav.fence_fetch_point_send(vehicle.target_system, vehicle.target_component, i)
                        break

            # message contains a rally item
            if message_name == "RALLY_POINT":

                # check this rally item was not populated before
                if message_dict["idx"] not in rally_count:

                    # initiate statistics data for this rally item
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

                    # add rally item to rally data
                    rally_data.append(message_dict)

                    # add rally item to rally count list to no request this again
                    rally_count.add(message_dict["idx"])

                    # request the next rally item if there are any
                    if message_dict["idx"] < rally_count_total - 1:
                        idx = message_dict["idx"] + 1
                        vehicle.mav.rally_fetch_point_send(vehicle.target_system, vehicle.target_component, idx)

                # do not proceed further
                continue

            # there are still unpopulated rally items so request them
            if rally and rally_count_total != len(rally_count):
                for i in range(rally_count_total):
                    if i not in rally_count:
                        vehicle.mav.rally_fetch_point_send(vehicle.target_system, vehicle.target_component, i)
                        break

            # drop non-periodic messages if user requested
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
@click.option("--fence", default=True, type=click.BOOL, required=False,
              help="Fetch fence.")
@click.option("--rally", default=True, type=click.BOOL, required=False,
              help="Fetch rally.")
def main(host, port, master, timeout, drop, white, black, param, plan, fence, rally):
    # start telemetry receiver thread
    threading.Thread(target=receive_telemetry, args=(master, timeout, drop, white, black,
                                                     param, plan, fence, rally)).start()

    # create server
    server = gevent.pywsgi.WSGIServer(listener=(host, port), application=application, log=application.logger)

    # run server
    server.serve_forever()


# main entry point
if __name__ == "__main__":
    # run main function
    main()
