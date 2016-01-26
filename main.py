# coding: utf-8


"""
Интерфейсная часть
"""
from gtk._gtk import Button

import PocketClass
from kivy.app import App, Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import (NumericProperty, ObjectProperty, StringProperty,
    ListProperty)
from kivy.graphics import Rectangle, Color #, Canvas
from kivy.uix.spinner import Spinner
from functools import partial


class MyFace(StackLayout):
    # item_in = ObjectProperty(None)
    # item_out = ObjectProperty(None)
    # pocket = ObjectProperty(None)
    # item = ObjectProperty(None)
    # summ = ObjectProperty(None)
    # amount = ObjectProperty(None)
    # comment = ObjectProperty(None)
    #
    # btn = ObjectProperty(None)

    #chooser = ObjectProperty(DrpDwnList)
    money_label_text = StringProperty('')

    def __init__(self, **kwargs):
        super(MyFace,self).__init__(**kwargs)
        self.pcs = PocketClass.Pockets('MyPythonMoney.db')
        self.pcs.fill_from_db()
        self.pcs.get_setiings()
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
            pass
        elif self.previous_action_name == 'Exchange':
            pass
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
                              on_press=partial(self.some_action))
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
                              on_press=partial(self.some_action))
            self.add_widget(self.btn)
        elif action_name == 'Betwean':
            pass
        elif action_name == 'Exchange':
            pass
        elif action_name == 'Credit1In':
            pass
        elif action_name == 'Credit1Out':
            pass
        elif action_name == 'Credit2In':
            pass
        elif action_name == 'Credit2Out':
            pass
        self.previous_action_name = action_name

    def some_action(self, x):
        pass


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
    input_text = StringProperty(None)

    def __init__(self, caption, **kwargs):
        self.caption = caption
        super(InptData, self).__init__(**kwargs)


class MyMoney(App):
    def build(self):
        face = MyFace()
        return face


if __name__ == '__main__':
    Builder.load_file('main.kv')
    MyMoney().run()