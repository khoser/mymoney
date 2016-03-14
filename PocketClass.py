# coding: utf-8


"""
Классы, описывающие кошельки и их поведение
"""
import base64
import PocketDB


class SimpleObject:
    """Один кошелек со своей валютой и баллансом"""
    def __init__(self, name, **kwargs):
        self.__name__ = 'SimpleObject'
        self.name = name
        self.kwargs = {}
        for i in kwargs:
            self.kwargs[i] = kwargs[i]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return unicode(self.name)

    def __bytes__(self):
        return bytes(self.name)

    def get_info(self):
        # вывод информации в виде строки
        kw = ''
        ks = self.kwargs.keys()
        ks.sort()
        for k in ks:
            kw += '                    %s: %s \n' % (k, self.kwargs[k])
        return "%s:\n%s" % (self.name, kw)


class OnePocket(SimpleObject):
    """Один кошелек со своей валютой и баллансом"""
    def __init__(self, name, currency, balance=0, **kwargs):
        SimpleObject.__init__(self, name, **kwargs)
        self.__name__ = 'OnePocket'
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
        kw = ''
        ks = self.kwargs.keys()
        ks.sort()
        for k in ks:
            kw += '                    %s: %s \n' % (k, self.kwargs[k])
        return "%s: %s %s\n%s" % (self.name, self.balance, self.currency, kw)


class OneCredit(OnePocket):
    """Один кредит со своими валютой, контактом и баллансом"""
    def __init__(self, name, currency, contact, balance=0, **kwargs):
        OnePocket.__init__(self, name, currency, balance, **kwargs)
        self.__name__ = 'OneCredit'
        self.contact = contact

    def get_info(self):
        # вывод информации в виде строки
        kw = ''
        ks = self.kwargs.keys()
        ks.sort()
        for k in ks:
            kw += '                    %s: %s \n' % (k, self.kwargs[k])
        return "%s (%s): %s %s\n%s" % (self.name,
                                       self.contact,
                                       self.balance,
                                       self.currency,
                                       kw)


class Pockets:
    """
    Список кошельков и их взаимодействия
    """
    def __init__(self, db_name='MyMoney.db'):
        self.__name__ = 'Pockets'
        self.pockets = []
        self.out_items = []
        self.in_items = []
        self.contacts = []
        self.credits = []
        self.currency = []
        self.simple_objects = {
            'OnePocket': 'OnePocket',
            'OneCredit': 'OneCredit',
            'OneOutItem': 'OneOutItem',
            'OneInItem': 'OneInItem',
            'OneContact': 'OneContact',
            'Currency': 'Currency'
        }
        self.db = PocketDB.PocketsDB(db_name)
        self.actions_names = {
            1: 'In',
            2: 'Out',
            3: 'Between',
            4: 'Exchange',
            5: 'Credit1In',
            6: 'Credit1Out',
            7: 'Credit2In',
            8: 'Credit2Out',
        }
        self.settings = {'URL': '', 'Authorization': ''}
        # self.parsing = False

    def _drop_db(self):
        self.db._drops()

    def set_cur(self, name, **kwargs):
        # добавление валюты в словарь
        so = SimpleObject(name, **kwargs)
        so.__name__ = self.simple_objects['Currency']
        self.currency.append(so)

    def set_pocket(self, name, currency='', balance=0, **kwargs):
        # добавление еще одного кошелька в список
        # или обновление баланса существующего кошелька
        exist = False
        for x in self.pockets:
            if name == x.name:
                exist = True
                x.set_balance(balance)
        if not exist:
            self.pockets.append(OnePocket(name, currency, balance, **kwargs))

    def _drop_pocket(self, name):
        # удаление кошелька из списка
        for i in range(len(self.pockets)):
            if self.pockets[i].name == name:
                self.pockets.remove(self.pockets[i])

    def _drop_credit(self, name):
        # удаление кредита из списка
        for i in range(len(self.credits)):
            if self.credits[i].name == name:
                self.credits.remove(self.credits[i])

    def set_credit(self, name, currency, contact, balance=0, **kwargs):
        # добавление еще одного кредита в список
        # или обновление баланса существующего кредита
        exist = False
        for x in self.credits:
            if (name == x.name) & (contact == x.contact):
                exist = True
                x.set_balance(balance)
        if not exist:
            self.credits.append(
                OneCredit(name, currency, contact, balance, **kwargs)
            )

    def set_out_item(self, name, **kwargs):
        so = SimpleObject(name, **kwargs)
        so.__name__ = self.simple_objects['OneOutItem']
        self.out_items.append(so)

    def set_in_item(self, name, **kwargs):
        so = SimpleObject(name, **kwargs)
        so.__name__ = self.simple_objects['OneInItem']
        self.in_items.append(so)

    def set_contact(self, name, **kwargs):
        so = SimpleObject(name, **kwargs)
        so.__name__ = self.simple_objects['OneContact']
        self.contacts.append(so)

    def set_simple(self, name, simple_type, **kwargs):
        if simple_type == self.simple_objects['OneOutItem']:
            self.set_out_item(name, **kwargs)
        if simple_type == self.simple_objects['OneInItem']:
            self.set_in_item(name, **kwargs)
        if simple_type == self.simple_objects['OneContact']:
            self.set_contact(name, **kwargs)

    def get_info(self):
        # вывод информации о кошельках и кредитах в виде строки
        res = ""
        ps_names = []
        for i in self.pockets:
            ps_names.append(i.name)
        ps_names.sort()
        for n in ps_names:
            i = self.get_one(n, 'OnePocket')
            res += i.get_info()
            if self.pockets[-1] != i:
                res += "\n"
        if (len(self.pockets) > 0) & (len(self.contacts) > 0):
            res += "\n"
        cs_names = []
        for i in self.credits:
            cs_names.append(i.name)
        cs_names.sort()
        for n in cs_names:
            i = self.get_one(n, 'OneCredit')
            res += i.get_info()
            if self.credits[-1] != i:
                res += "\n"
        return res

    def get_all_info(self):
        # вывод информации о всех simple_objects в виде строки
        res = ''
        attrs = {'OnePocket': self.pockets,
                 'OneCredit': self.credits,
                 'OneOutItem': self.out_items,
                 'OneInItem': self.in_items,
                 'OneContact': self.contacts,
                 'Currency': self.currency
                 }
        for key in attrs:
            s_names = []
            for i in attrs[key]:
                s_names.append(i.name)
            s_names.sort()
            for n in s_names:
                i = self.get_one(n, key)
                res += i.get_info()
                res += "\n"
        return res

    def get_one(self, obj_name, obj_type=None):
        # возвращает simple_object по наименованию
        if obj_type == self.simple_objects['OnePocket'] or obj_type is None:
            for i in self.pockets:
                if i.name == obj_name:
                    return i
        if obj_type == self.simple_objects['OneCredit'] or obj_type is None:
            for i in self.credits:
                if i.name == obj_name:
                    return i
        if obj_type == self.simple_objects['OneContact'] or obj_type is None:
            for i in self.contacts:
                if i.name == obj_name:
                    return i
        if obj_type == self.simple_objects['OneOutItem'] or obj_type is None:
            for i in self.out_items:
                if i.name == obj_name:
                    return i
        if obj_type == self.simple_objects['OneInItem'] or obj_type is None:
            for i in self.in_items:
                if i.name == obj_name:
                    return i
        if obj_type == self.simple_objects['Currency'] or obj_type is None:
            for i in self.currency:
                if i.name == obj_name:
                    return i

    def find_by_key(self, key, obj_type=None):
        if obj_type == self.simple_objects['OnePocket'] or obj_type is None:
            for i in self.pockets:
                if i.kwargs.has_key('Ref_Key'):
                    if i.kwargs['Ref_Key'] == key:
                        return i
        if obj_type == self.simple_objects['OneCredit'] or obj_type is None:
            for i in self.credits:
                if i.kwargs.has_key('Ref_Key'):
                    if i.kwargs['Ref_Key'] == key:
                        return i
        if obj_type == self.simple_objects['OneContact'] or obj_type is None:
            for i in self.contacts:
                if i.kwargs.has_key('Ref_Key'):
                    if i.kwargs['Ref_Key'] == key:
                        return i
        if obj_type == self.simple_objects['OneOutItem'] or obj_type is None:
            for i in self.out_items:
                if i.kwargs.has_key('Ref_Key'):
                    if i.kwargs['Ref_Key'] == key:
                        return i
        if obj_type == self.simple_objects['OneInItem'] or obj_type is None:
            for i in self.in_items:
                if i.kwargs.has_key('Ref_Key'):
                    if i.kwargs['Ref_Key'] == key:
                        return i
        if obj_type == self.simple_objects['Currency'] or obj_type is None:
            for i in self.currency:
                if i.kwargs.has_key('Ref_Key'):
                    if i.kwargs['Ref_Key'] == key:
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
        # валюты:
        for data in self.db.get_currency():
            self.set_cur(
                data,
                **self.db.get_kwargs(data[0], self.simple_objects['Currency'])
            )
        # кошельки:
        for data in self.db.get_pockets():
            self.set_pocket(
                *data,
                **self.db.get_kwargs(data[0], self.simple_objects['OnePocket'])
            )
        # статьи доходов:
        for data in self.db.get_items_in():
            self.set_in_item(
                data,
                **self.db.get_kwargs(data[0], self.simple_objects['OneInItem'])
            )
        # статьи расходов:
        for data in self.db.get_items_out():
            self.set_out_item(
                data,
                **self.db.get_kwargs(data[0], self.simple_objects['OneOutItem'])
            )
        # контакты:
        for data in self.db.get_contacts():
            self.set_contact(
                data,
                **self.db.get_kwargs(data[0], self.simple_objects['OneContact'])
            )
        # кредиты:
        for data in self.db.get_credits():
            self.set_credit(
                *data,
                **self.db.get_kwargs(data[0], self.simple_objects['OneCredit'])
            )

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

    def set_settings(self, url_wsdl, login, password):
        self.settings['URL'] = url_wsdl
        authorization = 'Basic %s' % base64.encodestring('%s:%s' % (login,
                                                                    password)
                                                         ).strip()
        self.settings['Authorization'] = authorization
        self.db.reset_settings(url_wsdl, authorization)

    def get_settings(self):
        data = self.db.get_settings()
        if data != -1:
            self.settings['URL'] = data[0]
            self.settings['Authorization'] = data[1]

    def parse_income_cur(self, data):
        for i in data:
            self.set_cur(i['Description'], **i)

    def parse_income_in_items(self, data):
        for i in data:
            self.set_in_item(i['Description'], **i)

    def parse_income_out_items(self, data):
        for i in data:
            self.set_out_item(i['Description'], **i)

    def parse_income_contacts(self, data):
        for i in data:
            self.set_contact(i['Description'], **i)

    def parse_income_pockets(self, data):
        for i in data:
            self.set_pocket(i['Description'],
                            self.find_by_key(i[u'Валюта_Key'],
                                             self.simple_objects['Currency']),
                            0, **i)

    def parse_income_credits(self, data):
        for i in data:
            self.set_credit(i['Description'],
                            self.find_by_key(i[u'Валюта_Key'],
                                             self.simple_objects['Currency']),
                            self.find_by_key(i[u'Контакт_Key'],
                                             self.simple_objects['OneContact'])
                            , 0, **i)

    def parsing_functions(self):
        return {self.simple_objects['Currency']: self.parse_income_cur,
                self.simple_objects['OneInItem']: self.parse_income_in_items,
                self.simple_objects['OneOutItem']: self.parse_income_out_items,
                self.simple_objects['OneContact']: self.parse_income_contacts,
                self.simple_objects['OnePocket']: self.parse_income_pockets,
                self.simple_objects['OneCredit']: self.parse_income_credits}

    def get_data(self):
        if hasattr(self, 'settings'):
            self.get_settings()
            sr = PocketDB.ODataRequests(self.settings)
            sr.get_refs(self.parsing_functions())


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

