"""Guards that keep this fork from ever sending an OS update to a calculator."""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import evo_usb  # noqa: E402

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "evo_usb.py")


class OSUpdateRequestRefusedTests(unittest.TestCase):
    def test_update_urls_are_refused(self):
        for pkt_type in ("F", ord("F")):
            for url in (b"hh01/upd/pkg?bundle=1&prodnum=23&version=7.1.0.1", b"hh01/upd/", b"HH01/UPD/pkg"):
                with self.subTest(pkt_type=pkt_type, url=url):
                    with self.assertRaises(evo_usb.OSUpdateRefused):
                        evo_usb.make_packet(0, pkt_type, url)

    def test_ordinary_requests_still_build(self):
        for url in (b"hh01/xfr/var?memtarget=0&policy=1", b"hh01/get/hh01/sys/screen", b"hh01/sys/reboot"):
            with self.subTest(url=url):
                self.assertTrue(evo_usb.make_packet(0, "F", url))

    def test_data_packets_are_not_inspected(self):
        # File contents may legitimately contain these bytes.
        self.assertTrue(evo_usb.make_packet(0, "D", b"hh01/upd/pkg"))

    def test_send_os_function_is_gone(self):
        self.assertFalse(hasattr(evo_usb, "send_os"))


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, timeout=30)

    def test_send_os_flag_is_rejected_as_unknown(self):
        result = self.run_cli("--send-os", "bundle.84b2")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown option", result.stderr)

    def test_usage_does_not_mention_send_os(self):
        result = self.run_cli()
        self.assertNotIn("--send-os", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
