# coding: utf-8


"""
Классы, описывающие кошельки и их поведение
"""
import base64
from threading import Thread
import PocketDB
from suds import WebFault


class Decor(object):

    @staticmethod
    def put_to_pool(func):
        def wrapper(*args):
            #print 'added', func.__name__
            th = Thread(target=func, args=args)
            th.start()
            th.join()
        return wrapper


class OnePocket:
    """Один кошелек со своей валютой и баллансом"""
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
    """Один кредит со своими валютой, контактом и баллансом"""
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
        self.db = PocketDB.PocketsDB(db_name)
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
        self.settings = {'URL': '', 'Login': '', 'Pass': ''}
        # self.parsing = False

    @Decor.put_to_pool
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

    @Decor.put_to_pool
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
        self.db.recreate_refs(self)
        self.db.recreate_docs()

    def fill_from_db(self):
        """
        Заполняем объект класса из базы данных
        """
        self.get_settings()
        # кошельки:
        for data in self.db.get_pockets():
            self.set_pocket(*data)
        # статьи доходов:
        self.in_items = self.db.get_items_in()
        # статьи расходов:
        self.out_items = self.db.get_items_out()
        # контакты:
        self.contacts = self.db.get_contacts()
        # кредиты:
        for data in self.db.get_credits():
            self.set_credit(*data)

    def action_in(self, pocket, item, summ, amount=0, comment=''):
        """
        доходы
        в кошелек по статье на сумму
        """
        if type(summ) != float and type(summ) != int:
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if tpc.name == pocket:
                    pc = tpc
                    break
            else:
                allright = False
        if not allright:
            return 1
        pc.balance += summ
        self.db.upd_pocket_balance(pc.name, pc.balance)
        self.db.action_in(pc.name, item, summ, amount, comment)
        return 0

    def action_out(self, pocket, item, summ, amount=0, comment=''):
        """
        расходы
        из кошелька по статье на сумму за количество
        """
        if type(summ) != float and type(summ) != int:
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if tpc.name == pocket:
                    pc = tpc
                    break
            else:
                allright = False
        if not allright:
            return 1
        pc.balance -= summ
        self.db.upd_pocket_balance(pc.name, pc.balance)
        self.db.action_out(pc.name, item, summ, amount, comment)

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
                if tpc.name == pocketin:
                    pcin = tpc
                    break
            else:
                allright = False
        if not allright:
            return 1
        pcout.balance -= summ
        pcin.balance += summ
        self.db.upd_pocket_balance(pcin.name, pcin.balance)
        self.db.upd_pocket_balance(pcout.name, pcout.balance)
        self.db.action_between(pcout.name, pcin.name, summ, comment)

    def action_exchange(self, pocketout, pocketin, summout, summin, coment=''):
        """
        обмен валюты
        из кошелька в кошелек сумма расхода, сумма прихода
        """
        summout_type = type(summout) != float and type(summout) != int
        summin_type = type(summin) != float and type(summin) != int
        if summout_type or summin_type:
            return 1
        allright = True
        if isinstance(pocketin, OnePocket):
            pcin = pocketin
        elif type(pocketin) == str:
            for tpc in self.pockets:
                if tpc.name == pocketin:
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

        self.db.upd_pocket_balance(pcin.name, pcin.balance)
        self.db.upd_pocket_balance(pcout.name, pcout.balance)
        self.db.action_exchange(pcout.name, pcin.name, summout, summin, coment)

    def action_credit1_in(self, pocket, credit, summ, addit_summ=0, comment=''):
        """
        мы взяли в долг
        в кошелек по кредиту у контакта сумму
        """
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != float and type(addit_summ) != int):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if tpc.name == pocket:
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
        cr.balance -= summ
        pc.balance += (summ - addit_summ)
        self.db.upd_pocket_balance(pc.name, pc.balance)
        self.db.upd_credit_balance(cr.name, cr.balance)
        self.db.action_credit1_in(pc.name, cr.name, summ, addit_summ, comment)

    def action_credit2_in(self, pocket, credit, summ, addit_summ, comment=''):
        """
        нам вернули долг
        в кошелек по кредиту от контакта сумму
        """
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != float and type(addit_summ) != int):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if tpc.name == pocket:
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
        cr.balance -= summ
        pc.balance += summ
        self.db.upd_pocket_balance(pc.name, pc.balance)
        self.db.upd_credit_balance(cr.name, cr.balance)
        self.db.action_credit2_in(pc.name, cr.name, summ, addit_summ, comment)

    def action_credit1_out(self, pocket, credit,
                           summ, addit_summ, percent_sum,
                           comment=''):
        """
        мы вернули долг
        из кошелька по кредиту контакту сумму
        """
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != int and type(percent_sum) != int
            or type(addit_summ) != float and type(percent_sum) != float):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if tpc.name == pocket:
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
        self.db.upd_pocket_balance(pc.name, pc.balance)
        self.db.upd_credit_balance(cr.name, cr.balance)
        self.db.action_credit1_out(pc.name, cr.name, summ, addit_summ,
                                   percent_sum, comment)

    def action_credit2_out(self, pocket, credit, summ, addit_summ, comment=''):
        """
        мы дали в долг
        из кошелька по кредиту контакту сумму
        """
        if (type(summ) != float and type(summ) != int
            or type(addit_summ) != float and type(addit_summ) != int):
            return 1
        allright = True
        if isinstance(pocket, OnePocket):
            pc = pocket
        elif type(pocket) == str:
            for tpc in self.pockets:
                if tpc.name == pocket:
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
        self.db.upd_pocket_balance(pc.name, pc.balance)
        self.db.upd_credit_balance(cr.name, cr.balance)
        self.db.action_credit2_out(pc.name, cr.name, summ, addit_summ, comment)

    # хранение настроек

    def set_settings(self, url_wsdl, login, password, pass_in_64=False):
        if pass_in_64:
            pass_value = password
        else:
            pass_value = base64.standard_b64encode(password)
        self.settings['URL'] = url_wsdl
        self.settings['Login'] = login
        self.settings['Pass'] = pass_value
        self.db.reset_settings(url_wsdl, login, pass_value)

    def get_settings(self):
        data = self.db.get_settings()
        if data != -1:
            self.settings['URL'] = data[0]
            self.settings['Login'] = data[1]
            self.settings['Pass'] = data[2]

    def parse_soap_income(self, data):
        res_data = [res for res in data]
        self.in_items = res_data[0]
        self.out_items = res_data[1]
        self.contacts = res_data[2]
        for pocket_data in res_data[3]:
            self.set_pocket(*pocket_data.data)
        for credit_data in res_data[4]:
            self.set_credit(*credit_data.data)
        self.create_db()
        # self.parsing = False

    def parse_soap_income_in_items(self, data):
        self.in_items = data

    def parse_soap_income_out_items(self, data):
        self.out_items = data

    def parse_soap_income_contacts(self, data):
        self.contacts = data

    def parse_soap_income_pockets(self, data):
        for pocket_data in data:
            self.set_pocket(*pocket_data.data)

    def parse_soap_income_credits(self, data):
        for credit_data in data:
            self.set_credit(*credit_data.data)

    def parsing_functions(self):
        return {'in_items': self.parse_soap_income_in_items,
                'out_items': self.parse_soap_income_out_items,
                'contacts': self.parse_soap_income_contacts,
                'pockets': self.parse_soap_income_pockets,
                'credits': self.parse_soap_income_credits}

    def soap_data(self):
        if hasattr(self, 'settings'):
            # self.parsing = True
            data = self.db.prepare_send_data()
            self.get_settings()
            sr = PocketDB.SoapRequests(self.settings)
            sr.send_soap_data(data, self.parsing_functions())



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

