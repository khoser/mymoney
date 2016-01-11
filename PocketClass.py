# coding: utf-8


"""
Классы, описывающие кошельки и их поведение
"""


class OnePocket:
    """Один кошелек со своей волютой и баллансом"""
    def __init__(self, name, currency, balance=0):
        self.name = name
        self.currency = currency
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
        self.set_balance(balance)

    def set_balance(self, balance):
        # изменение баланса
        if type(balance) == float or int:
            self.balance = balance
        elif type(balance) == str:
            self.balance = float(balance.replace(" ", "").replace(",", "."))

    def get_info(self):
        # вывод информации в виде строки
        return "%s (%s): %s %s" % (self.name, self.contact, self.balance, self.currency)


class Pockets:
    """Список кошельков"""
    # common = 0 #для экспериментов

    def __init__(self):
        self.pockets = []
        self.out_items = []
        self.in_items = []
        self.contacts = []
        self.credits = []

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


# class PocketsActions(Pockets): # для чего? а наследуюсь?

    def create_db(self):
        # TODO создание базы данных
        import sqlite3

        con = sqlite3.connect('MyMoney.db')
        cur = con.cursor()
        cur.executescript("""
            DROP TABLE IF EXISTS Pocket;
            CREATE TABLE Pocket(Name TEXT, Currency TEXT);
            DROP TABLE IF EXISTS Balance;
            CREATE TABLE Balance(Pocket TEXT, Balance FLOAT);
            DROP TABLE IF EXISTS CreditBalance;
            CREATE TABLE CreditBalance(CreditName TEXT, Balance FLOAT);
            DROP TABLE IF EXISTS OutItems;
            CREATE TABLE OutItems(Item TEXT);
            DROP TABLE IF EXISTS InItems;
            CREATE TABLE InItems(Item TEXT);
            DROP TABLE IF EXISTS Contacts;
            CREATE TABLE Contacts(ContactName TEXT);
            DROP TABLE IF EXISTS Credits;
            CREATE TABLE Credits(CreditName TEXT, ContactName TEXT, Currency TEXT);
            CREATE TABLE IF NOT EXISTS Actions(Id INT, DateTime TEXT, Action_name INT, ActionId INT);
            CREATE TABLE IF NOT EXISTS InAction(
                Id INT, Action_name INT, Pocket TEXT, Item TEXT, Sum FLOAT, Amount FLOAT, Comment TEXT);
            CREATE TABLE IF NOT EXISTS OutAction(
                Id INT, Action_name INT, Pocket TEXT, Item TEXT, Sum FLOAT, Amount FLOAT, Comment TEXT);
            CREATE TABLE IF NOT EXISTS BetweenAction(
                Id INT, Action_name INT, PocketOut TEXT, PocketIn TEXT, Sum FLOAT, Comment TEXT);
            CREATE TABLE IF NOT EXISTS ExchangeAction(
                Id INT, Action_name INT, PocketOut TEXT, PocketIn TEXT, SumOut FLOAT, SumIn FLOAT, Comment TEXT);
            CREATE TABLE IF NOT EXISTS СreditInAction(
                Id INT, Action_name INT, Pocket TEXT, CreditName TEXT, Sum FLOAT, Comment TEXT);
            """)
        for pocket in self.pockets:
            cur.execute("INSERT INTO Pocket(Name, Currency) VALUES (?, ?)", (pocket.name, pocket.currency))
            cur.execute("INSERT INTO Balance(Pocket, Balance) VALUES (?, ?)", (pocket.name, pocket.balance))
        for x in self.out_items:
            cur.execute("INSERT INTO OutItems(Item) VALUES (?)", (x,))
        for x in self.in_items:
            cur.execute("INSERT INTO InItems(Item) VALUES (?)", (x,))
        for x in self.contacts:
            cur.execute("INSERT INTO Contacts(ContactName) VALUES (?)", (x,))
        for credit in self.credits:
            cur.execute("INSERT INTO Credits(CreditName, ContactName, Currency) VALUES (?, ?, ?)", (credit.name, credit.contact, credit.currency))
            cur.execute("INSERT INTO CreditBalance(CreditName, Balance) VALUES (?, ?)", (credit.name, credit.balance))

        con.commit()
        con.close()

    def fill_pockets(self):
        # Заполняем кошельки из базы данных
        # TODO Подключение к базе данных, чтение инфы о кошельках и остатках в объект класса Pockets
        pass

    def fill_pockets_from_file(self):
        # Заполняем кошельки из файла
        # TODO чтение инфы о кошельках и остатках в объект класса Pockets из файла/ов
        # формат файла "файл кошельков": название кошелька/валюта/баланс
        import pickle
        myfile = file(r"файл кошельков") #todo правильный путь к файлу
        loadedlist = pickle.load(myfile)
        myfile.close()
        for i in loadedlist:
            self.add_pocket(*i.split("/"))

    # todo операции