import unittest
import sqlite3
from database import *


# a = _query_invitation_code(c, "1255d5s6d", '1')
# print(a)
class CommunicationCase(unittest.TestCase):
    # def test_create_new_user(self):
    #     create_new_user(c, conn, "neboer", "123456", "wsbz", "2eDcf1")

    def test_get_user_from_local(self):
        a = get_user_from_local(c, "nepdfdfoer")
        print(a.name)

    # def test_change_password_from_local_db(self):
    #     change_password_from_local_db(c, conn, "nepoer", "abcd1234")
    #
    # def test_query_invitation_code(self):
    #     query_invitation_code(c, "1d4B2c")


if __name__ == '__main__':
    conn = sqlite3.connect("HCRC.sqlite")
    c = conn.cursor()
    unittest.main()
