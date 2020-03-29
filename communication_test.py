import unittest

from communication import *


class CommunicationCase(unittest.TestCase):
    def test_check_user_from_server(self):
        self.assertTrue(check_user_from_server('wsbz', '2956136'))
        self.assertFalse(check_user_from_server('wsbz', '1234567'))

    def test_add_user_to_server(self):
        self.assertTrue(add_user_to_server('2333', '123456'))

    def test_change_user_password_from_server(self):
        self.assertTrue(change_user_password_from_server('wsbz', '123456', '123456'))

    def test_del_user_from_server(self):
        self.assertTrue(del_user_from_server('2333'))

    def test_get_user_list_from_server(self):
        self.assertTrue(len(get_user_list_from_server()) > 0)

    def test_give_kit(self):
        self.assertTrue(give_kit('wsbz', '萌新'))


if __name__ == '__main__':
    unittest.main()
