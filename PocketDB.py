# coding: utf-8

"""
Классы, описывающие работу с базой данных и с соап-сервисом
"""
import sqlite3
import os
import string
import threading
import urllib2
import json
from kivy.network.urlrequest import UrlRequest
from time import sleep


def get_type(val):
    str_type = unicode(type(val))
    result = ''
    for l in str_type:
        if l in string.letters:
            result += l
    return result.replace(u'type', '')


def convert_to_type(str_value, str_type):

    def none_type(*args):
        return None

    def bool_int(*args):
        return bool(int(*args))

    action_by_str_type = {u'str': unicode,
                          u'unicode': unicode,
                          u'int': int,
                          u'float': float,
                          u'long': long,
                          u'NoneType': none_type,
                          u'list': list,
                          u'bool': bool_int}
    if str_type in action_by_str_type:
        return action_by_str_type[str_type](str_value)
    else:
        return unicode(str_value)


def convert_type_to_str(value):
    str_type = get_type(value)
    action_by_type = {u'str': unicode,
                      u'unicode': unicode,
                      u'int': int,
                      u'float': float,
                      u'long': long,
                      u'NoneType': unicode,
                      u'list': unicode,
                      u'bool': int}
    # print value
    if str_type in action_by_type:
        return unicode(action_by_type[str_type](value))
    else:
        return unicode(value)


def guid(dct):
    g_id = ''
    if type(dct) == dict and 'Ref_Key' in dct:
        g_id = dct['Ref_Key']
    return u"(guid'%s')" % g_id


class PocketsDB:

    def __init__(self, db_name='MyMoney.db'):
        self.__name__ = 'PocketsDB'
        self.db_name = db_name
        if self.check_first_start():
            self._first_start()
            self.recreate_docs()
            self.recreate_refs()
            self.reset_settings()

    def check_first_start(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        return_value = False
        try:
            # первый запуск уже был?
            cur.execute("""SELECT count(*) FROM sqlite_master
                        WHERE type='table' AND name='First_Table'
                        """
                        )
        except sqlite3.OperationalError:
            return_value = True
        for row in cur:
            return_value = row[0] == 0
        con.close()
        return return_value

    def _first_start(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        try:
            cur.execute("""CREATE TABLE First_Table(
                                    Id INTEGER PRIMARY KEY AUTOINCREMENT)
                                    """)
        except sqlite3.OperationalError:
            pass
        finally:
            con.close()

    def close_db(self):
        #self.con.close()
        pass

    def _drops(self):
        os.remove(self.db_name)

    def recreate_docs(self):
        """
        (пере)создание базы данных
        вызывается только? при синхронизации и первичной инициации объекта
        """
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()

        cur.executescript("""
--последовательность
            DROP TABLE IF EXISTS Actions;
            CREATE TABLE IF NOT EXISTS Actions(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                DateTime VARCHAR(18),
                Action_name INTEGER,
                ActionId INTEGER);
--доходы 1
            DROP TABLE IF EXISTS InAction;
            CREATE TABLE IF NOT EXISTS InAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Item VARCHAR(50),
                Summ FLOAT,
                Amount FLOAT,
                Comment TEXT);
--расходы 2
            DROP TABLE IF EXISTS OutAction;
            CREATE TABLE IF NOT EXISTS OutAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Item VARCHAR(50),
                Summ FLOAT,
                Amount FLOAT,
                Comment TEXT);
--перемещения 3
            DROP TABLE IF EXISTS BetweenAction;
            CREATE TABLE IF NOT EXISTS BetweenAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                PocketOut VARCHAR(50),
                PocketIn VARCHAR(50),
                Summ FLOAT,
                Comment TEXT);
--обмен валют 4
            DROP TABLE IF EXISTS ExchangeAction;
            CREATE TABLE IF NOT EXISTS ExchangeAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                PocketOut VARCHAR(50),
                PocketIn VARCHAR(50),
                SummOut FLOAT,
                SummIn FLOAT,
                Comment TEXT);
--мы взяли в долг 5
            DROP TABLE IF EXISTS Credit1InAction;
            CREATE TABLE IF NOT EXISTS Credit1InAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Credit VARCHAR(50),
                Summ FLOAT,
                AdditionalSumm FLOAT,
                Comment TEXT);
--мы вернули долг 6
            DROP TABLE IF EXISTS Credit1OutAction;
            CREATE TABLE IF NOT EXISTS Credit1OutAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Credit VARCHAR(50),
                Summ FLOAT,
                AdditionalSumm FLOAT,
                PercentSumm FLOAT,
                Comment TEXT);
--нам вернули долг 7
            DROP TABLE IF EXISTS Credit2InAction;
            CREATE TABLE IF NOT EXISTS Credit2InAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Credit VARCHAR(50),
                Summ FLOAT,
                AdditionalSumm FLOAT,
                PercentSumm FLOAT,
                Comment TEXT);
--мы дали в долг 8
            DROP TABLE IF EXISTS Credit2OutAction;
            CREATE TABLE IF NOT EXISTS Credit2OutAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Credit VARCHAR(50),
                Summ FLOAT,
                AdditionalSumm FLOAT,
                Comment TEXT);
            """)
        con.commit()
        con.close()

    def recreate_refs(self, pcs=None):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()

        cur.executescript("""
--кошельки
            DROP TABLE IF EXISTS Pockets;
            CREATE TABLE Pockets(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 Name VARCHAR(50), Currency VARCHAR(10));
--остатки
            DROP TABLE IF EXISTS Balances;
            CREATE TABLE Balances(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  Pocket VARCHAR(50), Balance FLOAT);
--остатки по долгам
            DROP TABLE IF EXISTS CreditBalances;
            CREATE TABLE CreditBalances(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        Credit VARCHAR(50), Balance FLOAT);
--статьи расходов
            DROP TABLE IF EXISTS OutItems;
            CREATE TABLE OutItems(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  Item VARCHAR(50));
--статьи доходов
            DROP TABLE IF EXISTS InItems;
            CREATE TABLE InItems(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 Item VARCHAR(50));
--контакты
            DROP TABLE IF EXISTS Contacts;
            CREATE TABLE Contacts(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  Name VARCHAR(50));
--кредиты
            DROP TABLE IF EXISTS Credits;
            CREATE TABLE Credits(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 Name VARCHAR(50),
                                 Contact VARCHAR(50),
                                 Currency VARCHAR(10));
--валюты
            DROP TABLE IF EXISTS Currency;
            CREATE TABLE Currency(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  Name VARCHAR(50),
                                  Course FLOAT,
                                  Multiplicity VARCHAR(10));

--дополнительные параметры
            DROP TABLE IF EXISTS KWArgs;
            CREATE TABLE KWArgs(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                ObjName VARCHAR(50),
                                ObjType VARCHAR(50),
                                DataName VARCHAR(50),
                                DataType VARCHAR(50),
                                DataValue VARCHAR(150));
            """)
        con.commit()
        if pcs is not None:
            for pocket in pcs.pockets:
                cur.execute(
                                "INSERT INTO Pockets VALUES (NULL, ?, ?)",
                                (
                                    pocket.name,
                                    pocket.currency
                                )
                            )
                cur.execute(
                                "INSERT INTO Balances VALUES (NULL, ?, ?)",
                                (
                                    pocket.name,
                                    pocket.balance
                                )
                            )
            for x in pcs.out_items:
                cur.execute("INSERT INTO OutItems VALUES (NULL, ?)", (x.name,))
            for x in pcs.in_items:
                cur.execute("INSERT INTO InItems VALUES (NULL, ?)", (x.name,))
            for x in pcs.contacts:
                cur.execute("INSERT INTO Contacts VALUES (NULL, ?)", (x.name,))
            for x in pcs.currency:
                cur.execute("INSERT INTO Currency VALUES (NULL, ?, ?, ?)",
                            (x.name, x.course, x.multiplicity))
            for credit in pcs.credits:
                cur.execute(
                                "INSERT INTO Credits VALUES (NULL, ?, ?, ?)",
                                (
                                    credit.name,
                                    credit.contact,
                                    credit.currency
                                )
                            )
                cur.execute(
                    "INSERT INTO CreditBalances VALUES (NULL, ?, ?)",
                    (
                        credit.name,
                        credit.balance
                    )
                )
            con.commit()
            for credit in pcs.credits:
                self.dump_kwargs(credit)
            for pocket in pcs.pockets:
                self.dump_kwargs(pocket)
            for item in pcs.in_items:
                self.dump_kwargs(item)
            for item in pcs.out_items:
                self.dump_kwargs(item)
            for contact in pcs.contacts:
                self.dump_kwargs(contact)
            for currency in pcs.currency:
                self.dump_kwargs(currency)

        con.close()

    def get_settings(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM Settings")
        except sqlite3.OperationalError:
            return -1
        for row in cur:
            return_value = [row[i] for i in range(2, 4)]
        con.close()
        return return_value

    def reset_settings(self, url_wsdl='', authorization=''):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.executescript("""
            DROP
                TABLE IF EXISTS Settings;
            CREATE TABLE Settings(Id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  OwnerName VARCHAR(50),
                                  Url_wsdl VARCHAR(300),
                                  Authorization VARCHAR(100));
                                  """)
        cur.execute("INSERT INTO Settings VALUES (NULL, ?, ?, ?)",
                         (1, url_wsdl, authorization))
        con.commit()
        con.close()

    def add_action(self, action_name, action_id):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
                """INSERT INTO Actions
                VALUES (NULL, datetime('now', 'localtime'), ?, ?)
                """,
                (action_name, action_id)
        )
        con.commit()
        con.close()

    def action_in(self, pocket_name, item_name, summ, amount, comment):
        """
        доходы
        в кошелек по статье на сумму
        """
        action_name = 1
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO InAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, item_name, summ, amount, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_out(self, pocket_name, item_name, summ, amount, comment):
        """
        расходы
        из кошелька по статье на сумму за количество
        """
        action_name = 2
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, item_name, summ, amount, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_between(self, pocket_out_name, pocket_in_name, summ, comment):
        """
        перемещение
        из кошелька в кошелек сумму
        """
        action_name = 3
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO BetweenAction VALUES (NULL, ?, ?, ?, ?, ?)",
            (action_name, pocket_out_name, pocket_in_name, summ, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_exchange(self, pcout_name, pcin_name, summout, summin, coment):
        """
        обмен валюты
        из кошелька в кошелек сумма расхода, сумма прихода
        """
        action_name = 4
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO ExchangeAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pcout_name, pcin_name, summout, summin, coment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_credit1_in(self, pocket_name, credit_name,
                          summ, addit_summ, comment):
        """
        мы взяли в долг
        в кошелек по кредиту у контакта сумму
        """
        action_name = 5
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Credit1InAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, credit_name, summ, addit_summ, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_credit2_in(self, pocket_name, credit_name,
                          summ, addit_summ, percent_sum, comment):
        """
        нам вернули долг
        в кошелек по кредиту от контакта сумму
        """
        action_name = 7
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Credit2InAction VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, credit_name,
             summ, addit_summ, percent_sum, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_credit1_out(self, pocket_name, credit_name,
                           summ, addit_summ, percent_sum, comment):
        """
        мы вернули долг
        из кошелька по кредиту контакту сумму
        """
        action_name = 6
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Credit1OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, credit_name,
             summ, addit_summ, percent_sum, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_credit2_out(self, pocket_name, credit_name,
                           summ, addit_summ, comment):
        """
        мы дали в долг
        из кошелька по кредиту контакту сумму
        """
        action_name = 8
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Credit2OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, credit_name,
             summ, addit_summ, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def upd_pocket_balance(self, pocket_name, pocket_balance):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
                "UPDATE Balances SET Balance = ? WHERE Pocket = ?",
                (pocket_balance, pocket_name)
        )
        con.commit()
        con.close()

    def upd_credit_balance(self, credit_name, credit_balance):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
                "UPDATE CreditBalances SET Balance = ? WHERE Credit = ?",
                (credit_balance, credit_name)
        )
        con.commit()
        con.close()

    def get_pockets(self):
        # кошельки:
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        try:
            cur.execute("""SELECT
                                  P.Name,
                                  P.Currency,
                                  B.Balance
                           FROM Pockets AS P
                           LEFT JOIN Balances AS B ON B.Pocket = P.Name
                           """
                        )
            return_value = [[row[0], row[1], row[2]] for row in cur]
        except sqlite3.OperationalError:
            return_value = -1
        finally:
            con.close()
        return return_value

    def get_items_in(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM InItems")
        return_value = [row[1] for row in cur]
        con.close()
        return return_value

    def get_items_out(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM OutItems")
        return_value = [row[1] for row in cur]
        con.close()
        return return_value

    def get_currency(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM Currency")
        return_value = [[row[1], row[2], row[3]] for row in cur]
        con.close()
        return return_value

    def get_contacts(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM Contacts")
        return_value = [row[1] for row in cur]
        con.close()
        return return_value

    def get_credits(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        try:
            cur.execute("""SELECT
                                  C.Name,
                                  C.Currency,
                                  C.Contact,
                                  B.Balance
                           FROM Credits AS C
                           LEFT JOIN CreditBalances AS B ON B.Credit = C.Name
                           """
                       )
            return_value = [[row[0], row[1], row[2], row[3]] for row in cur]
        except sqlite3.OperationalError:
            return_value = 1
        finally:
            con.close()
        return return_value

    def dump_kwargs(self, obj, obj_type=None, **kwargs):
        kw = kwargs
        if hasattr(obj, 'kwargs'):
            kw = obj.kwargs
        if hasattr(obj, '__name__'):
            obj_type = obj.__name__
        if kw is None or obj_type is None:
            raise Exception('kwargs or object type is None')
        obj_name = unicode(obj)
        # if hasattr(obj, 'name'):
        #     obj_name = obj.name
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        for k in kw:
            try:
                cur.execute(
                    """DELETE FROM KWArgs
                       WHERE ObjName = ? AND ObjType = ? AND DataName = ?""",
                    (obj_name, obj_type, k)
                )
                cur.execute("INSERT INTO KWArgs VALUES (NULL, ?, ?, ?, ?, ?)",
                            (obj_name, obj_type, k, get_type(kw[k]),
                             convert_type_to_str(kw[k]))
                            )
            except sqlite3.OperationalError:
                raise Exception('KWArgs dump fail')
        con.commit()
        con.close()

    def get_kwargs(self, obj, obj_type=None):
        if hasattr(obj,'__name__'):
            obj_type = unicode(obj.__name__)
        if obj_type is None:
            raise Exception('Object type is None')
        obj_name = unicode(obj)
        # if hasattr(obj,'name'):
        #     obj_name = obj.name
        return_value = {}
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        try:
            cur.execute("""SELECT * FROM KWArgs
                        WHERE ObjName = ? AND ObjType = ?""",
                        (obj_name, obj_type))
        except sqlite3.OperationalError:
            raise Exception('KWArgs table is wrong')
        for row in cur:
            return_value[row[3]] = convert_to_type(row[5], row[4])
        con.close()
        # print obj_name, obj_type, return_value
        return return_value


    def prepare_send_data(self):
        """функция готовит данные для передачи 1С

        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        # готовим данные для отправки
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        returnvalue = 0
        try:
            cur.execute(
                """
                SELECT
                    A.Id,
                    A.Action_name,
                    A.DateTime,
                    B.Value1,
                    B.Value2,
                    B.Value3,
                    B.Value4,
                    B.Value5,
                    B.Value6,
                    B.Value7
                FROM Actions AS A
                LEFT JOIN (
                    SELECT
                        InAction.Id                         AS Id,
                        InAction.Action_name                AS Action_name,
                        cast(InAction.Pocket    as text)    AS Value1,
                        cast(InAction.Item      as text)    AS Value2,
                        cast(InAction.Summ      as text)    AS Value3,
                        InAction.Comment                    AS Value4,
                        '-'                                  AS Value5,
                        '-'                                  AS Value6,
                        '-'                                  AS Value7
                    FROM InAction as InAction

                    UNION ALL

                    SELECT
                        OutAction.Id                        AS Id,
                        OutAction.Action_name               AS Action_name,
                        cast(OutAction.Pocket   as text)    AS Value1,
                        cast(OutAction.Item     as text)    AS Value2,
                        cast(OutAction.Summ     as text)    AS Value3,
                        cast(OutAction.Amount   as text)    AS Value4,
                        OutAction.Comment                   AS Value5,
                        '-'                                  AS Value6,
                        '-'                                  AS Value7
                    FROM OutAction as OutAction

                    UNION ALL

                    SELECT
                        BetweenAction.Id AS Id,
                        BetweenAction.Action_name AS Action_name,
                        cast(BetweenAction.PocketOut    as text) AS Value1,
                        cast(BetweenAction.PocketIn     as text) AS Value2,
                        cast(BetweenAction.Summ         as text) AS Value3,
                        BetweenAction.Comment                    AS Value4,
                        '-' AS Value5,
                        '-' AS Value6,
                        '-' AS Value7
                    FROM BetweenAction as BetweenAction

                    UNION ALL

                    SELECT
                        ExchangeAction.Id AS Id,
                        ExchangeAction.Action_name AS Action_name,
                        cast(ExchangeAction.PocketOut   as text) AS Value1,
                        cast(ExchangeAction.PocketIn    as text) AS Value2,
                        cast(ExchangeAction.SummOut     as text) AS Value3,
                        cast(ExchangeAction.SummIn      as text) AS Value4,
                        ExchangeAction.Comment AS Value5,
                        '-' AS Value6,
                        '-' AS Value7
                    FROM ExchangeAction as ExchangeAction

                    UNION ALL

                    SELECT
                        Credit1InAction.Id AS Id,
                        Credit1InAction.Action_name AS Action_name,
                        cast(Credit1InAction.Pocket         as text) AS Value1,
                        cast(Credit1InAction.Credit         as text) AS Value2,
                        cast(Credit1InAction.Summ           as text) AS Value3,
                        Credit1InAction.Comment                      AS Value4,
                        cast(Credits.Contact                as text) AS Value5,
                        cast(Credit1InAction.AdditionalSumm as text) AS Value6,
                        '-' AS Value7
                    FROM Credit1InAction as Credit1InAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Credit1InAction.Credit

                    UNION ALL

                    SELECT
                        Credit1OutAction.Id AS Id,
                        Credit1OutAction.Action_name AS Action_name,
                        cast(Credit1OutAction.Pocket            as text) AS Value1,
                        cast(Credit1OutAction.Credit            as text) AS Value2,
                        cast(Credit1OutAction.Summ              as text) AS Value3,
                        Credit1OutAction.Comment                         AS Value4,
                        cast(Credits.Contact                    as text) AS Value5,
                        cast(Credit1OutAction.AdditionalSumm    as text) AS Value6,
                        cast(Credit1OutAction.PercentSumm       as text) AS Value7
                    FROM Credit1OutAction as Credit1OutAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Credit1OutAction.Credit

                    UNION ALL

                    SELECT
                        Credit2InAction.Id AS Id,
                        Credit2InAction.Action_name AS Action_name,
                        cast(Credit2InAction.Pocket         as text) AS Value1,
                        cast(Credit2InAction.Credit         as text) AS Value2,
                        cast(Credit2InAction.Summ           as text) AS Value3,
                        Credit2InAction.Comment                      AS Value4,
                        cast(Credits.Contact                as text) AS Value5,
                        cast(Credit2InAction.AdditionalSumm as text) AS Value6,
                        cast(Credit2InAction.PercentSumm    as text) AS Value7
                    FROM Credit2InAction as Credit2InAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Credit2InAction.Credit

                    UNION ALL

                    SELECT
                        Credit2OutAction.Id AS Id,
                        Credit2OutAction.Action_name AS Action_name,
                        cast(Credit2OutAction.Pocket as text)         AS Value1,
                        cast(Credit2OutAction.Credit as text)         AS Value2,
                        cast(Credit2OutAction.Summ as text)           AS Value3,
                        Credit2OutAction.Comment                      AS Value4,
                        cast(Credits.Contact as text)                 AS Value5,
                        cast(Credit2OutAction.AdditionalSumm as text) AS Value6,
                        '-' AS Value7
                    FROM Credit2OutAction as Credit2OutAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Credit2OutAction.Credit

                ) AS B
                    ON A.Action_name = B.Action_name and A.ActionId = B.Id
                ORDER BY A.Id
                """
            )
        except sqlite3.OperationalError:
            returnvalue = 1
        data = []
        if returnvalue == 1:
            return data
        data = [[row[i] for i in xrange(10)] for row in cur]
        con.close()
        return data


# передача и получение данных посредством веб-сервиса

class ODataRequests:

    def __init__(self, settings):
        self.__name__ = 'ODataRequests'
        self.fix_set = {'odata_url': '/odata/standard.odata/',
                        'json_format': '/?$format=json;odata=nometadata',
                        'json_': '/?$format=json',
                        'post': '/Post?PostingModeOperational=false',
                        'journ_oper': 'AccountingRegister_' +
                                      urllib2.quote('ЖурналОпераций'),
                        'balance': '/Balance',
                        'slice': '/SliceLast',
                        'journ_cur': 'InformationRegister_' +
                                   urllib2.quote('КурсыВалют'),
                        'ref_cur': 'Catalog_' +
                                   urllib2.quote('Валюты'),
                        'ref_pockets': 'Catalog_' +
                                       urllib2.quote('КошелькиИСчета'),
                        'ref_credits': 'Catalog_' +
                                       urllib2.quote('Долги'),
                        'ref_contacts': 'Catalog_' +
                                       urllib2.quote('Контакты'),
                        'ref_in_items': 'Catalog_' +
                                       urllib2.quote('СтатьиДоходов'),
                        'ref_out_items': 'Catalog_' +
                                       urllib2.quote('СтатьиРасходов'),
                        'doc_in': 'Document_' +
                                       urllib2.quote('Доход'),
                        'doc_out': 'Document_' +
                                       urllib2.quote('Расход'),
                        'doc_between': 'Document_' +
                                       urllib2.quote('Перемещение'),
                        'doc_exchange': 'Document_' +
                                       urllib2.quote('ОбменВалюты'),
                        'doc_credit1_in': 'Document_' +
                                       urllib2.quote('МыВзялиВДолг'),
                        'doc_credit2_in': 'Document_' +
                                       urllib2.quote('НамВернулиДолг'),
                        'doc_credit1_out': 'Document_' +
                                       urllib2.quote('МыВернулиДолг'),
                        'doc_credit2_out': 'Document_' +
                                       urllib2.quote('МыДалиВДолг'),
                        'filter': ("&$filter=Date ge datetime'%sT00:00:00' " +
                                    "and Date le datetime'%sT00:00:00' " +
                                    "and Posted eq true")}
        self.settings = settings
        self.max_get_actions = 0
        self.num_get_actions = 0
        self.num_get_error_actions = 0
        self.max_post_actions = 0
        self.num_post_actions = 0
        self.num_post_error_actions = 0
        self.event_to_call_post = threading.Event()
        self.event_to_call_get = threading.Event()
        self.set_progress = None
        self.num_docs_by_period = 0
        self._docs_by_period_dict = {}
        self._docs_by_period_call_back = None

    def re_settings(self, settings):
        self.settings = settings

    def get(self, url, **kwargs):
        headers = {'Authorization': self.settings['Authorization']}
        req = UrlRequest(url, req_headers=headers, **kwargs)
        req.wait(delay=0.1)

    def post(self, url, body, **kwargs):
        self.get(url, req_body=body, **kwargs)

    def url_currency(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['ref_cur'] + self.fix_set['json_format'])
        return url

    def url_pockets(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['ref_pockets'] + self.fix_set['json_format'])
        return url

    def url_credits(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['ref_credits'] + self.fix_set['json_format'])
        return url

    def url_contacts(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['ref_contacts'] + self.fix_set['json_format'])
        return url

    def url_in_items(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['ref_in_items'] + self.fix_set['json_format'])
        return url

    def url_out_items(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['ref_out_items'] + self.fix_set['json_format'])
        return url

    def url_balance(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['journ_oper'] + self.fix_set['balance'] +
               self.fix_set['json_format'])
        return url

    def url_courses(self):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['journ_cur'] + self.fix_set['slice'] +
               self.fix_set['json_format'])
        return url

    def get_refs(self, callback_funcs):
        if 'OneCurrency' in callback_funcs:
            self.get(self.url_currency(),
                     on_success=callback_funcs['OneCurrency'],
                     on_error=self.event_get_error_action)
        if 'OneInItem' in callback_funcs:
            self.get(self.url_in_items(),
                     on_success=callback_funcs['OneInItem'],
                     on_error=self.event_get_error_action)
        if 'OneOutItem' in callback_funcs:
            self.get(self.url_out_items(),
                     on_success=callback_funcs['OneOutItem'],
                     on_error=self.event_get_error_action)
        if 'OneContact' in callback_funcs:
            self.get(self.url_contacts(),
                     on_success=callback_funcs['OneContact'],
                     on_error=self.event_get_error_action)
        if 'OnePocket' in callback_funcs:
            self.get(self.url_pockets(),
                     on_success=callback_funcs['OnePocket'],
                     on_error=self.event_get_error_action)
        if 'OneCredit' in callback_funcs:
            self.get(self.url_credits(),
                     on_success=callback_funcs['OneCredit'],
                     on_error=self.event_get_error_action)
        if 'Balance' in callback_funcs:
            self.get(self.url_balance(),
                     on_success=callback_funcs['Balance'],
                     on_error=self.event_get_error_action)
        if 'Courses' in callback_funcs:
            self.get(self.url_courses(),
                     on_success=callback_funcs['Courses'],
                     on_error=self.event_get_error_action)

    def post_action_in(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_in'] + self.fix_set['json_format'])
        value = {
            "Date": data['date'], #"2016-03-16T22:22:22",
            u"Комментарий": data['comment'],
            u"Доходы": [{
                "LineNumber": "1",
                #u"Кошелек_Key": "85565e0a-11bf-11e4-589e-0018f3e1b84e",
                u"Кошелек_Key": data['pocket_key'], #"c4182b70-ca31-11e4-1491-0018f3e1b84e",
                u"СтатьяДохода_Key": data['item_in_key'], #"f8bbc04a-70bc-11dc-89ac-00195b6993ba",
                u"СуммаДохода": data['sum'], #1000,
                u"Комментарий": data['line_comment'], #u"тест",
            #    u"АналитикаСтатьи_Key": "00000000-0000-0000-0000-000000000000",
                u"СуммаВВалютеОперации": data['sum_rub'], #1234,
                u"Курс": data['course'], #100,
                u"Кратность": data['multiplicity'],#"1",
            #    u"ФинансоваяЦель_Key": "00000000-0000-0000-0000-000000000000"
            }],
            #u"АналитикаДокумента": []
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def post_action_out(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_out'] + self.fix_set['json_format'])
        value = {
            "Date": data['date'],
            # u"РазделУчета_Key": "44747adc-5dd5-11e3-95ac-005056c00008",
            u"КошелекДолг": data['pocket_key'],
            u"КошелекДолг_Type": u"StandardODATA.Catalog_КошелькиИСчета",
            u"ВалютаОперации_Key": data['currency_key'],
            # u"СуммаОплаты": data['sum'],
            u"Комментарий": data['comment'],
            u"Расходы": [{
                "LineNumber": "1",
                u"СтатьяРасходаИмущество": data['item_out_key'],
                u"СтатьяРасходаИмущество_Type":
                    "StandardODATA.Catalog_СтатьиРасходов",
                u"Сумма": data['sum'],
                u"Количество": data['amount'],
                u"КомментарийСтроки": data['line_comment']
            }],
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def post_action_between(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_between'] + self.fix_set['json_format'])
        value = {
            "Date": data['date'],
            # u"СчетОткуда_Key": "44747adc-5dd5-11e3-95ac-005056c00008",
            # u"СчетКуда_Key": "44747adc-5dd5-11e3-95ac-005056c00008",
            u"КошелекОткуда_Key": data['pocket_out_key'],
            u"КошелекКуда_Key": data['pocket_in_key'],
            u"СуммаОперации": data['sum'],
            u"ВалютаОперации_Key": data['currency_key'],
            u"Комментарий": data['line_comment']
            # u"СписаноСУчетомРасходов": 1000,
            # u"ПолученоСУчетомРасходов": 1000,
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def post_action_exchange(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_exchange'] + self.fix_set['json_format'])
        value = {
            "Date": data['date'],
            u"КошелекОткуда_Key": data['pocket_out_key'],
            # u"ФинансоваяЦельОткуда_Key": "44747ae3-5dd5-11e3-95ac-005056c00008",
            u"СуммаВыдано": data['sum_out'],
            u"ВалютаСписания_Key": data['currency_out_key'],
            u"КошелекКуда_Key": data['pocket_in_key'],
            # u"ФинансоваяЦельКуда_Key": "44747ae3-5dd5-11e3-95ac-005056c00008",
            u"СуммаПолучено": data['sum_in'],
            u"ВалютаПоступления_Key": data['currency_in_key'],
            # u"РасходыИзКошелькаПоступления": data['pocket_in_sum_out'],
            # u"РасходыИзКошелькаСписания": data['pocket_out_sum_out'],
            u"Комментарий": data['line_comment'],
            u"СписаноСУчетомКомиссии": data['sum_out'],
            u"ПолученоСУчетомКомиссии": data['sum_in']
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def post_action_credit1_in(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_credit1_in'] + self.fix_set['json_format'])
        value = {
            u"Date": data['date'],
            u"Кредитор_Key": data['contact_key'],
            u"Кредит_Key": data['credit_key'],
            u"Кошелек_Key": data['pocket_key'],
            #"ФинансоваяЦель_Key": "44747ae3-5dd5-11e3-95ac-005056c00008",
            u"ВалютаПолучено_Key": data['currency_key'],
            u"СуммаПолучено": data['sum'],
            u"ВалютаКредита_Key": data['currency_key'],
            u"СуммаКредита": data['sum'],
            # "Пользователь_Key": "00000000-0000-0000-0000-000000000000",
            # "ОписаниеОперации": "Мы взяли в долг [обеды] в кошелек [Наличные Олег]",
            u"Комментарий": data['line_comment'],
            u"СуммаДополнительныхРасходов": data['addit_sum']
            # "РазделУчета_Key": "44747ad5-5dd5-11e3-95ac-005056c00008"
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def post_action_credit1_out(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_credit1_out'] + self.fix_set['json_format'])
        value = {
            u"Date": data['date'],
            u"ВалютаКошелька_Key": data['currency_key'],
            u"ВалютаКредита_Key": data['currency_key'],
            u"ВыплаченоКомиссии": data['additional_sum'],
            u"ВыплаченоКредита": data['sum'],
            u"ВыплаченоПроцентов": data['percent_sum'],
            u"Комментарий": data['comment'],
            u"Кошелек_Key": data['pocket_key'],
            u"КратностьВалютыКошелька": data['multiplicity'],
            u"КратностьВалютыКредита": data['multiplicity'],
            u"Кредит_Key": data['credit_key'],
            u"Кредитор_Key": data['contact_key'],
            u"КурсВалютыКошелька": data['course'],
            u"КурсВалютыКредита": data['course'],
            u"СписаноКредита": 0,
            # u"СтатьяРасходовПоКомиссии_Key": "00000000-0000-0000-0000-000000000000",
            u"СтатьяРасходовПоПроцентам_Key": data['percent_item_key'],
            # u"СтатьяСписания_Key": "00000000-0000-0000-0000-000000000000",
            u"СуммаДополнительныхРасходов": data['additional_sum'],
            u"СуммаКредитаВВалютеКредита": data['sum'],
            u"СуммаОперации": data['total_sum'],
            u"СуммаПроцентовВВалютеКредита": data['percent_sum'],
            # u"ФинансоваяЦель_Key": "00000000-0000-0000-0000-000000000000"
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def post_action_credit2_in(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_credit2_in'] + self.fix_set['json_format'])
        value = {
            u"Date": data['date'],
            u"ВалютаДолга_Key": data['currency_key'],
            u"ВалютаПолучено_Key": data['currency_key'],
            u"ВсегоСуммаПоступления": data['sum'],
            u"Долг_Key": data['credit_key'],
            u"Комментарий": data['comment'],
            u"Контакт_Key": data['contact_key'],
            u"Кошелек_Key": data['pocket_key'],
            u"СтатьяДоходовПоПроцентам_Key": data['item_key'],
            u"СуммаВозвратаДолга": data['sum'],
            u"СуммаДополнительныхРасходов": data['additional_sum'],
            u"СуммаПолучено": data['sum'],
            u"СуммаПроцентов": data['percent_sum'],
            u"СуммаПроцентовВВалютеДолга": data['percent_sum'],
            u"СуммаСписания": 0
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def post_action_credit2_out(self, data):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['doc_credit2_out'] + self.fix_set['json_format'])
        value = {
            u"Date": data['date'],
            u"Контакт_Key": data['contact_key'],
            u"Долг_Key": data['credit_key'],
            u"Кошелек_Key": data['pocket_key'],
            # u"ФинансоваяЦель_Key": "44747ae3-5dd5-11e3-95ac-005056c00008",
            u"ВалютаВыдано_Key": data['currency_key'],
            u"СуммаВыдано": data['sum'],
            u"ВалютаЗайма_Key": data['currency_key'],
            u"СуммаЗайма": data['sum'],
            u"Комментарий": data['comment'],
            u"СуммаДополнительныхРасходов": data['additional_sum'],
            u"ВсегоРасход": data['total_sum']
        }
        self.post(url, json.dumps(value),
                  on_success=self.success_post_data,
                  on_error=self.event_post_error_action)

    def success_post_data(self, req, data):
        url = req.url.replace(self.fix_set['json_format'],
                              guid(data) + self.fix_set['post'])
        self.get(url,
                 on_success=self.event_post_action,
                 on_error=self.event_post_error_action)

    def event_post_action(self, req=None, result=None):
        self.num_post_actions -= 1
        if self.num_post_actions == 0:
            self.event_to_call_post.set()

    def event_post_error_action(self, req=None, result=None):
        self.num_post_actions -= 1
        self.num_post_error_actions += 1
        if self.num_post_actions == 0:
            self.event_to_call_post.set()

    def event_get_actions(self, req=None, result=None):
        self.num_get_actions -= 1
        if self.num_get_actions == 0:
            self.event_to_call_get.set()

    def event_get_error_action(self, req=None, result=None):
        self.num_get_actions -= 1
        self.num_get_error_actions += 1
        if self.num_get_actions == 0:
            self.event_to_call_get.set()

    def post_new_contact(self, contact_name):
        url = (self.settings['URL'] + self.fix_set['odata_url'] +
               self.fix_set['ref_contacts'] + self.fix_set['json_format'])
        value = {
            "IsFolder": False,
            "Description": contact_name,
            u"Активность": True,
        }
        self.post(url, json.dumps(value))
        web_ref = ''
        try:
            web_ref = self.post(url, json.dumps(value))
        except:
            return False
        dict_ref = json.loads(web_ref)
        return True

    # todo: создание новых статей, кредитов, кошельков.

    def post_docs(self, data):
        for d in data:
            if d['action'] == 1:
                self.post_action_in(d)
            if d['action'] == 2:
                self.post_action_out(d)
            if d['action'] == 3:
                self.post_action_between(d)
            if d['action'] == 4:
                self.post_action_exchange(d)
            if d['action'] == 5:
                self.post_action_credit1_in(d)
            if d['action'] == 6:
                self.post_action_credit1_out(d)
            if d['action'] == 7:
                self.post_action_credit2_in(d)
            if d['action'] == 8:
                self.post_action_credit2_out(d)

    def post_writer(self, to_call):
        self.event_to_call_post.wait()  # wait for event
        self.event_to_call_post.clear()  # clean event for future
        if self.num_post_error_actions == 0:
            to_call()

    def get_writer(self, to_call, arg):
        self.event_to_call_get.wait()  # wait for event
        self.event_to_call_get.clear()  # clean event for future
        if self.num_get_error_actions == 0:
            to_call(arg)

    def wait_for_post_and_recreate(self, to_call):
        self.num_post_error_actions = 0
        self.event_to_call_post.clear()
        t1 = threading.Thread(target=self.post_writer, args=(to_call,))
        t1.start()
        # t1.join()

    def wait_for_get_and_recreate(self, to_call, arg):
        self.num_get_error_actions = 0
        self.event_to_call_get.clear()
        t1 = threading.Thread(target=self.get_writer, args=(to_call, arg))
        t1.start()

    def check_progress(self):
        res = (self.num_get_actions + self.num_post_actions,
               self.num_get_error_actions + self.num_post_error_actions)
        if self.set_progress is not None:
            self.set_progress(res[0])
        return res

    def _docs_by_period(self, req, data):
        self.num_docs_by_period -= 1
        meta = data['odata.metadata'].split('#')[1]
        for i in data['value']:
            self._docs_by_period_dict[i['Date'] + i['Ref_Key']] = i
            self._docs_by_period_dict[i['Date'] + i['Ref_Key']]['meta'] = meta
        if self.num_docs_by_period == 0:
            if self._docs_by_period_call_back is not None:
                self._docs_by_period_call_back(self._docs_by_period_dict)

    def _docs_by_period_error(self, req=None, result=None):
        self.num_docs_by_period -= 1
        if self.num_docs_by_period == 0:
            if self._docs_by_period_call_back is not None:
                self._docs_by_period_call_back(self._docs_by_period_dict)

    def get_docs_by_period(self, begin_date, end_date, call_back=None):
        if self.num_docs_by_period != 0:
            return
        self._docs_by_period_call_back = call_back
        self.num_docs_by_period = 8
        for k in self.fix_set:
            if k[:4] == 'doc_':
                url = (self.settings['URL'] + self.fix_set['odata_url'] +
                       self.fix_set[k] + self.fix_set['json_'] +
                       self.fix_set['filter'] % (begin_date, end_date))
                self.get(url, on_success=self._docs_by_period,
                         on_error=self._docs_by_period_error)