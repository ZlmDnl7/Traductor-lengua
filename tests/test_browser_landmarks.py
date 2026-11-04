# test_browser_landmarks.py
# Version web: el navegador detecta la mano y manda solo los 21 puntos. El servidor
# debe reconocer la sena con esos puntos sin volver a buscar la mano en una imagen.

import unittest
from unittest import mock


class _DetectorThatMustNotRun:
    def process(self, frame):
        raise AssertionError("No se debe buscar la mano en el servidor si ya llegaron los puntos")

    def close(self):
        pass


class BrowserLandmarksTests(unittest.TestCase):
    def setUp(self):
        from src import main as main_module
        from tests.fakes import FakeDB, controller_patches

        # controller_patches reemplaza el arranque; aqui se necesita el real.
        real_start = main_module.MainController._start_translation_loop
        patches = controller_patches(FakeDB()) + [
            mock.patch.object(main_module, "WEB_DEPLOYMENT", True),
            mock.patch.object(main_module, "HandDetector", _DetectorThatMustNotRun),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.c = main_module.MainController()
        real_start(self.c)
        self.assertTrue(self.c._translation_running)
        self.addCleanup(self.c._stop_translation_loop)

    def test_points_are_classified_and_returned(self):
        hand = [{"x": 0.3 + 0.01 * i, "y": 0.7 - 0.02 * i, "z": -0.01} for i in range(21)]
        seq = self.c.submit_browser_landmarks(hand)
        result = self.c.wait_browser_hand_points(seq, timeout=2.0)

        self.assertTrue(result["fresh"])
        self.assertEqual(len(result["hand_points"]), 21)
        self.assertAlmostEqual(result["hand_points"][5][0], hand[5]["x"], places=3)

    def test_no_hand_clears_points(self):
        hand = [{"x": 0.5, "y": 0.5 - 0.01 * i, "z": 0.0} for i in range(21)]
        self.c.wait_browser_hand_points(self.c.submit_browser_landmarks(hand), timeout=2.0)
        result = self.c.wait_browser_hand_points(self.c.submit_browser_landmarks(None), timeout=2.0)

        self.assertTrue(result["fresh"])
        self.assertIsNone(result["hand_points"])
        self.assertIsNone(result["letter"])

    def test_server_detector_not_created_for_browser_points(self):
        # ~60 MB por sesion que no hacen falta si el navegador detecta la mano.
        self.assertIsNone(self.c._hand_detector)
        hand = [{"x": 0.5, "y": 0.5 - 0.01 * i, "z": 0.0} for i in range(21)]
        self.c.wait_browser_hand_points(self.c.submit_browser_landmarks(hand), timeout=2.0)
        self.assertIsNone(self.c._hand_detector)

    def test_rejected_when_translation_is_not_running(self):
        self.c._stop_translation_loop()
        self.assertEqual(self.c.submit_browser_landmarks(None), 0)


if __name__ == "__main__":
    unittest.main()
