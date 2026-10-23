"""Local phase-order checks. No SSH or remote publication occurs."""
import os
import platform
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for name in ('deploy-releases', 'generate-overview'):
            shutil.copy2(ROOT / name, self.root / name)
        (self.root / 'releases').mkdir()
        (self.root / 'releases/FP6-stable').write_text('fixture\n')
        self.bin = self.root / 'bin'; self.bin.mkdir()
        for name, body in (
            ('brotli', 'touch "$1.br"'),
            ('zopfli', 'touch "$1.gz"'),
            ('rsync', 'exit 0'),
        ):
            path = self.bin / name
            path.write_text('#!/bin/sh\n' + body + '\n'); path.chmod(0o755)
        self.transport = self.root / 'transport'
        self.transport.write_text('#!/bin/sh\nprintf "%s\\n" "$1" >> "$TEST_OPERATIONS"\n'
                                  '[ "$1" != release-payloads ] || [ "${FAIL_PAYLOAD:-0}" = 0 ]\n')
        self.transport.chmod(0o700)
        self.env = dict(os.environ, PATH=str(self.bin) + ':/usr/bin:/bin',
                        DIAMANEOS_PUBLICATION_TRANSPORT=str(self.transport), TEST_OPERATIONS=str(self.root / 'operations'))

    @unittest.skipUnless(platform.system() == 'Linux', 'publication uses GNU flock and Bash on Linux')
    def test_all_payloads_precede_selectors(self):
        result = subprocess.run(['bash', str(self.root / 'deploy-releases')], cwd=self.root,
                                env=self.env, capture_output=True, text=True, timeout=10)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(['release-payloads', 'release-selectors'], (self.root / 'operations').read_text().splitlines())

    @unittest.skipUnless(platform.system() == 'Linux', 'publication uses GNU flock and Bash on Linux')
    def test_payload_failure_never_publishes_selectors(self):
        result = subprocess.run(['bash', str(self.root / 'deploy-releases')], cwd=self.root,
                                env=dict(self.env, FAIL_PAYLOAD='1'), capture_output=True, timeout=10)
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(['release-payloads'], (self.root / 'operations').read_text().splitlines())

    def test_overview_is_canonical(self):
        (self.root / 'releases/FP6-alpha').write_text('2 1792691126 FP6 alpha\n')
        result = subprocess.run(['python3', str(self.root / 'generate-overview')], cwd=self.root,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(b'{"FP6":{"alpha":"2","stable":"fixture"}}\n', (self.root / 'overview.json').read_bytes())

    def test_missing_selectors_do_not_produce_empty_overview(self):
        (self.root / 'releases/FP6-stable').unlink()
        result = subprocess.run(['python3', str(self.root / 'generate-overview')], cwd=self.root,
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(0, result.returncode)
        self.assertIn('no channel selector found', result.stderr)
        self.assertFalse((self.root / 'overview.json').exists())


if __name__ == '__main__':
    unittest.main()
