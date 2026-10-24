import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui import i18n

class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.original_language = i18n.language
    def tearDown(self):
        i18n.language = self.original_language
    def test_all_requested_languages_exist(self):
        self.assertEqual(set(i18n.LANGUAGES), {"en","ta","hi","te","kn","ml","mr","bn","gu","pa"})
    def test_missing_key_falls_back_to_key(self):
        i18n.language = lambda: "ta"
        self.assertEqual(i18n.t("unknown_key"), "unknown_key")
    def test_english_fallback_and_formatting(self):
        i18n.language = lambda: "en"
        self.assertEqual(i18n.t("recorded", label="Report"), "Report recorded")
    def test_language_selection_persists_in_session(self):
        fake = types.SimpleNamespace(session_state={})
        previous = sys.modules.get("streamlit"); sys.modules["streamlit"] = fake
        try:
            i18n.set_language("hi"); self.assertEqual(fake.session_state["language"], "hi")
            i18n.set_language("invalid"); self.assertEqual(fake.session_state["language"], "en")
        finally:
            if previous is not None: sys.modules["streamlit"] = previous
            else: del sys.modules["streamlit"]

if __name__ == "__main__": unittest.main()
