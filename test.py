# coding: utf-8


"""
тест
"""

import PocketClass
# import os
# import sqlite3
# import base64
# try:
#     # For Python 3.0 and later
#     import urllib as urllib2
# except ImportError:
    # Fall back to Python 2's urllib2
import urllib2 as urllib2
# from httplib2 import Http
# import httplib
# import requests
# from requests.auth import HTTPBasicAuth

import unittest


class testall(unittest.TestCase):

    def test_one_pocket(self):
        # print ('test init one pocket')
        kw = {'Ref_Key': "9747544e-11c8-11e4-589e-0018f3e1b84e",
              'IsFolder': False,
              'Description': "Название",
              'Активность': True,}
        one_pcs = PocketClass.OnePocket('Test', 'руб', 123, **kw)
        self.assertEqual(one_pcs.name, "Test")
        self.assertEqual(one_pcs.kwargs['Description'], "Название")
        self.assertEqual(one_pcs.kwargs['Ref_Key'],
                         "9747544e-11c8-11e4-589e-0018f3e1b84e")
        self.assertEqual(one_pcs.balance, 123)

    def test_one_credit(self):
        # print ('test init one credit')
        kw = {'Ref_Key': "9747544e-11c8-11e4-589e-0018f3e1b84e",
              'IsFolder': False,
              'Description': "Название",
              'Активность': True,}
        one_crd = PocketClass.OneCredit('Test', 'руб', 'My contact', 123, **kw)
        self.assertEqual(one_crd.name, "Test")
        self.assertEqual(one_crd.kwargs['Description'], "Название")
        self.assertEqual(one_crd.kwargs['Ref_Key'],
                         "9747544e-11c8-11e4-589e-0018f3e1b84e")
        self.assertEqual(one_crd.balance, 123)
        self.assertEqual(one_crd.contact, 'My contact')

    def test_pockets_init(self):
        # print ('test init one pocket in pocketclass')
        pcs = PocketClass.Pockets('test_db')
        kw = {'Ref_Key': "9747544e-11c8-11e4-589e-0018f3e1b84e",
              'IsFolder': False,
              'Description': "Название",
              'Активность': True,}
        args = ['Test', 'руб', 123]
        pcs.set_pocket(*args, **kw)
        self.assertEqual(pcs.pockets[0].name, "Test")
        self.assertEqual(pcs.pockets[0].kwargs['Description'], "Название")
        self.assertEqual(pcs.pockets[0].kwargs['Ref_Key'],
                         "9747544e-11c8-11e4-589e-0018f3e1b84e")
        self.assertEqual(pcs.pockets[0].balance, 123)
        pcs._drop_db()

    def test_credits_init(self):
        # print ('test init one credit in pocketclass')
        pcs = PocketClass.Pockets('test_db')
        kw = {'Ref_Key': "9747544e-11c8-11e4-589e-0018f3e1b84e",
              'IsFolder': False,
              'Description': "Название",
              'Активность': True,}
        args = ['Test', 'руб', 'My contact', 123]
        pcs.set_credit(*args, **kw)
        self.assertEqual(pcs.credits[0].name, "Test")
        self.assertEqual(pcs.credits[0].contact, "My contact")
        self.assertEqual(pcs.credits[0].kwargs['Description'], "Название")
        self.assertEqual(pcs.credits[0].kwargs['Ref_Key'],
                         "9747544e-11c8-11e4-589e-0018f3e1b84e")
        self.assertEqual(pcs.credits[0].balance, 123)
        pcs._drop_db()

    def test_drop_pocket(self):
        # print ('test drop pocket')
        pcs = PocketClass.Pockets('test_db')
        args = ['Test', 'руб', 123]
        pcs.set_pocket(*args)
        pcs._drop_pocket('Test')
        self.assertEqual(len(pcs.pockets),0)

    def test_drop_credit(self):
        # print ('test drop credit')
        pcs = PocketClass.Pockets('test_db')
        args = ['Test', 'руб', 'My contact', 123]
        pcs.set_credit(*args)
        pcs._drop_credit('Test')
        self.assertEqual(len(pcs.credits),0)
        
    def test_odata(self):
        print ('test odata')
        pcs = PocketClass.Pockets('MyPythonMoney.db')
        pcs.get_settings()

        ourl = '/odata/standard.odata'
        journ = u'\xd0\x96\xd1\x83\xd1\x80\xd0\xbd\xd0\xb0\xd0\xbb\xd0\x9e\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb9'
        reg_slice = '/AccountingRegister_%s/SliceLast' % journ
        # reg_slice = unicode(reg_slice, 'utf-8')
        URL = pcs.settings['URL']
        # furl = "money.kter.ru"
        # lurl = "/money/odata/standard.odata/"
        full_url = URL + ourl + reg_slice
        authorization = pcs.settings['Authorization']

        headers = {
            'Authorization': authorization
        }
        req = urllib2.Request(full_url, None, headers)
        result = urllib2.urlopen(req)

        data = result.read()

        print(data)
        self.assertEqual(1,1)


if __name__ == '__main__':
    unittest.main()
