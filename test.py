# coding: utf-8


"""
тест
"""


# import PocketClass


# pcs = PocketClass.Pockets('MyPythonMoney.db')
#pcs.create_db()
#pcs.set_settings('http://money.kter.ru/money/ws/ws1.1cws?wsdl',
#                 'ktu',
#                 '', False)
#print "\ninit:\n" + pcs.get_info()
#pcs.get_all_soap_data()
#print "\nget data:\n" + pcs.get_info()
#print "\n"
#for itm in pcs.out_items:
#    print itm
# pcs.fill_from_db()
#pcs.action_between(pcs.pockets[9],pcs.pockets[6], 5000, 'UZI')
#pcs.action_out(pcs.pockets[6], pcs.out_items[7], 2000, 0, 'UZI')
#pcs.action_out(pcs.pockets[6], pcs.out_items[7], 115, 0, 'Bahils')
#pcs.action_out(pcs.pockets[6], pcs.out_items[14], 38, 0, 'Potato')
#print "\nout:\n" + pcs.get_info()


# pcs.send_soap_data()
#print "\nafter sync:\n" + pcs.get_info()
#print "\nafter filling:\n" + pcs.get_info()

'''
pcs.set_pocket("cash", "rub", 501.6)
pcs.set_pocket("card", "rub", 3501.6)
pcs.set_pocket("foreign", "usd", 0)
pcs.in_items = ["zp", "ava", "other"]
pcs.out_items = ["dinner", "product", "xo3pacxoD", "other", "hobby"]
pcs.contacts = ["mother", "father", "brother", "man"]
pcs.set_credit("it was 20.02", "rub", "man", 0)
pcs.set_credit("it was 10.01", "rub", "man", 100)
print "\ninit:\n" + pcs.get_info()
pcs.create_db()
pcs.fill_from_db()
pcs.action_in("card", "zp", 100, 0, 'test1')
print "\nin:\n" + pcs.get_info()
pcs.action_out("cash", "dinner", 150, 0, 'today')
print "\nout:\n" + pcs.get_info()
pcs.action_between("cash", "card", 200, 'top of the day')
print "\nbetween:\n" + pcs.get_info()
pcs.action_exchange("cash", "foreign", 150, 3, 'top of the day')
print "\nexchange:\n" + pcs.get_info()
pcs.action_credit1_in("cash", "it was 20.02", 500, 'top of the day')
print "\nвзяли в кредит:\n" + pcs.get_info()
pcs.action_credit1_out("cash", "it was 20.02", 300, 'top of the day')
print "\nвернули кредит:\n" + pcs.get_info()
pcs.action_credit2_out(pcs.pockets[1], "it was 10.01", 3000, 'top of the day')
print "\nдали в кредит:\n" + pcs.get_info()
pcs.action_credit2_in(pcs.pockets[1], "it was 10.01", 1000, 'top of the day')
print "\nнам вернули кредит:\n" + pcs.get_info()
pcs.fill_from_db()
print "\nafter filling:\n" + pcs.get_info()
'''
# pcs.close_db()

from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from random import random as r
from functools import partial


class StressCanvasApp(App):

    def add_rects(self, label, wid, count, *largs):
        label.text = str(int(label.text) + count)
        with wid.canvas:
            for x in range(count):
                Color(r(), 1, 1, mode='hsv')
                Rectangle(pos=(r() * wid.width + wid.x,
                               r() * wid.height + wid.y), size=(20, 20))

    def double_rects(self, label, wid, *largs):
        count = int(label.text)
        self.add_rects(label, wid, count, *largs)

    def reset_rects(self, label, wid, *largs):
        label.text = '0'
        wid.canvas.clear()

    def build(self):
        wid = Widget()

        label = Label(text='0')

        btn_add100 = Button(text='+ 100 rects',
                            on_press=partial(self.add_rects, label, wid, 100))

        btn_add500 = Button(text='+ 500 rects',
                            on_press=partial(self.add_rects, label, wid, 500))

        btn_double = Button(text='x 2',
                            on_press=partial(self.double_rects, label, wid))

        btn_reset = Button(text='Reset',
                           on_press=partial(self.reset_rects, label, wid))

        btn_add0 = Button(text='+ 0 rects',
                            on_press=partial(self.add_rects, label, wid, 0))

        layout = BoxLayout(size_hint=(1, None), height=50)
        layout.add_widget(btn_add100)
        layout.add_widget(btn_add500)
        layout.add_widget(btn_double)
        layout.add_widget(btn_reset)
        layout.add_widget(label)

        layout2 = BoxLayout(size_hint=(1, None), height=50)
        layout2.add_widget(btn_add0)

        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)
        root.add_widget(layout2)

        return root

if __name__ == '__main__':
    StressCanvasApp().run()