import unittest

from SMS import *


class SMSTestCase(unittest.TestCase):
    def test_send(self):
        send_code("13940436867", get_code())


if __name__ == '__main__':
    unittest.main()
