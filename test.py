# coding: utf-8


"""
тест
"""

import PocketClass
import PocketDB
# import os
import sqlite3
# import base64
# try:
#     # For Python 3.0 and later
#     import urllib as urllib2
# except ImportError:
    # Fall back to Python 2's urllib2
import urllib2 as urllib2
from urllib2 import quote
# from httplib2 import Http
# import httplib
# import requests
# from requests.auth import HTTPBasicAuth

import unittest


class testall(unittest.TestCase):

    # тестирование PocketDB
    def test_db_init(self):
        pdb = PocketDB.PocketsDB('test_db')
        self.assertFalse(pdb.check_first_start())

        table_names = [u'Pockets',
                       u'Balances',
                       u'CreditBalances',
                       u'OutItems',
                       u'InItems',
                       u'Contacts',
                       u'Credits',
                       u'Settings',
                       u'Actions',
                       u'InAction',
                       u'OutAction',
                       u'BetweenAction',
                       u'ExchangeAction',
                       u'Credit1InAction',
                       u'Credit1OutAction',
                       u'Credit2InAction',
                       u'Credit2OutAction']
        table_names.sort()
        return_value = []
        con = sqlite3.connect(pdb.db_name)
        cur = con.cursor()
        try:
            cur.execute("""SELECT name FROM sqlite_master
                        WHERE type='table' AND name in (%s)
                        """%(', '.join('?' for _ in table_names)), (table_names)
                        )
        except sqlite3.OperationalError:
            pass
        for row in cur:
            return_value.append(row[0])
        con.close()
        return_value.sort()
        self.assertListEqual(table_names, return_value)
        pdb._drops()

    def test_all_actions(self):
        pdb = PocketDB.PocketsDB('test_db')
        pdb.add_action(2,3)
        con = sqlite3.connect(pdb.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM Actions")
        for row in cur:
            self.assertEquals(row[2],2)
            self.assertEquals(row[3],3)
        pocket1 = u'pocket1'
        pocket2 = u'pocket2'
        credit1 = u'for one day'
        contact1 = u'my friend'
        item1 = u'item1'
        item2 = u'item2'
        sum1 = 123.45
        sum2 = 456.78
        amount1 = 1.0
        amount2 = 2.0
        act_data = [[pocket1, item1, sum1, amount1, u'in'],
                    [pocket1, item1, sum1, amount1, u'out'],
                    [pocket1, pocket2, sum1, u'between'],
                    [pocket1, pocket2, sum1, sum2, u'exchange'],
                    [pocket1, credit1, sum1, sum2, u'get'],
                    [pocket1, credit1, sum1, sum2, u'give'],
                    [pocket1, credit1, sum1, sum2, amount1, u'give back'],
                    [pocket1, credit1, sum1, sum2, u'get back']
                    ]
        table_names = ['InAction',
                       'OutAction',
                       'BetweenAction',
                       'ExchangeAction',
                       'Credit1InAction',
                       'Credit2InAction',
                       'Credit1OutAction',
                       'Credit2OutAction']
        pdb.action_in(*act_data[0])
        pdb.action_out(*act_data[1])
        pdb.action_between(*act_data[2])
        pdb.action_exchange(*act_data[3])
        pdb.action_credit1_in(*act_data[4])
        pdb.action_credit2_in(*act_data[5])
        pdb.action_credit1_out(*act_data[6])
        pdb.action_credit2_out(*act_data[7])
        for i in range(8):
            cur.execute("SELECT * FROM %s" % table_names[i])
            for row in cur:
                self.assertListEqual(act_data[i], [x for x in row[2:]])
        con.close()
        pdb._drops()


    # тестирование PocketClass
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
        jformat = '/?$format=json'
        journ = 'ЖурналОпераций'
        reg_slice = '/AccountingRegister_%s/Balance' % urllib2.quote(journ)
        # reg_slice = unicode(reg_slice, 'utf-8')
        URL = pcs.settings['URL']
        # furl = "money.kter.ru"
        # lurl = "/money/odata/standard.odata/"
        full_url = URL + ourl + reg_slice + jformat
        authorization = pcs.settings['Authorization']

        headers = {
            'Authorization': authorization
        }
        req = urllib2.Request(full_url, None, headers)
        result = urllib2.urlopen(req)

        data = result.read()

        # print(data)
        self.assertEqual(1,1)


if __name__ == '__main__':
    unittest.main()
