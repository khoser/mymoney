# coding: utf-8


"""
тест
"""

import PocketClass
from PocketDB import SoapRequests
from time import sleep
from suds.client import Client
from suds import WebFault
import base64
from multiprocessing import Pool
import binascii

pcs = PocketClass.Pockets('MyPythonMoney.db')
pcs.get_settings()
# sr = SoapRequests(pcs.settings)
pcs.parsing = True
# sr.send_soap_data([], pcs.parse_soap_income, False)

# sr.send_soap_data([], printcallback, False)

xx = []
def print_callback(x):
    print x
    xx.append(x)
    pcs.parsing = False

client = Client(pcs.settings['URL'],
                        username=pcs.settings['Login'],
                        password=base64.standard_b64decode(pcs.settings['Pass'])
                        )
cl = client.service[0]


def remote_f(x):
    return_data = cl.From1c2py(x)
    print x
    print type(return_data), return_data, type(return_data.data), return_data.data


send_names = ['in_items',
              'out_items',
              'contacts',
              'pockets',
              'credits']

p = Pool(processes=2)
# results = p.map_async(remote_f, send_names, callback=print_callback)
for i in send_names:
    results = p.apply_async(remote_f, args=(i,), callback=print_callback)
    results.wait()
# results = p.map(do_remote_action_, send_names)
# to_callback(results)
p.close()
p.join()


print 'info' #, pcs.get_info()
k = 0
while pcs.parsing:
    sleep(1)
    k += 1
    print 'info', k #, pcs.get_info()

