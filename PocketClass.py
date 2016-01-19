# coding: utf-8


"""
Классы, описывающие кошельки и их поведение
"""
import sqlite3
from suds import WebFault
from suds.client import Client


SOAP_ACTION = "http://money.kter.ru#kter_ru:Android"
SOAP_METHOD_NAME = "Android"
defaultURL = "http://myhost/money/ws/ws1.1cws"
NAMESPACE = "http://money.kter.ru"
SOAP_ACTION2 = "http://money.kter.ru#kter_ru:Android_out1"
SOAP_METHOD_NAME2 = "Android_out1"
SOAP_ACTION3 = "http://money.kter.ru#kter_ru:Android_out2"
SOAP_METHOD_NAME3 = "Android_out2"
SOAP_ACTION4 = "http://money.kter.ru#kter_ru:Android_out3"
SOAP_METHOD_NAME4 = "Android_out3"
SOAP_property_actions = "actions"
SOAP_property_what = "what"
SOAP_property_param = "param"
SOAP_Auth = "Authorization"


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

    def close_db(self):
        """
        Требуется вызывать при завершении существования объекта в
        дереве жизни приложения
        """
        self.con.close()

    def set_pocket(self, name, currency, balance=0):
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

    def create_db(self):
        """
        (пере)создание базы данных
        вызывается только? при синхронизации и первичной инициации объекта
        """
        self.cur.executescript("""
            DROP TABLE IF EXISTS Pockets;
--кошельки
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
--последовательность
            CREATE TABLE IF NOT EXISTS Actions(Id INT PRIMARY KEY,
                                               DateTime VARCHAR(18),
                                               Action_name INT,
                                               ActionId INT);
--доходы 1
            CREATE TABLE IF NOT EXISTS InAction(Id INT PRIMARY KEY,
                                                Action_name INT,
                                                Pocket VARCHAR(50),
                                                Item VARCHAR(50),
                                                Summ FLOAT,
                                                Amount FLOAT,
                                                Comment TEXT);
--расходы 2
            CREATE TABLE IF NOT EXISTS OutAction(Id INT PRIMARY KEY,
                                                 Action_name INT,
                                                 Pocket VARCHAR(50),
                                                 Item VARCHAR(50),
                                                 Summ FLOAT,
                                                 Amount FLOAT,
                                                 Comment TEXT);
--перемещения 3
            CREATE TABLE IF NOT EXISTS BetweenAction(Id INT PRIMARY KEY,
                                                     Action_name INT,
                                                     PocketOut VARCHAR(50),
                                                     PocketIn VARCHAR(50),
                                                     Summ FLOAT,
                                                     Comment TEXT);
--обмен валют 4
            CREATE TABLE IF NOT EXISTS ExchangeAction(Id INT PRIMARY KEY,
                                                      Action_name INT,
                                                      PocketOut VARCHAR(50),
                                                      PocketIn VARCHAR(50),
                                                      SummOut FLOAT,
                                                      SummIn FLOAT,
                                                      Comment TEXT);
--мы взяли в долг 5
            CREATE TABLE IF NOT EXISTS Сredit1InAction(Id INT PRIMARY KEY,
                                                       Action_name INT,
                                                       Pocket VARCHAR(50),
                                                       Credit VARCHAR(50),
                                                       Summ FLOAT,
                                                       Comment TEXT);
--мы вернули долг 6
            CREATE TABLE IF NOT EXISTS Сredit1OutAction(Id INT PRIMARY KEY,
                                                        Action_name INT,
                                                        Pocket VARCHAR(50),
                                                        Credit VARCHAR(50),
                                                        Summ FLOAT,
                                                        Comment TEXT);
--нам вернули долг 7
            CREATE TABLE IF NOT EXISTS Сredit2InAction(Id INT PRIMARY KEY,
                                                       Action_name INT,
                                                       Pocket VARCHAR(50),
                                                       Credit VARCHAR(50),
                                                       Summ FLOAT,
                                                       Comment TEXT);
--мы дали в долг 8
            CREATE TABLE IF NOT EXISTS Сredit2OutAction(Id INT PRIMARY KEY,
                                                        Action_name INT,
                                                        Pocket VARCHAR(50),
                                                        Credit VARCHAR(50),
                                                        Summ FLOAT,
                                                        Comment TEXT);
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
        # кошельки:
        self.cur.executescript("""
                    SELECT P.Name,
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
        self.cur.executescript("""
                    SELECT C.Name,
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

    def action_credit1_in(self, pocket, credit, summ, comment=''):
        """
        мы взяли в долг
        в кошелек по кредиту у контакта сумму
        """
        action_name = 5
        if summ != float and type(summ) != int:
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
            "INSERT INTO Сredit1InAction VALUES (NULL, ?, ?, ?, ?, ?)",
            (action_name, pc.name, cr.name, summ, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_credit1_out(self, pocket, credit, summ, comment=''):
        """
        мы вернули долг
        из кошелька по кредиту контакту сумму
        """
        action_name = 6
        if summ != float and type(summ) != int:
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
        pc.balance -= summ
        self.__upd_db_balance__(pc)
        self.__upd_db_credit_balance__(cr)
        self.cur.execute(
            "INSERT INTO Сredit1OutAction VALUES (NULL, ?, ?, ?, ?, ?)",
            (action_name, pc.name, cr.name, summ, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    def action_credit2_in(self, pocket, credit, summ, comment=''):
        """
        нам вернули долг
        в кошелек по кредиту от контакта сумму
        """
        action_name = 7
        if summ != float and type(summ) != int:
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

    def action_credit2_out(self, pocket, credit, summ, comment=''):
        """
        мы дали в долг
        из кошелька по кредиту контакту сумму
        """
        action_name = 8
        if summ != float and type(summ) != int:
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
        pc.balance -= summ
        self.__upd_db_balance__(pc)
        self.__upd_db_credit_balance__(cr)
        self.cur.execute(
            "INSERT INTO Сredit2OutAction VALUES (NULL, ?, ?, ?, ?, ?)",
            (action_name, pc.name, cr.name, summ, comment)
        )
        lid = self.cur.lastrowid
        self.__add_db_action__(action_name, lid)
        self.con.commit()
        return 0

    # todo передача и получение данных посредством веб-сервиса
    def Get_Soap_Service_Data(self, remote_param=''):
        """функция получает от сервиса 1С (веб-сервиса) данные

        :param remote_param:
            строка с числовым значением
                1: кошельки
                2: статьи дохода
                3: статьи расхода
                4: остатки
                пусто, если данные для нового функционала
        :return: -1 в случае неудачного запроса к сервису, иначе 0.
        """
        rslt = 0
        client = Client("http://money.kter.ru/money/ws/ws1.1cws?wsdl", username = 'ktu', password = '2132644')
        data = client.service[0].Android_out2()

        SoapObject Request = new SoapObject(NAMESPACE, SOAP_METHOD_NAME2);

        // here you form body of your SOAP-request
        Request.addProperty(MainContext.getString(R.string.SOAP_property_what), remote_param);

        SoapSerializationEnvelope soapEnvelope = new SoapSerializationEnvelope(SoapEnvelope.VER11);
        //soapEnvelope.dotNet = true;

        soapEnvelope.setAddAdornments(false);
        soapEnvelope.encodingStyle = SoapSerializationEnvelope.ENC;
        soapEnvelope.env = SoapSerializationEnvelope.ENV;
        soapEnvelope.implicitTypes = true;


        List<HeaderProperty> headerPropertyList = new ArrayList<HeaderProperty>();
        headerPropertyList.add(new HeaderProperty(MainContext.getString(R.string.SOAP_Auth), Form_Header()));

        soapEnvelope.setOutputSoapObject(Request);

        HttpTransportSE aht = new HttpTransportSE(URL); // перед вызовом URL обязательно он должен быть задан. а задается он функцией Form_Header()
//        aht.debug = true;

        try {
            aht.call(SOAP_ACTION2, soapEnvelope, headerPropertyList);
            SoapPrimitive resultString = (SoapPrimitive) soapEnvelope.getResponse();

            switch (remote_param) {
                case 1:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_purses));
                    break;
                case 2:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_initems));
                    break;
                case 3:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_outitems));
                    break;
                case 4:
                    writeDataFile(resultString.getValue().toString(), MainContext.getString(R.string.FileName_pursesbalances));
                    break;
            }

        } catch (Exception e) {
            rslt = -1;
        }
        return rslt;
    }

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

    # todo хранение настроек