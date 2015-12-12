# coding: utf-8


class OnePocket:
    def __init__(self, name, currency, balance = 0):
        self.name = name
        self.currency = currency
        self.balance = balance


class SomePockets:
    common = 0

    def __init__(self):
        self.pockets = []
        self.common+=1

    def add_pocket(self, name, currency, balance = 0):
        self.pockets.append(OnePocket(name, currency, balance))

    def print_pockets(self):
        res = ""
        for i in self.pockets:
            res = "%s: %s %s" % (i.name,i.balance,i.currency) + "\t"
        return res


class PocketsActions(SomePockets):

    def fill_pockets(self):
        pass

