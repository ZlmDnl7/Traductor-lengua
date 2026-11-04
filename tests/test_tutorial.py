# test_tutorial.py
# Tutorial de bienvenida: se ofrece solo a usuarios nuevos y deja de ofrecerse al completarlo.

import unittest


class TutorialFlowTests(unittest.TestCase):
    def setUp(self):
        from src import main as main_module
        from tests.fakes import FakeDB, controller_patches

        self.db = FakeDB()
        patches = controller_patches(self.db)
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.c = main_module.MainController()

    def test_new_user_sees_tutorial_once(self):
        # Asi queda un usuario recien registrado (register_user guarda False).
        self.db._user("nuevo")["tutorial_completed"] = False
        self.assertTrue(self.c.web_login("nuevo", "secret", "es")[0])
        self.assertTrue(self.c.get_web_state()["tutorial_pending"])

        self.assertEqual(self.c.web_complete_tutorial(), {"ok": True})
        self.assertFalse(self.c.get_web_state()["tutorial_pending"])

        # En el siguiente inicio de sesion ya no se ofrece.
        self.c.web_logout()
        self.assertTrue(self.c.web_login("nuevo", "secret", "es")[0])
        self.assertFalse(self.c.get_web_state()["tutorial_pending"])

    def test_existing_user_without_field_does_not_see_tutorial(self):
        self.assertTrue(self.c.web_login("antiguo", "secret", "es")[0])
        self.assertFalse(self.c.get_web_state()["tutorial_pending"])

    def test_logged_out_state_has_no_tutorial(self):
        self.assertFalse(self.c.get_web_state()["tutorial_pending"])
        self.assertFalse(self.c.web_complete_tutorial()["ok"])


if __name__ == "__main__":
    unittest.main()
