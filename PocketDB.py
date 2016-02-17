# coding: utf-8

"""
Классы, описывающие работу с базой данных и с соап-сервисом
"""
import sqlite3
from suds import WebFault
from suds.client import Client
import base64
from multiprocessing import Pool


class PocketsDB():

    def __init__(self, db_name='MyMoney.db'):
        self.db_name = db_name
        if self.check_first_start():
            self.recreate_docs()
            self.recreate_refs()
            self.reset_settings('', '', '')

    def check_first_start(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        try:
            # первый запуск уже был?
            cur.execute("SELECT * FROM First_Table")
        except sqlite3.OperationalError:
            cur.execute("CREATE TABLE First_Table(Id INTEGER)")
            return True
        finally:
            con.close()
        return False

    def close_db(self):
        #self.con.close()
        pass

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
            DROP TABLE IF EXISTS Сredit1InAction;
            CREATE TABLE IF NOT EXISTS Сredit1InAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Credit VARCHAR(50),
                Summ FLOAT,
                AdditionalSumm FLOAT,
                Comment TEXT);
--мы вернули долг 6
            DROP TABLE IF EXISTS Сredit1OutAction;
            CREATE TABLE IF NOT EXISTS Сredit1OutAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Credit VARCHAR(50),
                Summ FLOAT,
                AdditionalSumm FLOAT,
                PercentSumm FLOAT,
                Comment TEXT);
--нам вернули долг 7
            DROP TABLE IF EXISTS Сredit2InAction;
            CREATE TABLE IF NOT EXISTS Сredit2InAction(
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Action_name INTEGER,
                Pocket VARCHAR(50),
                Credit VARCHAR(50),
                Summ FLOAT,
                AdditionalSumm FLOAT,
                Comment TEXT);
--мы дали в долг 8
            DROP TABLE IF EXISTS Сredit2OutAction;
            CREATE TABLE IF NOT EXISTS Сredit2OutAction(
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
            CREATE TABLE Pockets(Name VARCHAR(50), Currency VARCHAR(10));
--остатки
            DROP TABLE IF EXISTS Balances;
            CREATE TABLE Balances(Pocket VARCHAR(50), Balance FLOAT);
--остатки по долгам
            DROP TABLE IF EXISTS CreditBalances;
            CREATE TABLE CreditBalances(Credit VARCHAR(50),
                                       Balance FLOAT);
--статьи расходов
            DROP TABLE IF EXISTS OutItems;
            CREATE TABLE OutItems(Item VARCHAR(50));
--статьи доходов
            DROP TABLE IF EXISTS InItems;
            CREATE TABLE InItems(Item VARCHAR(50));
--контакты
            DROP TABLE IF EXISTS Contacts;
            CREATE TABLE Contacts(Name VARCHAR(50));
--кредиты
            DROP TABLE IF EXISTS Credits;
            CREATE TABLE Credits(Name VARCHAR(50),
                                 Contact VARCHAR(50),
                                 Currency VARCHAR(10));
            """)
        con.commit()
        if pcs is not None:
            for pocket in pcs.pockets:
                cur.execute(
                                "INSERT INTO Pockets VALUES (?, ?)",
                                (
                                    pocket.name,
                                    pocket.currency
                                )
                            )
                cur.execute(
                                "INSERT INTO Balances VALUES (?, ?)",
                                (
                                    pocket.name,
                                    pocket.balance
                                )
                            )
            for x in pcs.out_items:
                cur.execute("INSERT INTO OutItems VALUES (?)", (x,))
            for x in pcs.in_items:
                cur.execute("INSERT INTO InItems VALUES (?)", (x,))
            for x in pcs.contacts:
                cur.execute("INSERT INTO Contacts VALUES (?)", (x,))
            for credit in pcs.credits:
                cur.execute(
                                "INSERT INTO Credits VALUES (?, ?, ?)",
                                (
                                    credit.name,
                                    credit.contact,
                                    credit.currency
                                )
                            )
                cur.execute(
                                "INSERT INTO CreditBalances VALUES (?, ?)",
                                (
                                    credit.name,
                                    credit.balance
                                )
                            )
            con.commit()
        con.close()

    def get_settings(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM Settings")
        except sqlite3.OperationalError:
            return -1
        for row in cur:
            return_value = [row[i] for i in range(1,4)]
        con.close()
        return return_value

    def reset_settings(self, url_wsdl, login, password):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.executescript("""
            DROP
                TABLE IF EXISTS Settings;
            CREATE TABLE Settings(OwnerName VARCHAR(50),
                                  Url_wsdl VARCHAR(300),
                                  Login VARCHAR(50),
                                  Pass VARCHAR(300));
                                  """)
        cur.execute("INSERT INTO Settings VALUES (?, ?, ?, ?)",
                         (1, url_wsdl, login, password))
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

    def action_in(self, pocket_name, item, summ, amount, comment):
        """
        доходы
        в кошелек по статье на сумму
        """
        action_name = 1
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO InAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, item, summ, amount, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_out(self, pocket_name, item, summ, amount, comment):
        """
        расходы
        из кошелька по статье на сумму за количество
        """
        action_name = 2
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, item, summ, amount, comment)
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
            "INSERT INTO Сredit1InAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, credit_name, summ, addit_summ, comment)
        )
        lid = cur.lastrowid
        con.commit()
        con.close()
        self.add_action(action_name, lid)

    def action_credit2_in(self, pocket_name, credit_name,
                          summ, addit_summ, comment):
        """
        нам вернули долг
        в кошелек по кредиту от контакта сумму
        """
        action_name = 7
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO Сredit2InAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, credit_name, summ, addit_summ, comment)
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
            "INSERT INTO Сredit1OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
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
            "INSERT INTO Сredit2OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pocket_name, credit_name, summ, addit_summ, comment)
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
                (pocket_name, pocket_balance)
        )
        con.commit()
        con.close()

    def upd_credit_balance(self, credit_name, credit_balance):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute(
                "UPDATE CreditBalances SET Balance = ? WHERE Credit = ?",
                (credit_name, credit_balance)
        )
        con.commit()
        con.close()

    def prepare_send_data(self):
        """функция передает данные сервису 1С (веб-сервису)

        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        # готовим данные для отправки
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        returnvalue = 0
        try:
            cur.execute("""
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
                        BetweenAction.Comment AS Value4,
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
                        Сredit1InAction.Id AS Id,
                        Сredit1InAction.Action_name AS Action_name,
                        cast(Сredit1InAction.Pocket         as text) AS Value1,
                        cast(Сredit1InAction.Credit         as text) AS Value2,
                        cast(Сredit1InAction.Summ           as text) AS Value3,
                        Сredit1InAction.Comment AS Value4,
                        cast(Credits.Contact                as text) AS Value5,
                        cast(Сredit1InAction.AdditionalSumm as text) AS Value6,
                        '-' AS Value7
                    FROM Сredit1InAction as Сredit1InAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Сredit1InAction.Credit

                    UNION ALL

                    SELECT
                        Сredit1OutAction.Id AS Id,
                        Сredit1OutAction.Action_name AS Action_name,
                        cast(Сredit1OutAction.Pocket            as text) AS Value1,
                        cast(Сredit1OutAction.Credit            as text) AS Value2,
                        cast(Сredit1OutAction.Summ              as text) AS Value3,
                        Сredit1OutAction.Comment AS Value4,
                        cast(Credits.Contact                    as text) AS Value5,
                        cast(Сredit1OutAction.AdditionalSumm    as text) AS Value6,
                        cast(Сredit1OutAction.PercentSumm       as text) AS Value7
                    FROM Сredit1OutAction as Сredit1OutAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Сredit1OutAction.Credit

                    UNION ALL

                    SELECT
                        Сredit2InAction.Id AS Id,
                        Сredit2InAction.Action_name AS Action_name,
                        cast(Сredit2InAction.Pocket         as text) AS Value1,
                        cast(Сredit2InAction.Credit         as text) AS Value2,
                        cast(Сredit2InAction.Summ           as text) AS Value3,
                        Сredit2InAction.Comment AS Value4,
                        cast(Credits.Contact                as text) AS Value5,
                        cast(Сredit2InAction.AdditionalSumm as text) AS Value6,
                        '-' AS Value7
                    FROM Сredit2InAction as Сredit2InAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Сredit2InAction.Credit

                    UNION ALL

                    SELECT
                        Сredit2OutAction.Id AS Id,
                        Сredit2OutAction.Action_name AS Action_name,
                        cast(Сredit2OutAction.Pocket as text) AS Value1,
                        cast(Сredit2OutAction.Credit as text) AS Value2,
                        cast(Сredit2OutAction.Summ as text) AS Value3,
                        Сredit2OutAction.Comment AS Value4,
                        cast(Credits.Contact as text) AS Value5,
                        cast(Сredit2OutAction.AdditionalSumm as text) AS Value6,
                        '-' AS Value7
                    FROM Сredit2OutAction as Сredit2OutAction
                        LEFT JOIN Credits as Credits ON Credits.Name = Сredit2OutAction.Credit

                ) AS B
                    ON A.Action_name = B.Action_name and A.ActionId = B.Id
                ORDER BY A.Id
                """)
        except sqlite3.OperationalError:
            returnvalue = 1
        data = []
        if returnvalue == 1:
            return data
        for row in cur:
            values = [self.settings['Login'], self.actions_names[row[1]]]
            for i in xrange(8):
                values.append(row[i+2])
            data.append(values)
        con.close()
        return data

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
                           """)
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
        return_value = [row[0] for row in cur]
        con.close()
        return return_value

    def get_items_out(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM OutItems")
        return_value = [row[0] for row in cur]
        con.close()
        return return_value

    def get_contacts(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM Contacts")
        return_value = [row[0] for row in cur]
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
                           """)
            return_value = [[row[0], row[1], row[2], row[3]] for row in cur]
        except sqlite3.OperationalError:
            return_value = 1
        finally:
            con.close()
        return return_value


# передача и получение данных посредством веб-сервиса

class SoapRequests:

    def __init__(self, settings):
        self.settings = settings

    def _soap_service_factory(self):
        try:
            client = Client(self.settings['URL'],
                            username=self.settings['Login'],
                            password=base64.standard_b64decode(
                                    self.settings['Pass'])
                            )
        except WebFault:
            return -1
        return 0, client.service[0], client.factory

    def send_soap_data(self, data, to_callback, no_multi = False):
        """функция передает данные сервису 1С (веб-сервису)

        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        # data = self.prepare_send_data()

        def get_data():
            self._get_soap_data(to_callback, no_multi)

        if len(data) == 0:
            get_data()
            return 0
        act, remote_functions, remote_types = self._soap_service_factory()
        if act == -1:
            return -1

        def do_remote_action(arg):
            return remote_functions.Frompy21c(arg)

        remote_data = remote_types.create('ns1:arr')
        for data_res in data:
            remote_data.data.append(remote_types.create('ns1:arr'))
            remote_data.data[len(remote_data.data)-1].data = data_res
        try:
            if no_multi:
                do_remote_action(remote_data)
                get_data()
            else:
                p = Pool(processes=6)
                remote_result = p.map_async(do_remote_action,
                                            (remote_data,), callback=get_data)
                remote_result.wait()
                p.close()
                p.join()
        except WebFault:
            return -1
        # if remote_result[0] == 'Success':
        #     return 'Success'
            # self.recreate_docs()
        return 0

    def _get_soap_data(self, to_callback, no_multi=False):
        """функция получает от сервиса 1С (веб-сервиса) данные

        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        res_data = []
        act, remote_functions, remote_types = self._soap_service_factory()
        if act == -1:
            return -1

        def do_remote_action_(arg):
            return_val = remote_functions.From1c2py(arg).data
            return return_val

        try:
            send_names = ['in_items',
                          'out_items',
                          'contacts',
                          'pockets',
                          'credits']
            if no_multi:
                results = []
                for sn in send_names:
                    results.append(do_remote_action_(sn))
                to_callback(results)
            else:
                p = Pool(processes=1)
                # results = p.map_async(do_remote_action_, send_names,
                #                       callback=to_callback)
                # results.wait()
                for sn in send_names:
                    results = p.apply_async(do_remote_action_, sn,
                                            callback=to_callback[sn])
                    results.wait()

                # results = p.map(do_remote_action_, send_names)
                # to_callback(results)
                p.close()
                p.join()
            # res_data = [res.data for res in results]
            # self.in_items = remote_functions.From1c2py('in_items').data
            # self.out_items = remote_functions.From1c2py('out_items').data
            # self.contacts = remote_functions.From1c2py('contacts').data
            # pockets_data = remote_functions.From1c2py('pockets')
            # for pocket_data in pockets_data.data:
            #     self.set_pocket(*pocket_data.data)
            # credits_data = remote_functions.From1c2py('credits')
            # for credit_data in credits_data.data:
            #     self.set_credit(*credit_data.data)
        except WebFault:
            return -1
        # self.recreate_refs()
        return res_data
