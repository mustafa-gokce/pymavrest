import unittest
import requests
import json

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

    def test_get_statistics(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/get/statistics"
        data = requests.get(url=link).json()
        self.assertNotEqual(data, {})

    def test_post_command_long(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/command_long"
        data = requests.post(url=link, json=json.load(open("../samples/post_command_long.json")))
        self.assertEqual(data.json(), json.load(open("../samples/post_command_long_response.json")))

    def test_post_command_int(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/command_int"
        data = requests.post(url=link, json=json.load(open("../samples/post_command_int.json")))
        self.assertEqual(data.json(), json.load(open("../samples/post_command_int_response.json")))

    def test_post_param_set(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/param_set"
        data = requests.post(url=link, json=json.load(open("../samples/post_param_set.json")))
        self.assertEqual(data.json(), json.load(open("../samples/post_param_set_response.json")))

    def test_post_plan(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/plan"
        data = requests.post(url=link, json=json.load(open("../samples/post_plan.json")))
        self.assertEqual(data.json(), json.load(open("../samples/post_plan_response.json")))

    def test_post_rally(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/rally"
        data = requests.post(url=link, json=json.load(open("../samples/post_rally.json")))
        self.assertEqual(data.json(), json.load(open("../samples/post_rally_response.json")))

    def test_post_fence(self):
        global IP, PORT
        link = f"http://{IP}:{PORT}/post/fence"
        data = requests.post(url=link, json=json.load(open("../samples/post_fence.json")))
        self.assertEqual(data.json(), json.load(open("../samples/post_fence_response.json")))


if __name__ == "__main__":
    unittest.main()
