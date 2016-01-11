# coding: utf-8


"""
тест
"""


import PocketClass

pcs = PocketClass.Pockets()
pcs.set_pocket("cash", "rub", 501.6)
pcs.set_pocket("card", "rub", 3501.6)
pcs.in_items = ["zp", "ava", "other"]
pcs.out_items = ["dinner", "product", "xo3pacxoD", "other", "hobby"]
pcs.contacts = ["mother", "father", "brother", "man"]
pcs.set_credit("it was 20.02", "rub", "man", 0)
pcs.set_credit("it was 10.01", "rub", "man", 100)
print pcs.get_info()
pcs.create_db()
