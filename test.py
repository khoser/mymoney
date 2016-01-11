# coding: utf-8


"""
тест
"""


import PocketClass

pcs = PocketClass.Pockets()
pcs.set_pocket("cash","rub",501.6)
pcs.set_pocket("card","rub",3501.6)
print pcs.get_info()
pcs.create_db()
