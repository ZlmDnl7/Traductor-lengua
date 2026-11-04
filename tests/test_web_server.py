import unittest
from unittest.mock import patch

from pymongo.errors import ServerSelectionTimeoutError

try:
    import web_server
except ModuleNotFoundError as error:
    if error.name != "flask":
        raise
    web_server = None


@unittest.skipIf(web_server is None, "Instala Flask para correr las pruebas de la version web.")
class WebServerTests(unittest.TestCase):
    def setUp(self):
        self.client = web_server.app.test_client()

    def test_health_and_web_ui_are_served(self):
        health = self.client.get("/health")
        page = self.client.get("/")
        bridge = self.client.get("/browser_api.js")

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json(), {"status": "ok"})
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"browser_api.js", page.data)
        self.assertEqual(bridge.status_code, 200)
        page.close()
        bridge.close()

    def test_api_proxy_dispatches_browser_calls(self):
        class FakeAPI:
            def login(self, username, password):
                return {"ok": True, "username": username}

        class FakeController:
            def get_web_api(self):
                return FakeAPI()

        with patch.object(web_server, "_controller", return_value=FakeController()):
            response = self.client.post("/api/login", json=["demo", "password"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True, "username": "demo"})

    def test_api_proxy_rejects_invalid_argument_shape(self):
        response = self.client.post("/api/login", json={"username": "demo"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_api_reports_database_initialization_failure(self):
        with patch.object(web_server, "_controller", side_effect=RuntimeError("database unavailable")):
            response = self.client.post("/api/get_state", json=[])

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "database_unavailable")
        self.assertNotIn("database unavailable", response.get_json()["error"])

    def test_api_reports_database_query_failure(self):
        class FakeAPI:
            def get_state(self):
                raise ServerSelectionTimeoutError("database unavailable")

        class FakeController:
            def get_web_api(self):
                return FakeAPI()

        with patch.object(web_server, "_controller", return_value=FakeController()):
            response = self.client.post("/api/get_state", json=[])

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "database_unavailable")

    def test_hand_model_is_served_for_the_browser(self):
        response = self.client.get("/models/hand_landmarker.task")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 500_000)
        response.close()

    def test_camera_landmarks_are_validated_and_answered(self):
        class FakeController:
            def __init__(self):
                self.received = []

            def submit_browser_landmarks(self, landmarks):
                self.received.append(landmarks)
                return len(self.received)

            def wait_browser_hand_points(self, seq):
                return {"ok": True, "fresh": True, "hand_points": [[0.5, 0.5]], "letter": "A"}

        controller = FakeController()
        hand = [[0.1 * (i % 10), 0.05 * i, -0.01] for i in range(21)]
        with patch.object(web_server, "_controller", return_value=controller):
            ok = self.client.post("/api/camera/landmarks", json={"landmarks": hand})
            no_hand = self.client.post("/api/camera/landmarks", json={"landmarks": None})
            short = self.client.post("/api/camera/landmarks", json={"landmarks": hand[:5]})
            bad = self.client.post("/api/camera/landmarks", json={"landmarks": [["x", 0, 0]] * 21})
            not_finite = self.client.post("/api/camera/landmarks", data='{"landmarks": [[NaN, 0, 0]]}',
                                          content_type="application/json")

        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.get_json()["letter"], "A")
        self.assertEqual(no_hand.status_code, 200)
        self.assertEqual(controller.received[0][3], {"x": hand[3][0], "y": hand[3][1], "z": hand[3][2]})
        self.assertIsNone(controller.received[1])
        self.assertEqual(len(controller.received), 2)
        for response in (short, bad, not_finite):
            self.assertEqual(response.status_code, 400)

    def test_idle_sessions_are_released(self):
        class FakeController:
            def __init__(self):
                self.logged_out = False

            def web_logout(self):
                self.logged_out = True

        idle, active = FakeController(), FakeController()
        limit = web_server.SESSION_IDLE_SECONDS
        with web_server._controllers_lock:
            web_server._controllers.update({"idle": idle, "active": active})
            web_server._last_seen.update({"idle": 0.0, "active": limit})
            web_server._release_idle_sessions(limit + 1)
            remaining = set(web_server._controllers)
            web_server._controllers.pop("active", None)
            web_server._last_seen.pop("active", None)

        self.assertTrue(idle.logged_out)
        self.assertFalse(active.logged_out)
        self.assertNotIn("idle", remaining)
        self.assertIn("active", remaining)


if __name__ == "__main__":
    unittest.main()
