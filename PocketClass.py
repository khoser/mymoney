# coding: utf-8


"""
Классы, описывающие кошельки и их поведение
"""
import sqlite3
import base64
from suds import WebFault
from suds.client import Client


class OnePocket:
    """Один кошелек со своей волютой и баллансом"""
    def __init__(self, name, currency, balance=0):
        self.name = name
        self.currency = currency
        self.balance = 0
        self.set_balance(balance)

    def set_balance(self, balance):
        # изменение баланса
        if type(balance) == float or int:
            self.balance = balance
        elif type(balance) == str:
            self.balance = float(balance.replace(" ", "").replace(",", "."))

    def get_info(self):
        # вывод информации в виде строки
        return "%s: %s %s" % (self.name, self.balance, self.currency)


class OneCredit:
    """Один кошелек со своей волютой и баллансом"""
    def __init__(self, name, currency, contact, balance=0):
        self.name = name
        self.currency = currency
        self.contact = contact
        self.balance = balance
        self.set_balance(balance)

    def set_balance(self, balance):
        # изменение баланса
        if type(balance) == float or int:
            self.balance = balance
        elif type(balance) == str:
            self.balance = float(balance.replace(" ", "").replace(",", "."))

    def get_info(self):
        # вывод информации в виде строки
        return "%s (%s): %s %s" % (self.name,
                                   self.contact,
                                   self.balance,
                                   self.currency)


class Pockets:
    """
    Список кошельков и их взаимодействия
    """
    def __init__(self, db_name='MyMoney.db'):
        self.pockets = []
        self.out_items = []
        self.in_items = []
        self.contacts = []
        self.credits = []
        self.con = sqlite3.connect(db_name)
        self.cur = self.con.cursor()
        self.actions_names = {
            1: 'In',
            2: 'Out',
            3: 'Betwean',
            4: 'Exchange',
            5: 'Credit1In',
            6: 'Credit1Out',
            7: 'Credit2In',
            8: 'Credit2Out',
        }
        self.settings = {}

    def close_db(self):
        """
        Требуется вызывать при завершении существования объекта в
        дереве жизни приложения
        """
        self.con.close()

    def set_pocket(self, name, currency='', balance=0):
        # добавление еще одного кошелька в список
        # или обновление баланса существующего кошелька
        exist = False
        for x in self.pockets:
            if name == x.name:
                exist = True
                x.set_balance(balance)
        if not exist:
            self.pockets.append(OnePocket(name, currency, balance))

    def set_credit(self, name, currency, contact, balance=0):
        # добавление еще одного кредита в список
        # или обновление баланса существующего кредита
        exist = False
        for x in self.credits:
            if (name == x.name) & (contact == x.contact):
                exist = True
                x.set_balance(balance)
        if not exist:
            self.credits.append(OneCredit(name, currency, contact, balance))

    def get_info(self):
        # вывод информации в виде строки
        res = ""
        for i in self.pockets:
            res += i.get_info()
            if self.pockets[-1] != i:
                res += "\n"
        if (len(self.pockets) > 0) & (len(self.contacts) > 0):
            res += "\n"
        for i in self.credits:
            res += i.get_info()
            if self.credits[-1] != i:
                res += "\n"
        return res

    def get_one(self, obj_name):
        # возвращает кошелек (кредит) по наименованию
        for i in self.pockets:
            if i.name == obj_name:
                return i
        for i in self.credits:
            if i.name == obj_name:
                return i

    def create_db(self):
        """
        (пере)создание базы данных
        вызывается только? при синхронизации и первичной инициации объекта
        """
        self.recreate_refs()
        self.recreate_docs()

    def recreate_docs(self):
        """
        (пере)создание базы данных
        вызывается только? при синхронизации и первичной инициации объекта
        """
        self.cur.executescript("""
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
        self.con.commit()

    def recreate_refs(self):
        self.cur.executescript("""
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
        self.con.commit()
        for pocket in self.pockets:
            self.cur.execute(
                            "INSERT INTO Pockets VALUES (?, ?)",
                            (
                                pocket.name,
                                pocket.currency
                            )
                        )
            self.cur.execute(
                            "INSERT INTO Balances VALUES (?, ?)",
                            (
                                pocket.name,
                                pocket.balance
                            )
                        )
        for x in self.out_items:
            self.cur.execute("INSERT INTO OutItems VALUES (?)", (x,))
        for x in self.in_items:
            self.cur.execute("INSERT INTO InItems VALUES (?)", (x,))
        for x in self.contacts:
            self.cur.execute("INSERT INTO Contacts VALUES (?)", (x,))
        for credit in self.credits:
            self.cur.execute(
                            "INSERT INTO Credits VALUES (?, ?, ?)",
                            (
                                credit.name,
                                credit.contact,
                                credit.currency
                            )
                        )
            self.cur.execute(
                            "INSERT INTO CreditBalances VALUES (?, ?)",
                            (
                                credit.name,
                                credit.balance
                            )
                        )
        self.con.commit()
        #con.close()

    def fill_from_db(self):
        """
        Заполняем объект класса из базы данных
        """
        self.get_setiings()
        # кошельки:
        self.cur.execute("""
                    SELECT
                           P.Name,
                           P.Currency,
                           B.Balance
                    FROM Pockets AS P
                    LEFT JOIN Balances AS B ON B.Pocket = P.Name
                    """)
        for row in self.cur:
            self.set_pocket(row[0],row[1],row[2])
        # статьи доходов:
        self.cur.execute("SELECT * FROM InItems")
        for row in self.cur:
            self.in_items.append(row[0])
        # статьи расходов:
        self.cur.execute("SELECT * FROM OutItems")
        for row in self.cur:
            self.out_items.append(row[0])
        # контакты:
        self.cur.execute("SELECT * FROM Contacts")
        for row in self.cur:
            self.contacts.append(row[0])
        # кредиты:
        self.cur.execute("""
                    SELECT
                           C.Name,
                           C.Currency,
                           C.Contact,
                           B.Balance
                    FROM Credits AS C
                    LEFT JOIN CreditBalances AS B ON B.Credit = C.Name
                    """)
        for row in self.cur:
            self.set_credit(row[0],row[1],row[2],row[3])

    def __add_db_action__(self, action_name, action_id):
        self.cur.execute(
                """INSERT INTO Actions
                VALUES (NULL, datetime('now', 'localtime'), ?, ?)
                """,
                (action_name, action_id)
        )

    def __upd_db_balance__(self, pocket):
        self.cur.execute(
                "UPDATE Balances SET Balance = ? WHERE Pocket = ?",
                (pocket.name, pocket.balance)
        )

    def __upd_db_credit_balance__(self, credit):
        self.cur.execute(
                "UPDATE CreditBalances SET Balance = ? WHERE Credit = ?",
                (credit.name, credit.balance)
        )

    def action_in(self, pocket, item, summ, amount = 0, comment=''):
        """
        доходы
        в кошелек по статье на сумму
        """
        action_name = 1
        if type(summ) != float and type(summ) != int:
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if (tpc.name == pocket):
                    pc = tpc
                    break
            else:
                allright = False
        if not allright:
            return 1
        pc.balance += summ
        self.__upd_db_balance__(pc)
        self.cur.execute(
            "INSERT INTO InAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pc.name, item, summ, amount, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_out(self, pocket, item, summ, amount = 0, comment=''):
        """
        расходы
        из кошелька по статье на сумму за количество
        """
        action_name = 2
        if type(summ) != float and type(summ) != int:
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if (tpc.name == pocket):
                    pc = tpc
                    break
            else:
                allright = False
        if not allright:
            return 1
        pc.balance -= summ
        self.__upd_db_balance__(pc)
        self.cur.execute(
            "INSERT INTO OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pc.name, item, summ, amount, comment)
        )
        self.con.commit()
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_between(self, pocketout, pocketin, summ, comment=''):
        """
        перемещение
        из кошелька в кошелек сумму
        """
        action_name = 3
        if type(summ) != float and type(summ) != int:
            return 1
        allright = True
        if isinstance(pocketout, OnePocket):
            pcout = pocketout
        elif type(pocketout) == str:
            for tpc in self.pockets:
                if tpc.name == pocketout:
                    pcout = tpc
                    break
            else:
                allright = False
        if isinstance(pocketin, OnePocket):
            pcin = pocketin
        elif type(pocketin) == str:
            for tpc in self.pockets:
                if (tpc.name == pocketin):
                    pcin = tpc
                    break
            else:
                allright = False
        if not allright:
            return 1
        pcout.balance -= summ
        pcin.balance += summ
        self.__upd_db_balance__(pcin)
        self.__upd_db_balance__(pcout)
        self.cur.execute(
            "INSERT INTO BetweenAction VALUES (NULL, ?, ?, ?, ?, ?)",
            (action_name, pcout.name, pcin.name, summ, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_exchange(self, pocketout, pocketin, summout, summin, coment=''):
        """
        обмен валюты
        из кошелька в кошелек сумма расхода, сумма прихода
        """
        action_name = 4
        summout_type = type(summout) != float and type(summout) != int
        summin_type = type(summin) != float and type(summin) != int
        if summout_type or summin_type:
            return 1
        allright = True
        if isinstance(pocketin, OnePocket):
            pcin = pocketin
        elif type(pocketin) == str:
            for tpc in self.pockets:
                if (tpc.name == pocketin):
                    pcin = tpc
                    break
            else:
                allright = False
        if isinstance(pocketout, OnePocket):
            pcout = pocketout
        elif type(pocketout) == str:
            for tpc in self.pockets:
                if tpc.name == pocketout:
                    pcout = tpc
                    break
            else:
                allright = False
        if not allright:
            return 1
        pcout.balance -= summout
        pcin.balance += summin
        self.__upd_db_balance__(pcin)
        self.__upd_db_balance__(pcout)
        self.cur.execute(
            "INSERT INTO ExchangeAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pcout.name, pcin.name, summout, summin, coment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_credit1_in(self, pocket, credit, summ, addit_summ, comment=''):
        """
        мы взяли в долг
        в кошелек по кредиту у контакта сумму
        """
        action_name = 5
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != float and type(addit_summ) != int):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if (tpc.name == pocket):
                    pc = tpc
                    break
            else:
                allright = False
        if isinstance(credit, OneCredit):
            cr = credit
        elif (type(credit) == str):
            for tcr in self.credits:
                if (tcr.name == credit):
                    cr = tcr
                    break
            else:
                allright = False
        if not allright:
            return 1
        cr.balance -= summ
        pc.balance += (summ - addit_summ)
        self.__upd_db_balance__(pc)
        self.__upd_db_credit_balance__(cr)
        self.cur.execute(
            "INSERT INTO Сredit1InAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pc.name, cr.name, summ, addit_summ, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_credit2_in(self, pocket, credit, summ, addit_summ, comment=''):
        """
        нам вернули долг
        в кошелек по кредиту от контакта сумму
        """
        action_name = 7
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != float and type(addit_summ) != int):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if (tpc.name == pocket):
                    pc = tpc
                    break
            else:
                allright = False
        if isinstance(credit, OneCredit):
            cr = credit
        elif (type(credit) == str):
            for tcr in self.credits:
                if (tcr.name == credit):
                    cr = tcr
                    break
            else:
                allright = False
        if not allright:
            return 1
        cr.balance -= summ
        pc.balance += summ
        self.__upd_db_balance__(pc)
        self.__upd_db_credit_balance__(cr)
        self.cur.execute(
            "INSERT INTO Сredit2InAction VALUES (NULL, ?, ?, ?, ?, ?)",
            (action_name, pc.name, cr.name, summ, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_credit1_out(self, pocket, credit,
                           summ, addit_summ, percent_sum,
                           comment=''):
        """
        мы вернули долг
        из кошелька по кредиту контакту сумму
        """
        action_name = 6
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != int and type(percent_sum) != int
            or type(addit_summ) != float and type(percent_sum) != float):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if (tpc.name == pocket):
                    pc = tpc
                    break
            else:
                allright = False
        if isinstance(credit, OneCredit):
            cr = credit
        elif type(credit) == str:
            for tcr in self.credits:
                if tcr.name == credit:
                    cr = tcr
                    break
            else:
                allright = False
        if not allright:
            return 1
        cr.balance += summ
        pc.balance -= (summ + addit_summ + percent_sum)
        self.__upd_db_balance__(pc)
        self.__upd_db_credit_balance__(cr)
        self.cur.execute(
            "INSERT INTO Сredit1OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
            (action_name, pc.name, cr.name,
             summ, addit_summ, percent_sum, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_credit2_out(self, pocket, credit, summ, addit_summ, comment=''):
        """
        мы дали в долг
        из кошелька по кредиту контакту сумму
        """
        action_name = 8
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != float and type(addit_summ) != int):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if (tpc.name == pocket):
                    pc = tpc
                    break
            else:
                allright = False
        if isinstance(credit, OneCredit):
            cr = credit
        elif type(credit) == str:
            for tcr in self.credits:
                if tcr.name == credit:
                    cr = tcr
                    break
            else:
                allright = False
        if not allright:
            return 1
        cr.balance += summ
        pc.balance -= (summ + addit_summ)
        self.__upd_db_balance__(pc)
        self.__upd_db_credit_balance__(cr)
        self.cur.execute(
            "INSERT INTO Сredit2OutAction VALUES (NULL, ?, ?, ?, ?, ?, ?)",
            (action_name, pc.name, cr.name, summ, addit_summ, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    # хранение настроек

    def set_settings(self, url_wsdl, login, password, pass_in_64=False):
        if pass_in_64:
            pass_value = password
        else:
            pass_value = base64.standard_b64encode(password)
        self.cur.executescript("""
            DROP
                TABLE IF EXISTS Settings;
            CREATE TABLE Settings(OwnerName VARCHAR(50),
                                  Url_wsdl VARCHAR(300),
                                  Login VARCHAR(50),
                                  Pass VARCHAR(300));
                                  """)
        self.cur.execute("INSERT INTO Settings VALUES (?, ?, ?, ?)",
                         (1, url_wsdl, login, pass_value))
        self.con.commit()

    def get_setiings(self):
        self.cur.execute("SELECT * FROM Settings")
        for row in self.cur:
            self.settings['URL'] = row[1]
            self.settings['Login'] = row[2]
            self.settings['Pass'] = row[3]
        return 1

    # передача и получение данных посредством веб-сервиса

    def soap_service_factory(self):
        self.get_setiings()
        try:
            client = Client(self.settings['URL'],
                            username=self.settings['Login'],
                            password=base64.standard_b64decode(
                                    self.settings['Pass'])
                            )
        except WebFault:
            return -1
        return 0, client.service[0], client.factory

    def get_all_soap_data(self):
        """функция получает от сервиса 1С (веб-сервиса) данные

        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        act, remote_functions, remote_types = self.soap_service_factory()
        if act == -1:
            return -1
        try:
            self.in_items = remote_functions.From1c2py('in_items').data
            self.out_items = remote_functions.From1c2py('out_items').data
            self.contacts = remote_functions.From1c2py('contacts').data
            pockets_data = remote_functions.From1c2py('pockets')
            for pocket_data in pockets_data.data:
                self.set_pocket(*pocket_data.data)
            credits_data = remote_functions.From1c2py('credits')
            for credit_data in credits_data.data:
                self.set_credit(*credit_data.data)
        except WebFault:
            return -1
        self.recreate_refs()
        return 0

    def prepare_send_data(self):
        """функция передает данные сервису 1С (веб-сервису)

        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        # готовим данные для отправки
        self.cur.execute("""
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
        data = []
        for row in self.cur:
            values = [self.settings['Login'], self.actions_names[row[1]]]
            for i in xrange(8):
                values.append(row[i+2])
            data.append(values)
        return data

        # todo по кредитам допрасходы и проценты

    def send_soap_data(self):
        """функция передает данные сервису 1С (веб-сервису)

        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        data = self.prepare_send_data()
        act, remote_functions, remote_types = self.soap_service_factory()
        if act == -1:
            return -1
        remote_data = remote_types.create('ns1:arr')
        for data_res in data:
            remote_data.data.append(remote_types.create('ns1:arr'))
            remote_data.data[len(remote_data.data)-1].data = data_res
        try:
            remote_result = remote_functions.Frompy21c(remote_data)
        except WebFault:
            return -1
        if remote_result == 'Success':
            self.recreate_docs()
        return 0

    # TODO если БД не прокатит, то чтение инфы о кошельках и остатках из файлов
    """
    def fill_pockets_from_file(self):
        # Заполняем кошельки из файла
        # формат файла "файл кошельков": название кошелька/валюта/баланс
        # в объект класса Pockets
        import pickle
        myfile = file(r"файл кошельков") #todo правильный путь к файлу
        loadedlist = pickle.load(myfile)
        myfile.close()
        for i in loadedlist:
            self.add_pocket(*i.split("/"))
    """

