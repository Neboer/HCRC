import sqlite3
from database import get_user, generate_triple_invitation_code

conn = sqlite3.connect("HCRC.sqlite")
c = conn.cursor()
# a = _query_invitation_code(c, "1255d5s6d", '1')
# print(a)
a = generate_triple_invitation_code(c)
print(a)