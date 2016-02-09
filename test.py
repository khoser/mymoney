# coding: utf-8


"""
тест
"""

import PocketClass
from PocketDB import SoapRequests
from time import sleep

pcs = PocketClass.Pockets('MyPythonMoney.db')
pcs.get_settings()
sr = SoapRequests(pcs.settings)
pcs.parsing = True
sr.send_soap_data([], pcs.parse_soap_income, False)
print 'info', pcs.get_info()
k = 0
while pcs.parsing:
    sleep(1)
    k += 1
    print 'info', k, pcs.get_info()
