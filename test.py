# coding: utf-8


"""
тест
"""


import PocketClass

pcs = PocketClass.Pockets('MyPythonMoney.db')
pcs.set_pocket("cash", "rub", 501.6)
pcs.set_pocket("card", "rub", 3501.6)
pcs.set_pocket("foreign", "usd", 0)
pcs.in_items = ["zp", "ava", "other"]
pcs.out_items = ["dinner", "product", "xo3pacxoD", "other", "hobby"]
pcs.contacts = ["mother", "father", "brother", "man"]
pcs.set_credit("it was 20.02", "rub", "man", 0)
pcs.set_credit("it was 10.01", "rub", "man", 100)
print "init: \n" + pcs.get_info()
pcs.create_db()
pcs.fill_from_db()
pcs.action_in("card", "zp", 100, 0, comment = 'test1')
print "in: \n" + pcs.get_info()
pcs.action_out("cash", "dinner", 150, 0, comment = 'today')
print "out: \n" + pcs.get_info()
pcs.action_between("cash", "card", 200, comment = 'top of the day')
print "between: \n" + pcs.get_info()
pcs.action_exchange("cash", "foreign", 150, 3, comment = 'top of the day')
print "exchange: \n" + pcs.get_info()
pcs.fill_from_db()
print "\nafter filling: \n" + pcs.get_info()
pcs.close_db()