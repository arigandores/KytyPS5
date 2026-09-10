"""Standalone tests for the startup-catalogue exporter: python tests/shaderSeedTests.py."""
import contextlib
import io
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from shader_seed import export_seed


class SeedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.cache = root / "cache" / "GAME123"
        self.cache.mkdir(parents=True)
        self.output = root / "seed" / "GAME123"
        self.log = root / "run.log"
        signature = b"KytySC3:test\n1:1:4:1:1:1"
        self.key = struct.pack("<IQIII", 3, 123, 4, 128, 0)
        recipe = b"\x02" + self.key + struct.pack("<I", 0) + bytes(4)
        self.recipes = b"KytyPR1\n" + struct.pack("<I", len(signature)) + signature + struct.pack("<I", 1) + recipe
        (self.cache / "pipelines.bin").write_bytes(self.recipes)
        (self.cache / "cs_test.bin").write_bytes(b"KytySC3:test\n" + bytes(8) + self.key)
        (self.cache / "cs_stale.bin").write_bytes(b"KytySC3:old\n" + bytes(8) + self.key)
        self.log.write_text("ShaderSeed: compatibility=KytySeed1:GAME123:1.0:KytySC3:test::1:1:4:1:1:1:gpu:device\n")

    def export(self):
        with contextlib.redirect_stdout(io.StringIO()):
            export_seed(self.cache, self.log, self.output)

    def test_exports_compatible_set_only(self):
        self.export()
        self.assertTrue((self.output / "cs_test.bin").is_file())
        self.assertFalse((self.output / "cs_stale.bin").exists())
        self.assertEqual((self.output / "pipelines.bin").read_bytes(), self.recipes)

    def test_missing_source_is_rejected_before_output(self):
        (self.cache / "cs_test.bin").unlink()
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.output.exists())

    def test_truncated_recipe_is_rejected(self):
        (self.cache / "pipelines.bin").write_bytes(self.recipes[:-1])
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.output.exists())

    def test_incompatible_log_is_rejected(self):
        self.log.write_text("ShaderSeed: compatibility=another build\n")
        with self.assertRaises(ValueError): self.export()
        self.assertFalse(self.output.exists())

    def test_existing_catalogue_is_preserved(self):
        self.export()
        with self.assertRaises(FileExistsError): self.export()
        self.assertEqual((self.output / "pipelines.bin").read_bytes(), self.recipes)


if __name__ == "__main__":
    unittest.main()
