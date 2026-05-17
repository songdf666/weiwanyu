from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from euphemism_repro.preprocess.pipeline import PreprocessConfig, preprocess_document
from euphemism_repro.preprocess.schema import RawDocument


class PreprocessTests(unittest.TestCase):
    def test_preprocess_document_extracts_period_and_tokens(self):
        config = PreprocessConfig(input_globs=["**/*.txt"], lowercase=True)
        raw = RawDocument(
            doc_id=None,
            source_path="corpus/1990/sample.txt",
            text="Hello   WORLD https://example.com",
        )

        processed = preprocess_document(raw, config)

        self.assertIsNotNone(processed)
        self.assertEqual(processed.period, "1990")
        self.assertEqual(processed.text, "hello world")
        self.assertEqual(processed.tokens, ["hello", "world"])


if __name__ == "__main__":
    unittest.main()
