"""Exercise real Windows memory limits with tiny workers, never Pangu."""
import subprocess
import sys
import unittest

from pangu_service.guarded_run import GIB, run_limited


@unittest.skipUnless(sys.platform == 'win32', 'Windows Job Objects only')
class CpuGuardTests(unittest.TestCase):
    def test_verified_limit_denies_large_allocation(self):
        code = '''import sys
assert sys.stdin.buffer.readline() == b"GO\\n"
from pangu_service.guarded_run import require_cpu_guard
require_cpu_guard("cpu")
try:
    allocation = bytearray(128 * 1024 * 1024)
except MemoryError:
    print("memory limit verified", flush=True)
else:
    raise SystemExit("allocation unexpectedly succeeded")
'''
        result = run_limited([sys.executable, '-u', '-c', code],
                             limit_bytes=64 * 1024 * 1024, timeout_seconds=10)
        self.assertEqual(result.reason, 'exited', result.output)
        self.assertEqual(result.returncode, 0, result.output)
        self.assertIn('memory limit verified', result.output)

    def test_timeout_stops_waiting_worker(self):
        code = 'import sys,time; assert sys.stdin.buffer.readline()==b"GO\\n"; time.sleep(30)'
        result = run_limited([sys.executable, '-u', '-c', code],
                             limit_bytes=64 * 1024 * 1024, timeout_seconds=0.5)
        self.assertEqual(result.reason, 'timeout', result.output)
        self.assertNotEqual(result.returncode, 0)

    def test_rejects_above_hard_cap(self):
        with self.assertRaises(ValueError):
            run_limited([], limit_bytes=5 * GIB, timeout_seconds=1)

    def test_compatible_cli(self):
        result = subprocess.run([sys.executable, 'run_cpu_limited.py', '--help'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--max-memory-gb', result.stdout)
        self.assertIn('--model', result.stdout)


if __name__ == '__main__':
    unittest.main()
