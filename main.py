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


class MyFace(StackLayout):
    item_in = ObjectProperty(None)
    item_out = ObjectProperty(None)

    nu = NumericProperty(0)

    def get_last(self, item_name):
        """
        :param item_name:
        :return: возврат последнего использованного значения этой позиции
        """
        #todo возврат последнего
        return item_name

    def some_action(self):
        if self.nu % 2 == 0:
            self.item_in = DrpDwnList()
            self.item_out = DrpDwnList()
            self.add_widget(self.item_in)
            self.add_widget(self.item_out)
            self.item_out.label_text = str(self.nu)
            self.item_in.label_text = self.get_last('Статья дохода:')
            self.nu += 1
        else:
            # self.clear_widgets()
            self.remove_widget(self.item_in)
            self.remove_widget(self.item_out)
            self.nu += 1



class DrpDwnList(StackLayout):
    label_text = StringProperty('')
    input_text = StringProperty('')
    pass


class MyMoney(App):
    def build(self):

        face = MyFace()
        # btn = Button()
        # face.add_widget(btn)
        return face


if __name__ == '__main__':
    Builder.load_file('main.kv')
    MyMoney().run()