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
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics import Rectangle, Color #, Canvas
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

    nu = NumericProperty(0)

    def get_last(self, item_name):
        """
        :param item_name:
        :return: возврат последнего использованного значения этой позиции
        """
        #todo возврат последнего
        return item_name

    def prepare_action(self, action_name):
        if action_name == 'In':
            self.pocket = DrpDwnList()
            self.pocket.label_text = 'Кошелек:'
            self.add_widget(self.pocket)
            self.item_in = DrpDwnList()
            self.item_in.label_text = 'Статья:'
            self.add_widget(self.item_in)
            self.summ = InptData()
            self.summ.label_text = 'Сумма:'
            self.add_widget(self.summ)
            self.comment = InptData()
            self.comment.label_text = 'Комментарий:'
            self.add_widget(self.comment)
            self.btn = Button(size_hint=(1, None), height=50,
                              on_press=partial(self.some_action))
            self.add_widget(self.btn)
        elif action_name == 'Out':
            self.pocket = DrpDwnList()
            self.pocket.label_text = 'Кошелек:'
            self.add_widget(self.pocket)
            self.item_out = DrpDwnList()
            self.item_out.label_text = 'Статья:'
            self.add_widget(self.item_out)
            self.summ = InptData()
            self.summ.label_text = 'Сумма:'
            self.add_widget(self.summ)
            self.amount = InptData()
            self.amount.label_text = 'Сумма:'
            self.add_widget(self.amount)
            self.comment = InptData()
            self.comment.label_text = 'Комментарий:'
            self.add_widget(self.comment)
            self.btn = Button(size_hint=(1, None), height=50,
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

    def some_action(self, x):
        if self.nu % 2 == 1:
            self.item_in = DrpDwnList()
            self.item_out = DrpDwnList()
            self.add_widget(self.item_in)
            self.add_widget(self.item_out)
            self.item_out.label_text = str(self.nu)
            self.item_in.label_text = self.get_last('Статья дохода:')
            self.nu += 1
        else:
            # self.clear_widgets()
            # self.btn = Button(size_hint=(1, None), height=50,
            #              on_press=self.some_action())
            self.remove_widget(self.item_in)
            # self.remove_widget(self.item_out)
            # self.remove_widget(self.btn)
            # self.add_widget(self.btn)
            self.nu += 1
        # pass


class DrpDwnList(BoxLayout):
    label_text = StringProperty('')
    input_text = StringProperty('')
    pass


class InptData(BoxLayout):
    label_text = StringProperty('')
    input_text = StringProperty('')
    input_summ = NumericProperty(0)
    pass


class MyMoney(App):
    def build(self):

        face = MyFace()
        face.prepare_action('Out')
        # btn = Button()
        # face.add_widget(btn)
        return face


if __name__ == '__main__':
    Builder.load_file('main.kv')
    MyMoney().run()