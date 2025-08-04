import unittest
from log_parser import LogParser

class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.parser = LogParser()

    def test_valid_log_line(self):
        line = '127.0.0.1 - - [01/Aug/2025:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
        result = self.parser.parse_line(line)
        self.assertIsNotNone(result)
        self.assertEqual(result['ip_address'], '127.0.0.1')
        self.assertEqual(result['method'], 'GET')
        self.assertEqual(result['path'], '/index.html')
        self.assertEqual(result['status_code'], 200)

    def test_malformed_log_line(self):
        bad_line = 'INCOMPLETE LOG ENTRY'
        result = self.parser.parse_line(bad_line)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
