import unittest
import sys


class TestRuntime(unittest.TestCase):
    def test_check_python_version(self):
        """
            Check system python version greater equal to 3.11
            Ref: https://docs.python.org/3/library/sys.html
        """
        major, minor = sys.version_info.major, sys.version_info.minor
        self.assertGreaterEqual((major, minor), (3, 11), "Python 3.11 + is required")

if __name__ == "__main__":
    unittest.main()
