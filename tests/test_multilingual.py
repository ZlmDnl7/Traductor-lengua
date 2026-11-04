# test_multilingual.py
# Pruebas automatizadas de la configuracion multilingue (LSC / ASL / LIBRAS).
# No requieren camara, microfono ni MongoDB.
#
#   python -m unittest tests.test_multilingual -v

import os
import re
import string
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.languages import (  # noqa: E402
    LANGUAGE_PROFILES,
    MESSAGES,
    MODULE_CHALLENGE,
    build_ai_context,
    get_profile,
    get_sign_alphabet,
    language_pack,
    t,
)
from src.sign_language.performance_analyzer import LearningPerformanceAnalyzer  # noqa: E402
from src.sign_language.review_ai import ReviewAI  # noqa: E402
from src.sign_language.sign_classifier import SignClassifier  # noqa: E402
from src.sign_language.text_utils import letters_for_challenge, spell_text  # noqa: E402

WEB_DIR = os.path.join(ROOT, "src", "gui_web", "web")
LANGS = ("es", "en", "pt")


def finger_state(thumb, index, middle, ring, pinky, **extra):
    data = {"thumb": thumb, "index": index, "middle": middle, "ring": ring, "pinky": pinky}
    data.update(extra)
    return data


class ProfileTests(unittest.TestCase):
    def test_speech_codes(self):
        self.assertEqual(get_profile("es").speech_locale, "es-CO")
        self.assertEqual(get_profile("en").speech_locale, "en-US")
        self.assertEqual(get_profile("pt").speech_locale, "pt-BR")
        self.assertEqual([get_profile(l).whisper_language for l in LANGS], ["es", "en", "pt"])

    def test_sign_languages(self):
        self.assertEqual([get_profile(l).sign_language for l in LANGS], ["LSC", "ASL", "LIBRAS"])

    def test_unknown_language_falls_back_to_default(self):
        self.assertEqual(get_profile("xx").code, "es")
        self.assertEqual(get_profile(None).code, "es")

    def test_model_and_data_files_are_separate_and_exist(self):
        paths = set()
        for lang in LANGS:
            profile = get_profile(lang)
            self.assertTrue(os.path.isfile(profile.samples_csv), profile.samples_csv)
            self.assertTrue(os.path.isfile(profile.model_path), profile.model_path)
            paths.add(profile.model_path)
        self.assertEqual(len(paths), 3)

    def test_every_learning_letter_has_an_image_in_its_own_folder(self):
        for lang in LANGS:
            profile = get_profile(lang)
            folder = os.path.normpath(os.path.join(WEB_DIR, profile.image_folder))
            for letter in profile.learning_alphabet:
                path = os.path.join(folder, letter.lower() + ".png")
                self.assertTrue(os.path.isfile(path), f"{lang}: {path}")

    def test_alphabets(self):
        self.assertIn("Ñ", get_profile("es").learning_alphabet)
        self.assertNotIn("Ñ", get_profile("en").learning_alphabet)
        self.assertNotIn("Ç", get_profile("en").learning_alphabet)
        self.assertIn("Ç", get_profile("pt").learning_alphabet)
        self.assertEqual(len(get_profile("en").learning_alphabet), 26)

    def test_language_pack_contains_descriptions(self):
        for lang in LANGS:
            pack = language_pack(lang)
            self.assertEqual(set(pack["sign_descriptions"]), set(pack["learning_alphabet"]))
            self.assertEqual(pack["speech_locale"], get_profile(lang).speech_locale)


class SignDescriptionTests(unittest.TestCase):
    def test_full_coverage(self):
        for lang in LANGS:
            rules = get_sign_alphabet(lang)
            for letter in get_profile(lang).learning_alphabet:
                self.assertTrue(rules.describe(letter), f"{lang} {letter}")

    def test_descriptions_are_not_reused_between_alphabets(self):
        es, en, pt = (get_sign_alphabet(l).descriptions for l in LANGS)
        for letter in en:
            self.assertNotEqual(es.get(letter), en[letter])
            self.assertNotEqual(pt.get(letter), en[letter])
            self.assertNotEqual(pt.get(letter), es.get(letter))

    def test_configuration_differences_are_reflected(self):
        # LSC: A con el pulgar abierto; U con indice y menique.
        self.assertIn("pulgar hacia el costado", get_sign_alphabet("es").describe("A"))
        self.assertIn("meñique", get_sign_alphabet("es").describe("U"))
        # ASL: U con indice y medio juntos.
        self.assertIn("index and middle fingers together", get_sign_alphabet("en").describe("U"))
        # LIBRAS: M y Q apuntan hacia abajo.
        self.assertIn("para baixo", get_sign_alphabet("pt").describe("M"))
        self.assertIn("para baixo", get_sign_alphabet("pt").describe("Q"))

    def test_descriptions_are_written_in_the_profile_language(self):
        spanish_markers = re.compile(r"\b(dedos|mano|pulgar|índice)\b")
        english_markers = re.compile(r"\b(finger|fingers|thumb|hand)\b")
        portuguese_markers = re.compile(r"\b(dedos|mão|polegar|indicador)\b")
        for d in get_sign_alphabet("en").descriptions.values():
            self.assertIsNone(spanish_markers.search(d), d)
        for d in get_sign_alphabet("pt").descriptions.values():
            self.assertIsNone(english_markers.search(d), d)
            self.assertNotIn("pulgar", d)
        self.assertTrue(any(portuguese_markers.search(d) for d in get_sign_alphabet("pt").descriptions.values()))


class MessageCatalogTests(unittest.TestCase):
    def test_same_keys_in_all_languages(self):
        keys = set(MESSAGES["es"])
        for lang in LANGS:
            self.assertEqual(set(MESSAGES[lang]), keys, lang)

    def test_same_placeholders(self):
        fmt = string.Formatter()
        for key, template in MESSAGES["es"].items():
            expected = {f for _, f, _, _ in fmt.parse(template) if f}
            for lang in ("en", "pt"):
                got = {f for _, f, _, _ in fmt.parse(MESSAGES[lang][key]) if f}
                self.assertEqual(got, expected, f"{lang}:{key}")

    def test_translation(self):
        self.assertEqual(t("en", "must_login"), "You must log in")
        self.assertEqual(t("pt", "must_login"), "Você precisa entrar")
        self.assertEqual(t("es", "must_login"), "Debes iniciar sesión")
        self.assertEqual(t("en", "username_short", n=3), "The username must have at least 3 characters")


class AIContextTests(unittest.TestCase):
    def test_context_has_all_fields(self):
        ctx = build_ai_context("en", MODULE_CHALLENGE, "k")
        self.assertEqual(ctx.language, "en")
        self.assertEqual(ctx.sign_language, "ASL")
        self.assertEqual(ctx.letter, "K")
        self.assertEqual(ctx.response_language, "en-US")
        self.assertEqual(ctx.module, "challenge")
        self.assertEqual(len(ctx.alphabet), 26)
        self.assertEqual(ctx.instructions, get_sign_alphabet("en").describe("K"))


class ReviewAITests(unittest.TestCase):
    def test_correct_feedback_language(self):
        self.assertIn("Great job", ReviewAI("en").analyze("A", "A", 0.9).message)
        self.assertIn("Muito bem", ReviewAI("pt").analyze("A", "A", 0.9).message)
        self.assertIn("Buen trabajo", ReviewAI("es").analyze("A", "A", 0.9).message)

    def test_feedback_carries_context(self):
        fb = ReviewAI("pt").analyze("B", "A").as_dict()
        self.assertEqual(fb["language"], "pt")
        self.assertEqual(fb["sign_language"], "LIBRAS")
        self.assertEqual(fb["instructions"], get_sign_alphabet("pt").describe("B"))

    def test_u_uses_each_alphabet_rules(self):
        index_middle_up = finger_state(False, True, True, False, False)
        # ASL: la U es indice + medio -> el patron coincide, no hay error de dedos.
        asl = ReviewAI("en").analyze("U", "R", finger_state=index_middle_up)
        self.assertNotEqual(asl.title, "Check your fingers")
        # LSC: la U es indice + menique -> la IA corrige medio y menique.
        lsc = ReviewAI("es").analyze("U", "R", finger_state=index_middle_up)
        self.assertEqual(lsc.title, "Revisa tus dedos")
        self.assertIn("meñique", lsc.message)

    def test_uv_confusion_by_alphabet(self):
        together = finger_state(False, True, True, False, False, two_finger_pose="together_up")
        self.assertIn("too close together", ReviewAI("en").analyze("V", "U", finger_state=together).message)
        self.assertIn("juntos demais", ReviewAI("pt").analyze("V", "U", finger_state=together).message)
        # En LSC la U no es "V con dedos juntos": no se usa esa explicacion.
        lsc = ReviewAI("es").analyze("V", "U", finger_state=together)
        self.assertNotIn("demasiado juntos", lsc.message)
        self.assertFalse(lsc.confusion_pair)

    def test_asl_only_thumb_rules_are_not_applied_to_other_alphabets(self):
        fs = finger_state(False, True, True, True, True, thumb_between=True)
        self.assertIn("thumb is between", ReviewAI("en").analyze("B", "K", finger_state=fs).message)
        self.assertNotIn("pulgar está entre", ReviewAI("es").analyze("B", "K", finger_state=fs).message)

    def test_orientation_rules_by_alphabet(self):
        down = finger_state(False, False, False, False, False, palm_orientation="down")
        # ASL Q y LSC/LIBRAS M apuntan hacia abajo: no se pide girar la palma.
        self.assertNotEqual(ReviewAI("en").analyze("Q", "A", finger_state=down).category, "orientacion")
        self.assertNotEqual(ReviewAI("es").analyze("M", "A", finger_state=down).category, "orientacion")
        self.assertNotEqual(ReviewAI("pt").analyze("M", "A", finger_state=down).category, "orientacion")
        en = ReviewAI("en").analyze("C", "O", finger_state=down)  # C sin regla de orientacion
        self.assertNotEqual(en.category, "orientacion")
        b = ReviewAI("en").analyze("W", "X", finger_state=finger_state(False, True, True, True, False, palm_orientation="down"))
        self.assertEqual(b.category, "orientacion")
        self.assertIn("ASL", b.message)

    def test_generic_feedback_uses_alphabet_instructions(self):
        fb = ReviewAI("pt").analyze("Q", "Z")
        self.assertIn(get_sign_alphabet("pt").describe("Q"), fb.tip)
        fb_en = ReviewAI("en").analyze("Q", "Z")
        self.assertIn(get_sign_alphabet("en").describe("Q"), fb_en.tip)

    def test_analyze_attempts_language(self):
        attempts = [{"target_letter": "L", "detected_letter": "A"} for _ in range(5)]
        fb = ReviewAI("en").analyze_attempts(attempts)
        self.assertIn("attempts_analyzed=5", fb.details)
        self.assertEqual(fb.language, "en")
        self.assertNotRegex(fb.message, r"Formaste|Você")

    def test_no_spanish_in_english_or_portuguese_feedback(self):
        cases = [
            ("V", "U", finger_state(False, True, True, False, False, two_finger_pose="together_up")),
            ("L", "A", finger_state(False, False, False, False, False)),
            ("W", "X", finger_state(False, True, True, True, False, palm_orientation="lateral")),
            ("A", None, None),
            ("A", "A", None),
            ("A", "B", None),
        ]
        spanish = re.compile(r"\b(Tu|Estás|Formaste|dedo|mano|Revisa|Intenta)\b")
        for lang in ("en", "pt"):
            ai = ReviewAI(lang)
            for target, detected, fs in cases:
                fb = ai.analyze(target, detected, finger_state=fs)
                for text in (fb.title, fb.message, fb.tip):
                    self.assertIsNone(spanish.search(text), f"{lang}: {text}")


class PerformanceAnalyzerTests(unittest.TestCase):
    def test_messages_per_language(self):
        stats = {"attempts": 5, "correct": 1, "incorrect": 4}
        self.assertIn("needs more practice", LearningPerformanceAnalyzer("en").analyze(stats, "B").message)
        self.assertIn("precisa de mais prática", LearningPerformanceAnalyzer("pt").analyze(stats, "B").message)
        self.assertIn("necesita más práctica", LearningPerformanceAnalyzer("es").analyze(stats, "B").message)
        self.assertIn("Keep practicing", LearningPerformanceAnalyzer("es").analyze({}, "B", "en").message)


class ChallengeTextTests(unittest.TestCase):
    def test_spanish(self):
        self.assertEqual(letters_for_challenge("María José", "es"), list("MARIAJOSE"))
        self.assertEqual(letters_for_challenge("Ñandú", "es"), list("NANDU"))

    def test_english(self):
        self.assertEqual(letters_for_challenge("Zoë O'Neil", "en"), list("ZOEONEIL"))
        self.assertEqual(letters_for_challenge("François", "en"), list("FRANCOIS"))

    def test_portuguese_keeps_cedilla(self):
        self.assertEqual(letters_for_challenge("Coração", "pt"), ["C", "O", "R", "A", "Ç", "A", "O"])

    def test_unsupported_characters_never_block(self):
        letters, skipped = spell_text("ana_2024 ★!", "en")
        self.assertEqual(letters, list("ANA"))
        self.assertEqual(set(skipped), set("_2024★!"))
        letters, skipped = spell_text("Ç", "pt", allowed=list("ABC"))
        self.assertEqual(letters, [])
        self.assertEqual(skipped, ["Ç"])
        self.assertEqual(spell_text("", "es"), ([], []))
        self.assertEqual(spell_text("12345", "es")[0], [])

    def test_challenge_words_are_fully_spellable(self):
        for lang in LANGS:
            profile = get_profile(lang)
            self.assertGreaterEqual(len(profile.challenge_words), 5)
            for word in profile.challenge_words:
                letters, skipped = spell_text(word, lang, allowed=profile.model_alphabet)
                self.assertEqual(skipped, [], f"{lang} {word}")
                self.assertTrue(set(letters) <= set(profile.model_alphabet))


class ClassifierPerLanguageTests(unittest.TestCase):
    def test_each_language_loads_its_own_trained_model(self):
        for lang in LANGS:
            clf = SignClassifier(language=lang)
            self.assertTrue(clf.is_trained(), lang)
            self.assertEqual(os.path.normcase(clf.model_path), os.path.normcase(get_profile(lang).model_path))
            self.assertTrue(clf.known_letters() <= set(get_profile(lang).model_alphabet) | set("Ç"))


class VoiceConfigTests(unittest.TestCase):
    def _run_transcribe(self, language):
        import numpy as np
        from src.speech import voice_transcriber as vt

        calls = []

        class FakeModel:
            def transcribe(self, audio, **kwargs):
                calls.append(kwargs)
                seg = mock.Mock()
                seg.text = "hello world"
                return [seg], None

        with mock.patch.object(vt, "_model", FakeModel()):
            text = vt.transcribe(np.ones(1600, dtype=np.float32) * 0.1, language)
        return text, calls

    def test_whisper_receives_selected_language(self):
        for lang, code in (("es", "es"), ("en", "en"), ("pt", "pt")):
            _, calls = self._run_transcribe(lang)
            self.assertTrue(calls)
            self.assertTrue(all(c["language"] == code for c in calls), calls)

    def test_spanish_hotwords_and_fixes_only_for_spanish(self):
        text_en, calls_en = self._run_transcribe("en")
        self.assertEqual(text_en, "hello world")  # sin el reemplazo "hello" -> "hola"
        self.assertFalse(any("hotwords" in c for c in calls_en))
        text_es, _ = self._run_transcribe("es")
        self.assertEqual(text_es, "hola world")

    def test_whisper_model_is_multilingual(self):
        from src.config import WHISPER_MODEL_NAME

        self.assertFalse(WHISPER_MODEL_NAME.endswith(".en"))


class TextToSpeechTests(unittest.TestCase):
    VOICES = [("es-ES", "Helena"), ("en-US", "Zira")]

    def test_voice_selection_by_language(self):
        from src.speech.text_to_speech import voice_for

        self.assertEqual(voice_for("es-CO", self.VOICES), "Helena")  # mismo idioma
        self.assertEqual(voice_for("en-US", self.VOICES), "Zira")
        self.assertIsNone(voice_for("pt-BR", self.VOICES))  # nunca una voz de otro idioma

    def test_speak_validates_input(self):
        from src.speech import text_to_speech

        self.assertEqual(text_to_speech.speak("", "en-US")["code"], "empty")
        self.assertEqual(text_to_speech.speak("hi", "en-US'; Remove-Item x")["code"], "invalid_locale")
        with mock.patch.object(text_to_speech, "list_voices", return_value=self.VOICES):
            self.assertEqual(text_to_speech.speak("Olá", "pt-BR")["code"], "no_voice")


class MongoPerLanguageTests(unittest.TestCase):
    """Integracion con MongoDB real en una base de pruebas aparte (se elimina al final).
    Se omite si MongoDB no esta disponible. Nunca toca la base de la aplicacion."""

    TEST_DB = "traductor_senas_test_multilingual"

    def setUp(self):
        try:
            from pymongo import MongoClient

            from src.config import MONGO_URI

            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
            client.server_info()
        except Exception:
            self.skipTest("MongoDB no disponible")
        from src.database import db_manager

        self.client = client
        patcher = mock.patch.object(db_manager, "MONGO_DB_NAME", self.TEST_DB)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(client.close)
        self.addCleanup(lambda: client.drop_database(self.TEST_DB))
        self.db = db_manager.DatabaseManager()
        self.addCleanup(lambda: self.db._client and self.db._client.close())
        self.db.init_database()
        ok, msg = self.db.register_user("tester", "secret1", learning_language="en")
        self.assertTrue(ok)
        self.assertEqual(msg, "Registration successful")

    def test_registration_message_language(self):
        self.assertEqual(self.db.register_user("tester", "secret1", learning_language="pt"), (False, "Esse nome de usuário já existe"))

    def test_favorites_and_stats_are_separated_by_language(self):
        db = self.db
        db.add_favorite_letter("tester", "Ñ", "es")
        db.add_favorite_letter("tester", "V", "en")
        db.add_favorite_letter("tester", "Ç", "pt")
        self.assertEqual(db.get_favorite_letters("tester", "es"), ["Ñ"])
        self.assertEqual(db.get_favorite_letters("tester", "en"), ["V"])
        self.assertEqual(db.get_favorite_letters("tester", "pt"), ["Ç"])
        db.record_learning_attempt("tester", "A", True, "en")
        db.record_learning_attempt("tester", "A", False, "pt")
        self.assertEqual(db.get_learning_performance("tester", "A", "en")["correct"], 1)
        self.assertEqual(db.get_learning_performance("tester", "A", "pt")["incorrect"], 1)
        self.assertEqual(db.get_learning_performance("tester", "A", "es")["attempts"], 0)
        # Espanol conserva los campos originales (datos existentes de LSC).
        doc = self.client[self.TEST_DB]["users"].find_one({"username": "tester"})
        self.assertEqual(doc["favorite_letters"], ["Ñ"])
        self.assertEqual(doc["favorite_letters_en"], ["V"])
        self.assertIn("learning_performance_pt", doc)


class ControllerLanguageSwitchTests(unittest.TestCase):
    """Recorrido de cambio de idioma del controlador con una base de datos en memoria."""

    def setUp(self):
        from src import main as main_module
        from tests.fakes import FakeDB, controller_patches

        self.db = FakeDB()
        patches = controller_patches(self.db)
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.c = main_module.MainController()

    def test_login_error_in_interface_language(self):
        self.assertEqual(self.c.web_login("ana", "bad", "en"), (False, "Incorrect username or password"))
        self.assertEqual(self.c.web_login("ana", "bad", "pt"), (False, "Usuário ou senha incorretos"))

    def test_full_switch_flow(self):
        c = self.c
        self.assertTrue(c.web_login("ana", "secret", "es")[0])
        st = c.get_web_state()
        self.assertEqual((st["learning_language"], st["speech_locale"], st["sign_language"]), ("es", "es-CO", "LSC"))

        # 1-2) Español: Aprendizaje
        res = c.web_learning_attempt("A", "A")
        self.assertIn("Continúa practicando", res["analysis"]["message"])

        # 3) Cambiar a ingles
        res = c.web_set_learning_language("en")
        self.assertTrue(res["ok"])
        self.assertEqual(res["language_pack"]["sign_language"], "ASL")
        self.assertEqual(c._review_ai.language, "en")
        self.assertEqual(c._challenge_ai.language, "en")
        self.assertEqual(c._sign_classifier.language, "en")
        st = c.get_web_state()
        self.assertEqual((st["speech_locale"], st["sign_language"]), ("en-US", "ASL"))

        # 4) Repaso en ASL: IA en ingles con reglas ASL
        c.web_set_favorite_letter("V", True)
        self.assertEqual(c.web_get_favorite_letters()["letters"], ["V"])
        res = c.web_review_attempt("V", "V")
        self.assertEqual(res["feedback"]["language"], "en")
        self.assertEqual(res["feedback"]["sign_language"], "ASL")
        self.assertIn("Great job", res["feedback"]["message"])
        # Una letra que no existe en ASL (Ñ) se rechaza en vez de evaluarse.
        self.assertFalse(c.web_review_attempt("Ñ", "N")["ok"])

        # 5) Voz: se graba/transcribe en ingles
        c._voice_thread = None
        with mock.patch("threading.Thread") as thread:
            c.on_voice_start_capture()
            thread.assert_called_once()
        self.assertEqual(c._voice_language, "en")
        c._voice_recording = False

        # 6) Reto en ingles
        c.on_challenge_start("word")
        self.assertIn(c._challenge_word, get_profile("en").challenge_words)
        self.assertTrue(c._challenge_letters)

        # 7) Cambiar a portugues durante el reto: se reconstruye con LIBRAS
        c.web_set_learning_language("pt")
        self.assertIn(c._challenge_word, get_profile("pt").challenge_words)
        self.assertEqual(c._challenge_ai.language, "pt")
        self.assertEqual(c._sign_classifier.language, "pt")
        # Favoritos separados por idioma: la V de ASL no aparece en LIBRAS.
        self.assertEqual(c.web_get_favorite_letters()["letters"], [])
        self.assertEqual(c._review_attempts, [])

        # 8) Interaccion: mensajes del backend en portugues
        c._camera_error = "camera_open_error"
        self.assertIn("Não foi possível abrir a câmera", c.get_web_state()["camera_error"])
        c._sign_buffer = "OLA"
        c.on_sign_send()
        msg = c.get_web_state()["messages"][-1]
        self.assertEqual((msg["kind"], msg["who"], msg["speech_locale"]), ("signs", "Pessoa (sinais)", "pt-BR"))
        self.assertEqual(c.web_start_evaluation("x")["msg"], "A duração não é válida")

    def test_evaluation_letters_belong_to_active_alphabet(self):
        c = self.c
        c.web_login("ana", "secret", "es")
        for lang in LANGS:
            c.web_set_learning_language(lang)
            letters = {c._random_evaluation_letter() for _ in range(400)}
            self.assertTrue(letters <= set(get_profile(lang).model_alphabet), (lang, letters))
            # LSC: la Ñ no tiene muestras -> nunca se pide.
            self.assertNotIn("Ñ", letters)

    def test_evaluation_target_changes_alphabet_on_switch(self):
        c = self.c
        c.web_login("ana", "secret", "pt")
        c.web_set_learning_language("pt")
        c.web_start_evaluation(30)
        c.web_set_learning_language("en")
        self.assertIn(c._evaluation_target, get_profile("en").model_alphabet)

    def test_challenge_ai_hint_in_active_language(self):
        c = self.c
        c.web_login("ana", "secret", "en")
        c.web_set_learning_language("en")
        c.on_challenge_start("name")  # ANA
        self.assertEqual(c._challenge_letters, list("ANA"))
        for _ in range(c._challenge_feedback_frames):
            c._advance_challenge("B")
        fb = c.get_web_state()["challenge_feedback"]
        self.assertEqual((fb["language"], fb["module"], fb["target_letter"]), ("en", "challenge", "A"))
        # Acertar la letra limpia la pista y avanza.
        for _ in range(c._challenge_hold_frames):
            c._advance_challenge("A")
        self.assertEqual(c._challenge_index, 1)
        self.assertIsNone(c._challenge_feedback)

    def test_challenge_with_only_unsupported_characters_does_not_block(self):
        c = self.c
        c.web_login("123", "secret", "es")
        c.on_challenge_start("name")
        st = c.get_web_state()
        self.assertEqual(st["challenge_letters"], [])
        self.assertEqual(st["challenge_skipped"], list("123"))
        c._advance_challenge("A")  # no debe fallar


if __name__ == "__main__":
    unittest.main()
