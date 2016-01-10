# coding: utf-8


"""
Классы, описывающие кошельки и их поведение
"""


class OnePocket:
    """Один кошелек со своей волютой и баллансом"""
    def __init__(self, name, currency, balance=0):
        self.name = name
        self.currency = currency
        if type(balance) == float or int:
            self.balance = balance
        elif type(balance) == str:
            self.balance = float(balance.replace(" ","").replace(",","."))

    def get_info(self):
        #вывод информации в виде строки
        return "%s: %s %s" % (self.name,self.balance,self.currency)


class Pockets:
    """Список кошельков"""
    common = 0 #для экспериментов

    def __init__(self):
        self.pockets = []
        self.common=0

    def add_pocket(self, name, currency, balance=0):
        #добавление еще одного кошелька в список
        self.pockets.append(OnePocket(name, currency, balance))
        self.common+=1

    def get_info(self):
        #вывод информации в виде строки
        res = ""
        for i in self.pockets:
            res += i.get_info() + "\n"
        return res


#class PocketsActions(Pockets): # для чего? а наследуюсь?

    def fill_pockets(self):
        #Заполняем кошельки из базы данных
        #TODO Подключение к базе данных, чтение инфы о кошельках и остатках в объект класса Pockets
        pass

    def fill_pockets_from_file(self):
        #Заполняем кошельки из файла
        #TODO чтение инфы о кошельках и остатках в объект класса Pockets из файла/ов
        #формат файла "файл кошельков": название кошелька/валюта/баланс
        import pickle
        myfile = file(r"файл кошельков") #todo правильный путь к файлу
        loadedlist = pickle.load(myfile)
        myfile.close()
        for i in loadedlist:
            self.add_pocket(*i.split("/"))
