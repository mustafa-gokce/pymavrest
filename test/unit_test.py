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


if __name__ == '__main__':
    unittest.main()
