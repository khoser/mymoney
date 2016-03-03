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
        pdb = PocketDB.PocketsDB('test1_db')
        self.assertFalse(pdb.check_first_start())

        tbl_names = [u'Pockets',
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
                     u'Credit2OutAction',
                     u'KWArgs']
        tbl_names.sort()
        return_value = []
        con = sqlite3.connect(pdb.db_name)
        cur = con.cursor()
        try:
            cur.execute("""SELECT name FROM sqlite_master
                        WHERE type='table' AND name in (%s)
                        """%(', '.join('?' for _ in tbl_names)), (tbl_names)
                        )
        except sqlite3.OperationalError:
            pass
        for row in cur:
            return_value.append(row[0])
        con.close()
        return_value.sort()
        self.assertListEqual(tbl_names, return_value)
        pdb._drops()

    def test_all_actions(self):
        pdb = PocketDB.PocketsDB('test2_db')
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
        tbl_names = ['InAction',
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
            cur.execute("SELECT * FROM %s" % tbl_names[i])
            for row in cur:
                self.assertListEqual(act_data[i], [x for x in row[2:]])
        con.close()
        pdb._drops()

    def test_upd_balances(self):
        _name = 'Test'
        _cur = u'руб'
        _cont = 'My contact'
        _bal = 123
        _p_bal = 234.5
        _c_bal = 345.6
        pcs = PocketClass.Pockets('test3_db')
        pdb = pcs.db
        pcs.set_pocket(_name, _cur, _bal)
        pcs.set_credit(_name, _cur, _cont, _bal)
        pdb.recreate_refs(pcs)
        pdb.upd_pocket_balance(_name, _p_bal)
        pdb.upd_credit_balance(_name, _c_bal)
        con = sqlite3.connect(pdb.db_name)
        cur = con.cursor()
        try:
            cur.execute("SELECT Balance FROM Balances")
        except sqlite3.OperationalError:
            pass
        for row in cur:
            self.assertEqual(row[0], _p_bal)
        try:
            cur.execute("SELECT Balance FROM CreditBalances")
        except sqlite3.OperationalError:
            pass
        for row in cur:
            self.assertEqual(row[0], _c_bal)
        con.close()
        pdb._drops()

    def test_get_data(self):
        in_items = [u'item1', u'item2', u'Item3']
        out_items = [u'Item4', u'Item5', u'item6']
        contacts = [u'contact 1', u'contact 2', u'contact 3']
        pockets = {u'p1': [u'p1', u'руб', 123.4],
                   u'p2': [u'p2', u'руб', 234.5],
                   u'p3': [u'p3', u'USD', 345.6]}
        credit_s = {u'c1': [u'c1', u'руб', u'contact 1', 456.7],
                    u'c2': [u'c2', u'руб', u'contact 2', 567.8],
                    u'c3': [u'c3', u'USD', u'contact 3', 678.9]}
        pcs = PocketClass.Pockets('test4_db')
        pdb = pcs.db
        pcs.in_items = in_items
        pcs.out_items = out_items
        pcs.contacts = contacts
        for p in pockets:
            pcs.set_pocket(*pockets[p])
        for c in credit_s:
            pcs.set_credit(*credit_s[c])
        pdb.recreate_refs(pcs)
        return_val = pdb.get_items_in()
        return_val.sort()
        in_items.sort()
        self.assertListEqual(return_val, in_items)
        return_val = pdb.get_items_out()
        return_val.sort()
        out_items.sort()
        self.assertListEqual(return_val, out_items)
        return_val = pdb.get_contacts()
        return_val.sort()
        contacts.sort()
        self.assertListEqual(return_val, contacts)
        return_val = pdb.get_pockets()
        if return_val == -1:
            raise Exception('Pockets table broken.', return_val)
        for p in return_val:
            self.assertListEqual(p[:len(pockets[p[0]])], pockets[p[0]])
        return_val = pdb.get_credits()
        if return_val == -1:
            raise Exception('Credits table broken.', return_val)
        for c in return_val:
            self.assertListEqual(c[:len(credit_s[c[0]])], credit_s[c[0]])
        pdb._drops()

    def test_type_convert(self):
        acts = [['str', 'some text', 'some text'],
                ['str', False, 'False'],
                ['str', 123, '123'],
                ['int', '123', 123],
                ['int', '-123', -123],
                ['float', '-123', -123.0],
                ['float', '123.4', 123.4],
                ['long', '1234', 1234L],
                ['NoneType', '1234', None],
                ['NoneType', None, None],
                ['NoneType', 0, None],
                ['bool', 0, False],
                ['bool', 1, True],
                ['bool', '0', False],
                ['bool', '1', True]
                ]
        pdb = PocketDB.PocketsDB('test5_db')
        for a in acts:
            self.assertEqual(PocketDB.convert_to_type(a[1], a[0]), a[2])
        pdb._drops()

    def test_convert_to_str(self):
        acts = [['some text', 'some text'],
                [False, '0'],
                [True, '1'],
                [123, '123'],
                [-123, '-123'],
                [123.4, '123.4'],
                [None, 'None'],
                [0, '0'],
                ]
        pdb = PocketDB.PocketsDB('test6_db')
        for a in acts:
            self.assertEqual(PocketDB.convert_type_to_str(a[0]), a[1])
        pdb._drops()

    def test_dump_get_kwargs(self):
        pdb = PocketDB.PocketsDB('test7_db')
        kw1 = {u'Ref_Key': u"9747544e-11c8-11e4-589e-0018f3e1b84e",
               u'IsFolder': False,
               u'Description': u"Name",
               u'Активность': True}
        kw2 = {u'Ref_Key': u"44747adc-5dd5-11e3-95ac-005056c00008",
               u'ВалютнаяСуммаBalance': 123.45,
               u'ExtDimension1': u"Name",
               u'Активность': True,
               u'Пассивность': True}
        kw3 = {u'Ref_Key': u"6b4785a2-5ee9-11e5-6c8d-0018f3e1b84e",
               u'SomeValue': None,
               u'Description': 345,
               u'Активность': True}
        pct1 = PocketClass.OnePocket(u'Test1', u'руб', 123, **kw1)
        pct2 = PocketClass.OneCredit(u'Test2', u'руб', u'My contact', 123, **kw2)
        # третий - для произвольного объекта, например статьи расхода
        pdb.dump_kwargs(pct1)
        pdb.dump_kwargs(pct2)
        pdb.dump_kwargs('Item1', 'in_items', **kw3)
        return_value = []
        con = sqlite3.connect(pdb.db_name)
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM KWArgs")
        except sqlite3.OperationalError:
            raise Exception('KWArgs table is wrong')
        for row in cur:
            return_value.append([row[0], row[1], row[2], row[3], row[4]])
        con.close()
        return_value.sort()
        ethalon = []
        for k in pct1.kwargs:
            ethalon.append([pct1.name, pct1.__name__,
                            k,
                            PocketDB.get_type(pct1.kwargs[k]), pct1.kwargs[k]])
        for k in pct2.kwargs:
            ethalon.append([pct2.name, pct2.__name__,
                            k,
                            PocketDB.get_type(pct2.kwargs[k]), pct2.kwargs[k]])
        for k in kw3:
            ethalon.append([u'Item1', u'in_items',
                            k, PocketDB.get_type(kw3[k]), kw3[k]])
        ethalon.sort()
        self.assertListEqual(ethalon, return_value)
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
        pcs = PocketClass.Pockets('test8_db')
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
        pcs = PocketClass.Pockets('test9_db')
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
        pcs = PocketClass.Pockets('test10_db')
        args = ['Test', 'руб', 123]
        pcs.set_pocket(*args)
        pcs._drop_pocket('Test')
        self.assertEqual(len(pcs.pockets),0)
        pcs._drop_db()

    def test_drop_credit(self):
        # print ('test drop credit')
        pcs = PocketClass.Pockets('test11_db')
        args = ['Test', 'руб', 'My contact', 123]
        pcs.set_credit(*args)
        pcs._drop_credit('Test')
        self.assertEqual(len(pcs.credits),0)
        pcs._drop_db()

    def test_odata(self):
        # print ('test odata')
        pcs = PocketClass.Pockets('MyPythonMoney.db')
        pcs.get_settings()

        ourl = '/odata/standard.odata'
        jformat = '/?$format=json'
        journ = urllib2.quote('ЖурналОпераций')
        reg_slice = '/AccountingRegister_%s/Balance' % journ
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
