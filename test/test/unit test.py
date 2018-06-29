import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)
    def test_time(self):
        self.assertEqual(True, True, msg="test_time")

if __name__ == '__main__':
    unittest.main()
