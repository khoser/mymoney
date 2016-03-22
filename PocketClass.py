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


class OneCurrency(SimpleObject):
    """Один кошелек со своей валютой и баллансом"""
    def __init__(self, name, course=1, multiplicity='1', **kwargs):
        SimpleObject.__init__(self, name, **kwargs)
        self.__name__ = 'OneCurrency'
        self.set_course(course, multiplicity)

    def set_course(self, course, multiplicity='1'):
        if type(course) == float or int:
            self.course = course
        elif type(course) == str or type(course) == unicode:
            self.balance = float(course.replace(" ", "").replace(",", "."))
        self.multiplicity = multiplicity

    def coeff(self):
        ret_val = 1
        if type(self.course) in [int, float] and self.course != 0:
            ret_val = self.course
        if float(self.multiplicity) != 0:
            ret_val /= self.multiplicity
        return ret_val


    def get_info(self):
        # вывод информации в виде строки
        kw = ''
        ks = self.kwargs.keys()
        ks.sort()
        for k in ks:
            kw += '                    %s: %s \n' % (k, self.kwargs[k])
        return "%s: %s %s\n%s" % (self.name, self.balance, self.currency, kw)


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
        elif type(balance) == str or type(balance) == unicode:
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
            'OneCurrency': 'OneCurrency'
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

    def set_cur(self, name, course=1, multiplicity='1', **kwargs):
        # добавление валюты в словарь
        exist = False
        for x in self.currency:
            if name == x.name:
                exist = True
                x.set_course()
        if not exist:
            self.currency.append(OneCurrency(name, course, multiplicity, **kwargs))

    def set_pocket(self, name, currency, balance=0, **kwargs):
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
                 'OneCurrency': self.currency
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
        if obj_type == self.simple_objects['OneCurrency'] or obj_type is None:
            for i in self.currency:
                if i.name == obj_name:
                    return i
        return None

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
        if obj_type == self.simple_objects['OneCurrency'] or obj_type is None:
            for i in self.currency:
                if i.kwargs.has_key('Ref_Key'):
                    if i.kwargs['Ref_Key'] == key:
                        return i
        return None

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
                *data,
                **self.db.get_kwargs(data[0],
                                     self.simple_objects['OneCurrency'])
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

    def action_credit2_in(self, pocket, credit, summ, addit_summ,
                          percent_sum, comment=''):
        """
        нам вернули долг
        в кошелек по кредиту от контакта сумму
        """
        if (type(summ) != float and type(summ) != int or
                type(addit_summ) != float and type(addit_summ) != int or
                type(percent_sum) != float and type(percent_sum) != int):
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
        pc.balance += (summ + percent_sum - addit_summ)
        self.db.upd_pocket_balance(pc.name, pc.balance)
        self.db.upd_credit_balance(cr.name, cr.balance)
        self.db.action_credit2_in(pc.name, cr.name, summ, addit_summ,
                                  percent_sum, comment)

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
            if 'IsFolder' in i and i['IsFolder'] == True:
                continue
            self.set_cur(i['Description'], 1, '1', **i)

    def parse_income_in_items(self, data):
        for i in data:
            if 'IsFolder' in i and i['IsFolder'] == True:
                continue
            self.set_in_item(i['Description'], **i)

    def parse_income_out_items(self, data):
        for i in data:
            if 'IsFolder' in i and i['IsFolder'] == True:
                continue
            self.set_out_item(i['Description'], **i)

    def parse_income_contacts(self, data):
        for i in data:
            if 'IsFolder' in i and i['IsFolder'] == True:
                continue
            self.set_contact(i['Description'], **i)

    def parse_income_pockets(self, data):
        for i in data:
            if 'IsFolder' in i and i['IsFolder'] == True:
                continue
            self.set_pocket(i['Description'],
                            unicode(self.find_by_key(
                                i[u'Валюта_Key'],
                                self.simple_objects['OneCurrency'])),
                            0, **i)

    def parse_income_credits(self, data):
        for i in data:
            if 'IsFolder' in i and i['IsFolder'] == True:
                continue
            self.set_credit(i['Description'],
                            unicode(self.find_by_key(
                                i[u'Валюта_Key'],
                                self.simple_objects['OneCurrency'])),
                            unicode(self.find_by_key(
                                i[u'Контакт_Key'],
                                self.simple_objects['OneContact']))
                            , 0, **i)

    def parse_balance(self, data):
        for i in data:
            one_instance = None
            if (i['ExtDimension1_Type'] ==
                    u'StandardODATA.Catalog_КошелькиИСчета'):
                one_instance = self.find_by_key(
                    i['ExtDimension1'], self.simple_objects['OnePocket'])
            if (i['ExtDimension1_Type'] ==
                    u'StandardODATA.Catalog_Долги'):
                one_instance = self.find_by_key(
                    i['ExtDimension1'], self.simple_objects['OneCredit'])
            if one_instance is not None:
                one_instance.set_balance(i[u'ВалютнаяСуммаBalance'])

    def parse_courses(self, data):
        for i in data:
            one_instance = self.find_by_key(
                i[u'Валюта_Key'], self.simple_objects['OneCurrency'])
            if one_instance is not None:
                one_instance.set_course(i[u'Курс'], i[u'Кратность'])

    def parsing_functions(self):
        return {self.simple_objects['OneCurrency']: self.parse_income_cur,
                self.simple_objects['OneInItem']: self.parse_income_in_items,
                self.simple_objects['OneOutItem']: self.parse_income_out_items,
                self.simple_objects['OneContact']: self.parse_income_contacts,
                self.simple_objects['OnePocket']: self.parse_income_pockets,
                self.simple_objects['OneCredit']: self.parse_income_credits,
                'Balance': self.parse_balance,
                'Courses': self.parse_courses}

    def get_data(self):
        if (hasattr(self, 'settings') and
                "Authorization" in self.settings and
                len(self.settings["Authorization"]) > 0):
            self.get_settings()
            sr = PocketDB.ODataRequests(self.settings)
            sr.get_refs(self.parsing_functions())
            self.db.recreate_refs(self)

    def reformat_data(self):
        data_dict = self.db.prepare_send_data()
        data_dict.sort()
        ret_value = []
        for d in data_dict:
            date = d[1]  # '2016-03-17T22:22:22' todo
            if d[0] == 1:
                pocket = self.get_one(d[2], self.simple_objects['OnePocket'])
                item = self.get_one(d[3], self.simple_objects['OneInItem'])
                currency = self.get_one(unicode(pocket.currency),
                                        self.simple_objects['OneCurrency'])
                ret_value.append(
                    {'action': 1,
                     'Date': date,
                     'comment': '',
                     'pocket_key': pocket.kwargs['Ref_Key'],
                     'item_in_key': item.kwargs['Ref_Key'],
                     'sum': float(d[4]),
                     'line_comment': d[5],
                     'sum_rub': float(d[4]) * currency.coeff(),
                     'course': currency.course,
                     'multiplicity': currency.multiplicity
                     }
                )
            if d[0] == 2:
                pocket = self.get_one(d[2], self.simple_objects['OnePocket'])
                item = self.get_one(d[3], self.simple_objects['OneOutItem'])
                currency = self.get_one(unicode(pocket.currency),
                                        self.simple_objects['OneCurrency'])
                amount = 0
                if (u'КоличественныйУчет' in currency.kwargs
                    and currency.kwargs[u'КоличественныйУчет']):
                    amount = float(d[5])
                ret_value.append(
                    {'action': 2,
                     'Date': date,
                     'comment': '',
                     'pocket_key': pocket.kwargs['Ref_Key'],
                     'currency_key': currency.kwargs['Ref_Key'],
                     'item_out_key': item.kwargs['Ref_Key'],
                     'sum': float(d[4]),
                     'amount': amount,
                     'line_comment': d[6]
                     }
                )
            if d[0] == 3:
                pocket_out = self.get_one(d[2], self.simple_objects['OnePocket'])
                pocket_in = self.get_one(d[3], self.simple_objects['OnePocket'])
                currency = self.get_one(unicode(pocket_out.currency),
                                        self.simple_objects['OneCurrency'])
                ret_value.append(
                    {'action': 3,
                     'Date': date,
                     'pocket_out_key': pocket_out.kwargs['Ref_Key'],
                     'pocket_in_key': pocket_in.kwargs['Ref_Key'],
                     'currency_key': currency.kwargs['Ref_Key'],
                     'sum': float(d[4]),
                     'line_comment': d[5]
                     }
                )
            if d[0] == 4:
                pocket_out = self.get_one(d[2], self.simple_objects['OnePocket'])
                pocket_in = self.get_one(d[3], self.simple_objects['OnePocket'])
                currency_out = self.get_one(unicode(pocket_out.currency),
                                            self.simple_objects['OneCurrency'])
                currency_in = self.get_one(unicode(pocket_in.currency),
                                           self.simple_objects['OneCurrency'])
                ret_value.append(
                    {'action': 4,
                     'Date': date,
                     'pocket_out_key': pocket_out.kwargs['Ref_Key'],
                     'pocket_in_key': pocket_in.kwargs['Ref_Key'],
                     'currency_out_key': currency_out.kwargs['Ref_Key'],
                     'currency_in_key': currency_in.kwargs['Ref_Key'],
                     'sum_out': float(d[4]),
                     'sum_in': float(d[5]),
                     'line_comment': d[6]
                     }
                )
            if d[0] == 5:
                pocket = self.get_one(d[2], self.simple_objects['OnePocket'])
                credit = self.get_one(d[3], self.simple_objects['OneCredit'])
                currency = self.get_one(unicode(pocket.currency),
                                        self.simple_objects['OneCurrency'])
                contact = self.get_one(d[6], self.simple_objects['OneContact'])
                ret_value.append(
                    {'action': 5,
                     'Date': date,
                     'contact_key': contact.kwargs['Ref_Key'],
                     'credit_key': credit.kwargs['Ref_Key'],
                     'pocket_key': pocket.kwargs['Ref_Key'],
                     'currency_key': currency.kwargs['Ref_Key'],
                     'sum': float(d[4]),
                     'line_comment': d[5],
                     'addit_sum': float(d[7])
                     }
                )
            if d[0] == 6:
                pocket = self.get_one(d[2], self.simple_objects['OnePocket'])
                credit = self.get_one(d[3], self.simple_objects['OneCredit'])
                currency = self.get_one(unicode(pocket.currency),
                                        self.simple_objects['OneCurrency'])
                contact = self.get_one(d[6], self.simple_objects['OneContact'])
                item = self.get_one(u'Налоги, штрафы, комиссии',
                                    self.simple_objects['OneOutItem'])
                ret_value.append(
                    {'action': 6,
                     'Date': date,
                     'currency_key': currency.kwargs['Ref_Key'],
                     'additional_sum': float(d[7]),
                     'sum': float(d[4]),
                     'percent_sum': float(d[8]),
                     'comment': d[5],
                     'pocket_key': pocket.kwargs['Ref_Key'],
                     'credit_key': credit.kwargs['Ref_Key'],
                     'contact_key': contact.kwargs['Ref_Key'],
                     'course': currency.course,
                     'multiplicity': currency.multiplicity,
                     'percent_item_key': item.kwargs['Ref_Key'],
                     'total_sum': float(d[4]) + float(d[7]) + float(d[8])
                     }
                )
            if d[0] == 7:
                pocket = self.get_one(d[2], self.simple_objects['OnePocket'])
                credit = self.get_one(d[3], self.simple_objects['OneCredit'])
                currency = self.get_one(unicode(pocket.currency),
                                        self.simple_objects['OneCurrency'])
                contact = self.get_one(d[6], self.simple_objects['OneContact'])
                item = self.get_one(u'Прочие доходы',
                                    self.simple_objects['OneInItem'])
                ret_value.append(
                    {'action': 7,
                     'Date': date,
                     'currency_key': currency.kwargs['Ref_Key'],
                     'sum': float(d[4]),
                     'credit_key': credit.kwargs['Ref_Key'],
                     'comment': d[5],
                     'contact_key': contact.kwargs['Ref_Key'],
                     'pocket_key': pocket.kwargs['Ref_Key'],
                     'item_key': item.kwargs['Ref_Key'],
                     'additional_sum': float(d[7]),
                     'percent_sum': float(d[8])
                     }
                )
            if d[0] == 8:
                pocket = self.get_one(d[2], self.simple_objects['OnePocket'])
                credit = self.get_one(d[3], self.simple_objects['OneCredit'])
                currency = self.get_one(unicode(pocket.currency),
                                        self.simple_objects['OneCurrency'])
                contact = self.get_one(d[6], self.simple_objects['OneContact'])
                ret_value.append(
                    {'action': 8,
                     'Date': date,
                     'contact_key': contact.kwargs['Ref_Key'],
                     'credit_key': credit.kwargs['Ref_Key'],
                     'pocket_key': pocket.kwargs['Ref_Key'],
                     'currency_key': currency.kwargs['Ref_Key'],
                     'sum': float(d[4]),
                     'comment': d[5],
                     'additional_sum': float(d[7]),
                     'total_sum': float(d[4]) + float(d[7])
                     }
                )

    def post_data(self):
        if (hasattr(self, 'settings') and
                "Authorization" in self.settings and
                len(self.settings["Authorization"]) > 0):
            self.get_settings()
            sr = PocketDB.ODataRequests(self.settings)
            data_dict = self.db.prepare_send_data()
            data_dict.sort()
            if sr.post_docs(data_dict):
                self.db.recreate_docs()


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

