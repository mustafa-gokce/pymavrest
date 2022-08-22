import unittest
import requests

IP = "127.0.0.1"
PORT = 2609


class EndpointsReachableTest(unittest.TestCase):
    def test_root(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get"
        data = requests.get(url=link).json()
        self.assertEqual(data, {})

    def test_get_message_all(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/message/all"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_message_with_name(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/message/HEARTBEAT"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_message_with_id(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/message/0"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_message_field_with_name(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/message/HEARTBEAT/autopilot"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_message_field_with_id(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/message/0/autopilot"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_parameter_all(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/parameter/all"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_parameter_with_name(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/parameter/SYSID_THISMAV"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_plan_all(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/plan/all"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_plan_with_index(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/plan/0"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_fence_all(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/fence/all"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_fence_with_index(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/fence/0"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_rally_all(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/rally/all"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_get_rally_with_index(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/rally/0"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_post_command_long(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/command_long"
        data = requests.post(url=link,
                             json={"target_system": 0,
                                   "target_component": 0,
                                   "command": 400,
                                   "confirmation": 0,
                                   "param1": 1,
                                   "param2": 0,
                                   "param3": 0,
                                   "param4": 0,
                                   "param5": 0,
                                   "param6": 0,
                                   "param7": 0
                                   }).json()
        self.assertNotEqual(data, {})

    def test_post_command_int(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/command_int"
        data = requests.post(url=link,
                             json={"target_system": 0,
                                   "target_component": 0,
                                   "frame": 6,
                                   "command": 192,
                                   "current": 0,
                                   "autocontinue": 0,
                                   "param1": 0,
                                   "param2": 0,
                                   "param3": 0,
                                   "param4": 0,
                                   "x": -353613322,
                                   "y": 1491611469,
                                   "z": 10
                                   }).json()
        self.assertNotEqual(data, {})

    def test_post_param_set(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/param_set"
        data = requests.post(url=link,
                             json={"target_system": 0,
                                   "target_component": 0,
                                   "param_id": "SYSID_THISMAV",
                                   "param_value": 26,
                                   "param_type": 9
                                   }).json()
        self.assertNotEqual(data, {})

    def test_post_plan(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/plan"
        data = requests.post(url=link,
                             json=[
                                 {
                                     "target_system": 0,
                                     "target_component": 0,
                                     "seq": 1,
                                     "frame": 0,
                                     "command": 16,
                                     "current": 0,
                                     "autocontinue": 0,
                                     "param1": 0,
                                     "param2": 0,
                                     "param3": 0,
                                     "param4": 0,
                                     "x": -353606091,
                                     "y": 1491650274,
                                     "z": 784.5,
                                     "mission_type": 0
                                 }
                             ]).json()
        self.assertNotEqual(data, {})


if __name__ == "__main__":
    unittest.main()
