"""Input validation and timing interpretation for the shader inventory tool."""

import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location(
    "shader_inventory", Path(__file__).resolve().parents[1] / "tools" / "shader_inventory.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def fixture():
    data = bytearray(1024)
    data[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<Q", data, 32, 64)
    struct.pack_into("<HH", data, 54, 56, 1)
    struct.pack_into("<IIQQQQQQ", data, 64, 1, 4, 256, 4096, 0, 512, 512, 256)
    offset = 320
    data[offset:offset + 8] = inventory.MAGIC
    struct.pack_into("<q", data, offset + 32, 96 - 32)
    struct.pack_into("<IIIIIHHHBBB", data, offset + 64, 112, 128, 0, 0, 0, 0, 0, 0, 0, 0, 1)
    struct.pack_into("<II", data, offset + 96, 0x213, 32)
    return data, offset


class InventoryTests(unittest.TestCase):
    def test_segment_mapping_and_registers(self):
        data, offset = fixture()
        # A matching byte pattern outside a load segment is not an AGC candidate.
        data[800:808] = inventory.MAGIC
        result = inventory.scan_headers(data)
        self.assertEqual(result["header_candidates"], 1)
        self.assertEqual(result["headers"][0]["elf_vaddr"], 4096 + offset - 256)
        self.assertEqual(result["headers"][0]["sh_registers"], [[0x213, 32]])

    def test_reject_out_of_segment_relative_pointer(self):
        for delta in (-1000, 1000, 0):
            with self.subTest(delta=delta):
                data, offset = fixture()
                struct.pack_into("<q", data, offset + 32, delta)
                self.assertEqual(inventory.scan_headers(data)["header_candidates"], 0)

    def test_reject_wrong_container_and_truncation(self):
        with self.assertRaises(ValueError):
            inventory.scan_headers(b"SELF" + bytes(100))
        data, _ = fixture()
        with self.assertRaises(ValueError):
            inventory.scan_headers(data[:400])

    def test_out_of_order_timestamps_missing_and_late_registration(self):
        lines = [
            "ShaderRegister: hash=aa type=0 size=128 host_us=3000000",
            "ShaderFirstUse: hash=aa stage=4 words=32 ud=16 host_us=8000000",
            "ShaderRegister: hash=aa type=0 size=128 host_us=1000000",
            "ShaderFirstUse: hash=aa stage=4 words=32 ud=16 host_us=9000000",
            "ShaderFirstUse: hash=bb stage=5 words=32 ud=16 host_us=7000000",
            "ShaderFirstUse: hash=cc stage=2 words=32 ud=16 host_us=1000000",
            "ShaderRegister: hash=cc type=1 size=128 host_us=2000000",
        ]
        result = inventory.analyze_log(lines)
        self.assertEqual(result["registration_events"], 3)
        self.assertEqual(result["registered_hashes"], 2)
        self.assertEqual(result["stages"]["compute"]["median_seconds"], 7)
        self.assertEqual(result["stages"]["compute"]["first_use_hashes"], 1)
        self.assertEqual(result["stages"]["mesh"]["matched"], 0)
        self.assertEqual(result["stages"]["pixel"]["registered_before_use"], 0)
        self.assertEqual(result["stages"]["pixel"]["min_seconds"], -1)


if __name__ == "__main__":
    unittest.main()
