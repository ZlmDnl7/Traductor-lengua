# test_camera_toggle.py
# Boton de encendido/apagado de la camara: apagarla libera el dispositivo y
# nada la vuelve a encender hasta que el usuario lo pida.

import unittest
from unittest import mock


class CameraToggleTests(unittest.TestCase):
    def setUp(self):
        from src import main as main_module
        from tests.fakes import FakeDB, controller_patches

        self.db = FakeDB()
        patches = controller_patches(self.db)
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.starts = 0

        def fake_start(c):
            self.starts += 1
            c._translation_running = True

        start_patch = mock.patch.object(main_module.MainController, "_start_translation_loop", fake_start)
        start_patch.start()
        self.addCleanup(start_patch.stop)
        self.c = main_module.MainController()

    def test_turn_off_and_on(self):
        self.assertTrue(self.c.web_login("ana", "secret", "es")[0])
        self.assertEqual(self.starts, 1)
        self.assertTrue(self.c.get_web_state()["camera_enabled"])

        self.c._web_frame_b64 = "imagen"
        self.c._web_letter = "A"
        self.assertEqual(self.c.web_set_camera(False), {"ok": True, "camera_enabled": False})
        state = self.c.get_web_state()
        self.assertFalse(state["camera_enabled"])
        self.assertFalse(self.c._translation_running)
        self.assertIsNone(state["frame_jpeg_b64"])
        self.assertIsNone(state["letter"])

        self.assertEqual(self.c.web_set_camera(True), {"ok": True, "camera_enabled": True})
        self.assertEqual(self.starts, 2)
        self.assertTrue(self.c.get_web_state()["camera_enabled"])

    def test_stays_off_until_user_turns_it_on(self):
        self.c.web_login("ana", "secret", "es")
        self.c.web_set_camera(False)
        self.c.web_start_evaluation(30)
        self.c.on_open_interaction()
        self.assertEqual(self.starts, 1)
        self.assertFalse(self.c._translation_running)

    def test_new_session_starts_with_camera_on(self):
        self.c.web_login("ana", "secret", "es")
        self.c.web_set_camera(False)
        self.c.web_logout()
        self.assertFalse(self.c.get_web_state()["camera_enabled"])
        self.c.web_login("ana", "secret", "es")
        self.assertTrue(self.c.get_web_state()["camera_enabled"])
        self.assertEqual(self.starts, 2)

    def test_requires_login(self):
        self.assertFalse(self.c.web_set_camera(True)["ok"])
        self.assertEqual(self.starts, 0)


if __name__ == "__main__":
    unittest.main()
