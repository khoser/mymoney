# coding: utf-8


"""
Интерфейсная часть
"""
import PocketClass
from kivy.app import App, Builder
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Rectangle, Color #, Canvas


class MyFace(BoxLayout):
    item_in = ObjectProperty(None)
    item_out = ObjectProperty(None)


    def get_last(self, item_name):
        """
        :param item_name:
        :return: возврат последнего использованного значения этой позиции
        """
        #todo возврат последнего
        return item_name


class ItemsIn(BoxLayout):
    pass


class ItemsOut(BoxLayout):
    pass


class MyMoney(App):
    def build(self):
        face = MyFace()
#        item_in = Items_in()
#        item_out = Items_out()
#        face.add_widget(item_in)
#        face.add_widget(item_out)
        return face


if __name__ == '__main__':
    Builder.load_file('main.kv')
    MyMoney().run()