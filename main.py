# coding: utf-8


"""
Интерфейсная часть
"""
from gtk._gtk import Button

import PocketClass
from kivy.app import App, Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import (NumericProperty, ObjectProperty, StringProperty,
    ListProperty)
from kivy.graphics import Rectangle, Color, Canvas
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from functools import partial


class MyFace(StackLayout):
    money_label_text = StringProperty('')

    def __init__(self, **kwargs):
        super(MyFace, self).__init__(**kwargs)
        self.pcs = PocketClass.Pockets('MyPythonMoney.db')
        self.pcs.fill_from_db()
        self.prepare_action_chooser()
        self.previous_action_name = ''

    def prepare_action_chooser(self):
        self.chooser = DrpDwnList(
                'действие:',
                [self.pcs.actions_names[i+1] for i in xrange(8)],
                self.prepare_action)
        box_layout = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(1, None),
                orientation='horizontal')
        self.money_label = Label(markup=True)
        self.money_label_text = 'остаток'
        box_layout.add_widget(self.chooser)
        box_layout.add_widget(self.money_label)
        self.add_widget(box_layout)

    def get_last(self, item_name):
        """
        :param item_name:
        :return: возврат последнего использованного значения этой позиции
        """
        #todo возврат последнего
        return item_name

    def on_money_label_text(self, instance, value):
        self.money_label.text = ('[b][color=008000]%s[/color][/b]' % value)

    def show_money(self, pocket_name):
        self.money_label_text = str(self.pcs.get_one(pocket_name).balance)

    def prepare_action(self, action_name, *args, **kwargs):
        if self.previous_action_name == 'In':
            self.remove_widget(self.pocket)
            self.remove_widget(self.item_in)
            self.remove_widget(self.summ)
            self.remove_widget(self.comment)
            self.remove_widget(self.btn)
        elif self.previous_action_name == 'Out':
            self.remove_widget(self.pocket)
            self.remove_widget(self.item_out)
            self.remove_widget(self.summ)
            self.remove_widget(self.amount)
            self.remove_widget(self.comment)
            self.remove_widget(self.btn)
        elif self.previous_action_name == 'Betwean':
            self.remove_widget(self.pocket)
            self.remove_widget(self.to_pocket)
            self.remove_widget(self.summ)
            self.remove_widget(self.comment)
            self.remove_widget(self.btn)
        elif self.previous_action_name == 'Exchange':
            self.remove_widget(self.pocket)
            self.remove_widget(self.to_pocket)
            self.remove_widget(self.summ_out)
            self.remove_widget(self.summ_in)
            self.remove_widget(self.comment)
            self.remove_widget(self.btn)
        elif self.previous_action_name == 'Credit1In':
            pass
        elif self.previous_action_name == 'Credit1Out':
            pass
        elif self.previous_action_name == 'Credit2In':
            pass
        elif self.previous_action_name == 'Credit2Out':
            pass
        if action_name == 'In':
            self.pocket = DrpDwnList('Кошелек:',
                                     [i.name for i in self.pcs.pockets],
                                     self.show_money)
            self.add_widget(self.pocket)
            self.item_in = DrpDwnList('Статья:', self.pcs.in_items)
            self.add_widget(self.item_in)
            self.summ = InptData('Сумма:')
            self.add_widget(self.summ)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.do_action_in))
            self.add_widget(self.btn)
        elif action_name == 'Out':
            self.pocket = DrpDwnList('Кошелек:',
                                     [i.name for i in self.pcs.pockets],
                                     self.show_money)
            self.add_widget(self.pocket)
            self.item_out = DrpDwnList('Статья:', self.pcs.out_items)
            self.add_widget(self.item_out)
            self.summ = InptData('Сумма:')
            self.add_widget(self.summ)
            self.amount = InptData('Количество:')
            self.add_widget(self.amount)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.do_action_out))
            self.add_widget(self.btn)
        elif action_name == 'Betwean':
            self.pocket = DrpDwnList('Из кошелька:',
                                     [i.name for i in self.pcs.pockets],
                                     self.show_money)
            self.add_widget(self.pocket)
            self.to_pocket = DrpDwnList('В кошелек:',
                                     [i.name for i in self.pcs.pockets],
                                     self.show_money)
            self.add_widget(self.to_pocket)
            self.summ = InptData('Сумма:')
            self.add_widget(self.summ)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.do_action_between))
            self.add_widget(self.btn)
        elif action_name == 'Exchange':
            self.pocket = DrpDwnList('Из кошелька:',
                                     [i.name for i in self.pcs.pockets],
                                     self.show_money)
            self.add_widget(self.pocket)
            self.to_pocket = DrpDwnList('В кошелек:',
                                     [i.name for i in self.pcs.pockets],
                                     self.show_money)
            self.add_widget(self.to_pocket)
            self.summ_out = InptData('Сумма потрачено:')
            self.add_widget(self.summ_out)
            self.summ_in = InptData('Сумма получено:')
            self.add_widget(self.summ_in)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.some_action))
            self.add_widget(self.btn)
        elif action_name == 'Credit1In':
            pass #todo обработка интерфейса и работы с кредитами
        elif action_name == 'Credit1Out':
            pass
        elif action_name == 'Credit2In':
            pass
        elif action_name == 'Credit2Out':
            pass
        self.previous_action_name = action_name


    def some_action(self, x):
        pass

    def do_action_in(self, *args):
        self.pcs.action_in(self.pcs.get_one(self.pocket.spinner.text),
                           self.item_in.spinner.text,
                           float(self.summ.text_input.text),
                           0,
                           self.comment.text_input.text)

    def do_action_out(self, *args):
        self.pcs.action_out(self.pcs.get_one(self.pocket.spinner.text),
                            self.item_out.spinner.text,
                            float(self.summ.text_input.text),
                            float(self.amount.text_input.text),
                            self.comment.text_input.text)

    def do_action_between(self, *args):
        self.pcs.action_between(self.pcs.get_one(self.pocket.spinner.text),
                                self.pcs.get_one(self.to_pocket.spinner.text),
                                float(self.summ.text_input.text),
                                self.comment.text_input.text)

    def do_action_exchange(self, *args):
        self.pcs.action_exchange(self.pcs.get_one(self.pocket.spinner.text),
                                 self.pcs.get_one(self.to_pocket.spinner.text),
                                 float(self.summ_out.text_input.text),
                                 float(self.summ_in.text_input.text),
                                 self.comment.text_input.text)


class DrpDwnList(BoxLayout):

    def __init__(self, caption, values, action=None, **kwargs):
        self.values = values
        self.caption = caption
        self.action = action
        super(DrpDwnList, self).__init__(**kwargs)
        self.spinner = Spinner(
            # default value shown
            text='..select..',
            # available values
            values=values,
            # just for positioning in our example
            #size_hint=(None, None),
            #size=(100, 44),
            #pos_hint={'center_x': .5, 'center_y': .5}
                )
        if action is not None:
            self.spinner.bind(text=self.use_selected_value)
        self.add_widget(self.spinner)

    def use_selected_value(self, spinner, text):
        self.action(text)


class InptData(BoxLayout):

    def __init__(self, caption, **kwargs):
        self.caption = caption
        super(InptData, self).__init__(**kwargs)
        self.text_input = TextInput(height=20)
        self.add_widget(self.text_input)


class MyMoney(App):
    def build(self):
        scroll_view = ScrollView(size_hint=(1, 1),
                                 #size=(720, 1280),
                                 do_scroll_x=False, do_scroll_y=True)
        self.face = MyFace()
        scroll_view.add_widget(self.face)
        return scroll_view

    def on_stop(self):
        self.face.pcs.close_db()

if __name__ == '__main__':
    Builder.load_file('main.kv')
    MyMoney().run()