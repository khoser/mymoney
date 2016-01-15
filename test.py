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
print "\ninit: \n" + pcs.get_info()
pcs.create_db()
pcs.fill_from_db()
pcs.action_in("card", "zp", 100, 0, 'test1')
print "\nin: \n" + pcs.get_info()
pcs.action_out("cash", "dinner", 150, 0, 'today')
print "\nout: \n" + pcs.get_info()
pcs.action_between("cash", "card", 200, 'top of the day')
print "\nbetween: \n" + pcs.get_info()
pcs.action_exchange("cash", "foreign", 150, 3, 'top of the day')
print "\nexchange: \n" + pcs.get_info()
pcs.action_credit1_in("cash", "it was 20.02", 500, 'top of the day')
print "\nвзяли в кредит: \n" + pcs.get_info()
pcs.action_credit1_out("cash", "it was 20.02", 300, 'top of the day')
print "\nвернули кредит: \n" + pcs.get_info()
pcs.action_credit2_out(pcs.pockets[1], "it was 10.01", 3000, 'top of the day')
print "\nдали в кредит: \n" + pcs.get_info()
pcs.action_credit2_in(pcs.pockets[1], "it was 10.01", 1000, 'top of the day')
print "\nнам вернули кредит: \n" + pcs.get_info()
pcs.fill_from_db()
print "\nafter filling: \n" + pcs.get_info()
pcs.close_db()