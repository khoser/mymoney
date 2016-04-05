# coding: utf-8


"""
Интерфейсная часть
"""
import re
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar

import PocketClass
from garden.navigationdrawer import NavigationDrawer
from kivy.app import App, Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import (NumericProperty, ObjectProperty, StringProperty,
    ListProperty)
from kivy.graphics import Rectangle, Color, Canvas
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from functools import partial


class MyFace(StackLayout):
    money_label_text = StringProperty('')

    def __init__(self, pcs, **kwargs):
        super(MyFace, self).__init__(**kwargs)
        self.pcs = pcs
        self.pcs.fill_from_db()
        self.prepare_action_chooser()
        self.previous_action_name = ''

    def prepare_action_chooser(self):
        self.rem_recur_widgets(self)
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
        self.money_label_text = u'остаток'
        box_layout.add_widget(self.chooser)
        box_layout.add_widget(self.money_label)
        self.add_widget(box_layout)

    def rem_recur_widgets(self, childro):
        for ch in childro.children[:]:
            self.rem_recur_widgets(ch)
            childro.remove_widget(ch)

    def get_last(self, item_name):
        """
        :param item_name:
        :return: возврат последнего использованного значения этой позиции
        """
        #todo возврат последнего
        return item_name

    def on_money_label_text(self, instance, value):
        self.money_label.text = '[b][color=008000]%s[/color][/b]' % value

    def show_money(self, pocket_name):
        o = self.pcs.get_one(pocket_name, self.pcs.simple_objects['OnePocket'])
        if o is not None:
            self.money_label_text = unicode(o.balance)

    def show_all_new(self):
        if self.previous_action_name == 'In':
            self.show_money(self.pocket.spinner.text)
        elif self.previous_action_name == 'Out':
            self.show_money(self.pocket.spinner.text)
        elif self.previous_action_name == 'Between':
            self.show_money(self.pocket.spinner.text)
        elif self.previous_action_name == 'Exchange':
            self.show_money(self.pocket.spinner.text)
        elif self.previous_action_name == 'Credit1In':
            pass
        elif self.previous_action_name == 'Credit1Out':
            pass
        elif self.previous_action_name == 'Credit2In':
            pass
        elif self.previous_action_name == 'Credit2Out':
            pass
        self.prepare_action(self.previous_action_name)

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
        elif self.previous_action_name == 'Between':
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
            p_ar = [unicode(i) for i in self.pcs.pockets]
            p_ar.sort()
            i_ar = [unicode(i) for i in self.pcs.in_items]
            i_ar.sort()
            self.pocket = DrpDwnList('Кошелек:', p_ar, self.show_money)
            self.add_widget(self.pocket)
            self.item_in = DrpDwnList('Статья:', i_ar)
            self.add_widget(self.item_in)
            self.summ = InptData('Сумма:', inp_type=FloatInput)
            self.add_widget(self.summ)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.do_action_in))
            self.add_widget(self.btn)
        elif action_name == 'Out':
            p_ar = [unicode(i) for i in self.pcs.pockets]
            p_ar.sort()
            i_ar = [unicode(i) for i in self.pcs.out_items]
            i_ar.sort()
            self.pocket = DrpDwnList('Кошелек:', p_ar, self.show_money)
            self.add_widget(self.pocket)
            self.item_out = DrpDwnList('Статья:', i_ar)
            self.add_widget(self.item_out)
            self.summ = InptData('Сумма:', inp_type=FloatInput)
            self.add_widget(self.summ)
            self.amount = InptData('Количество:', inp_type=FloatInput)
            self.add_widget(self.amount)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.do_action_out))
            self.add_widget(self.btn)
        elif action_name == 'Between':
            p_ar = [unicode(i) for i in self.pcs.pockets]
            p_ar.sort()
            self.pocket = DrpDwnList('Из кошелька:', p_ar, self.show_money)
            self.add_widget(self.pocket)
            self.to_pocket = DrpDwnList('В кошелек:', p_ar, self.show_money)
            self.add_widget(self.to_pocket)
            self.summ = InptData('Сумма:', inp_type=FloatInput)
            self.add_widget(self.summ)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.do_action_between))
            self.add_widget(self.btn)
        elif action_name == 'Exchange':
            p_ar = [unicode(i) for i in self.pcs.pockets]
            p_ar.sort()
            self.pocket = DrpDwnList('Из кошелька:', p_ar, self.show_money)
            self.add_widget(self.pocket)
            self.to_pocket = DrpDwnList('В кошелек:', p_ar, self.show_money)
            self.add_widget(self.to_pocket)
            self.summ_out = InptData('Сумма потрачено:', inp_type=FloatInput)
            self.add_widget(self.summ_out)
            self.summ_in = InptData('Сумма получено:', inp_type=FloatInput)
            self.add_widget(self.summ_in)
            self.comment = InptData('Комментарий:')
            self.add_widget(self.comment)
            self.btn = Button(text='Учесть', size_hint=(1, None), height=50,
                              on_press=partial(self.do_action_exchange))
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

    def clear_inputs(self):
        if self.previous_action_name == 'In':
            # self.pocket
            # self.item_in
            self.summ.text_input.text = ''
            self.comment.text_input.text = u''
            # self.btn
        elif self.previous_action_name == 'Out':
            # self.pocket
            # self.item_out
            self.summ.text_input.text = ''
            self.amount.text_input.text = ''
            self.comment.text_input.text = u''
            # self.btn
        elif self.previous_action_name == 'Between':
            # self.pocket
            # self.to_pocket
            self.summ.text_input.text = ''
            self.comment.text_input.text = u''
            # self.btn
        elif self.previous_action_name == 'Exchange':
            # self.pocket
            # self.to_pocket
            self.summ_out.text_input.text = ''
            self.summ_in.text_input.text = ''
            self.comment.text_input.text = u''
            # self.btn
        elif self.previous_action_name == 'Credit1In':
            pass
        elif self.previous_action_name == 'Credit1Out':
            pass
        elif self.previous_action_name == 'Credit2In':
            pass
        elif self.previous_action_name == 'Credit2Out':
            pass

    def some_action(self, x):
        pass

    def do_action_in(self, *args):
        if self.summ.text_input.text == '':
            return
        self.pcs.action_in(
            self.pcs.get_one(self.pocket.spinner.text,
                             self.pcs.simple_objects['OnePocket']),
            self.item_in.spinner.text,
            float(self.summ.text_input.text),
            0,
            # unicode(self.comment.text_input.text.decode('utf-8')))
            self.comment.text_input.text)
        self.show_money(self.pocket.spinner.text)
        self.clear_inputs()

    def do_action_out(self, *args):
        if self.summ.text_input.text == '':
            return
        if self.amount.text_input.text == '':
            self.amount.text_input.text = '0'
        self.pcs.action_out(
            self.pcs.get_one(self.pocket.spinner.text,
                             self.pcs.simple_objects['OnePocket']),
            self.item_out.spinner.text,
            float(self.summ.text_input.text),
            float(self.amount.text_input.text),
            # unicode(self.comment.text_input.text.decode('utf-8')))
            self.comment.text_input.text)
        self.show_money(self.pocket.spinner.text)
        self.clear_inputs()

    def do_action_between(self, *args):
        self.pcs.action_between(
            self.pcs.get_one(self.pocket.spinner.text,
                             self.pcs.simple_objects['OnePocket']),
            self.pcs.get_one(self.to_pocket.spinner.text,
                             self.pcs.simple_objects['OnePocket']),
            float(self.summ.text_input.text),
            # unicode(self.comment.text_input.text.decode('utf-8')))
            self.comment.text_input.text)
        self.show_money(self.pocket.spinner.text)
        self.clear_inputs()

    def do_action_exchange(self, *args):
        self.pcs.action_exchange(
            self.pcs.get_one(self.pocket.spinner.text,
                             self.pcs.simple_objects['OnePocket']),
            self.pcs.get_one(self.to_pocket.spinner.text,
                             self.pcs.simple_objects['OnePocket']),
            float(self.summ_out.text_input.text),
            float(self.summ_in.text_input.text),
            # unicode(self.comment.text_input.text.decode('utf-8')))
            self.comment.text_input.text)
        self.show_money(self.pocket.spinner.text)
        self.clear_inputs()

    def prepare_report_view(self):
        self.rem_recur_widgets(self)
        box_layout = BoxLayout(
            padding=0,
            spacing=0,
            size_hint_x=1,
            size_hint_y=None,
            #, None),
            # height=20,
            orientation='horizontal')
        btn_rep = Button(text=u'Фин. рез.',  # size_hint=(1, None),
                         on_press=self.prepare_report_basis)
        box_layout.add_widget(btn_rep)
        btn_rep = Button(text=u'Не синхронизированые операции',
                         # size_hint=(1, None),
                         on_press=self.prepare_report_to_sync)
        box_layout.add_widget(btn_rep)
        btn_rep = DrpDwnList('Операции на сервере',
                             [u'День', u'Неделя', u'Месяц', u'Год'],
                             self.prepare_report_remote)
        box_layout.add_widget(btn_rep)
        self.add_widget(box_layout)

    def prepare_report_basis(self, *args):
        self.prepare_report_view()
        self.previous_action_name = 'report_basis'
        p_ar = [unicode(i) for i in self.pcs.pockets]
        p_ar.sort()
        c_ar = [unicode(i) for i in self.pcs.credits]
        c_ar.sort()
        cur_va = {}
        for p in p_ar:
            one = self.pcs.get_one(p, self.pcs.simple_objects['OnePocket'])
            if one.balance == 0:
                continue
            if cur_va.has_key(one.currency):
                cur_va[one.currency] += one.balance
            else:
                cur_va[one.currency] = one.balance
            p_lbl_name = Label(text='%s [sub]%s[/sub]'%(p, one.currency),
                            markup=True)
            p_lbl_blnc = Label(text=unicode(one.balance),
                               halign='right', valign='middle')
            box_layout = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(1, None),
                height=25,
                orientation='horizontal')
            box_layout.add_widget(p_lbl_name)
            box_layout.add_widget(p_lbl_blnc)
            self.add_widget(box_layout)
        for p in c_ar:
            one = self.pcs.get_one(p, self.pcs.simple_objects['OneCredit'])
            if one.balance == 0:
                continue
            if cur_va.has_key(one.currency):
                cur_va[one.currency] += one.balance
            else:
                cur_va[one.currency] = one.balance
            p_lbl_name = Label(text='%s [sub]%s[/sub][sup]%s[/sup]'%
                                    (p, one.currency, one.contact),
                               markup=True)
            p_lbl_blnc = Label(text=unicode(one.balance), text_size=self.size)
            box_layout = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(1, None),
                height=25,
                orientation='horizontal')
            box_layout.add_widget(p_lbl_name)
            box_layout.add_widget(p_lbl_blnc)
            self.add_widget(box_layout)
        box_layout = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(1, None))
        lbl_fin = Label(text=u'Финансовый результат')
        box_layout.add_widget(lbl_fin)
        self.add_widget(box_layout)
        for k in cur_va:
            p_lbl_name = Label(text=k)
            p_lbl_blnc = Label(text=unicode(cur_va[k]))
            box_layout = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(1, None),
                height=25,
                orientation='horizontal')
            box_layout.add_widget(p_lbl_name)
            box_layout.add_widget(p_lbl_blnc)
            self.add_widget(box_layout)

    def prepare_report_to_sync(self, *args):
        self.prepare_report_view()
        self.previous_action_name = 'report_to_sync'
        data_dict = self.pcs.db.prepare_send_data()
        for d_ids in data_dict:
            box_layout = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(1, None),
                height=12,
                orientation='horizontal')
            box_left = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(.2, 1),
                orientation='horizontal')
            box_mid = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(.8, 1),
                orientation='horizontal')
            box_right = BoxLayout(
                padding=0,
                spacing=0,
                size_hint=(.1, 1),
                orientation='horizontal')
            p_lbl_name = Label(text=unicode(d_ids[0]), width=10)
            box_left.add_widget(p_lbl_name)
            if d_ids[1] == 1:
                lbl_text = '[color=009900][b]+[/b][/color]'
            elif d_ids[1] == 2:
                lbl_text = '[color=990000][b]-[/b][/color]'
            elif d_ids[1] == 3:
                lbl_text = '[color=000099][b]=[/b][/color]'
            elif d_ids[1] == 4:
                lbl_text = '[color=999999][b]<>[/b][/color]'
            elif d_ids[1] == 5:
                lbl_text = '[color=FFFF00][b]!-[/b][/color]'
            elif d_ids[1] == 6:
                lbl_text = '[color=FFFF00][b]!+[/b][/color]'
            elif d_ids[1] == 7:
                lbl_text = '[color=FFFF00][b]+![/b][/color]'
            elif d_ids[1] == 8:
                lbl_text = '[color=FFFF00][b]-![/b][/color]'
            p_lbl_name = Label(text=lbl_text, markup=True, width=10)
            box_left.add_widget(p_lbl_name)
            k = d_ids[2]
            lbl_text = unicode(k).replace(u' ', u'\n')
            box_layout.height += 8 * lbl_text.count('\n')
            p_lbl_name = Label(text=lbl_text, markup=True)
            box_left.add_widget(p_lbl_name)
            for k in d_ids[3:]:
                if k == '-':
                    continue
                lbl_text = unicode(k).replace(u' ', u'\n')
                box_layout.height += 8 * lbl_text.count('\n')
                p_lbl_name = Label(text=lbl_text, markup=True)
                box_mid.add_widget(p_lbl_name)
            # todo: box_right
            box_layout.add_widget(box_left)
            box_layout.add_widget(box_mid)
            self.add_widget(box_layout)

    def prepare_report_remote(self, *args):
        self.prepare_report_view()
        self.previous_action_name = 'report_remote'


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
            size_hint=(1, .5),
            #size=(100, 44),
            #pos_hint={'center_x': .5, 'center_y': .5}
                )
        if action is not None:
            self.spinner.bind(text=self.use_selected_value)
        self.add_widget(self.spinner)

    def use_selected_value(self, spinner, text):
        self.action(text)


class FloatInput(TextInput):

    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s)
                          for s in substring.split('.',1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


class InptData(BoxLayout):

    def __init__(self, caption, inp_type=TextInput, **kwargs):
        self.caption = caption
        super(InptData, self).__init__(**kwargs)
        self.text_input = inp_type(height=20, text=u'', multiline=False)
        self.add_widget(self.text_input)

class AuthorizationPopUp(BoxLayout):

    def __init__(self, pcs, popup, **kwargs):
        self.orientation = 'vertical'
        self.pcs = pcs
        self.popup = popup
        super(AuthorizationPopUp, self).__init__(**kwargs)
        self.pcs.get_settings()
        label1 = Label(text='URL:')
        self.add_widget(label1)
        self.text_input1 = TextInput(text=self.pcs.settings['URL'])
        self.add_widget(self.text_input1)
        label1 = Label(text='Login:')
        self.add_widget(label1)
        self.text_input2 = TextInput(text=u'')
        self.add_widget(self.text_input2)
        label1 = Label(text='Password:')
        self.add_widget(label1)
        self.text_input3 = TextInput(password=True, text=u'')
        self.add_widget(self.text_input3)
        button = Button(height=40, text='Save', size_hint=(1, None),
                        on_press=partial(self.save_and_hide))
        self.add_widget(button)

    def save_and_hide(self, *args):
        self.pcs.set_settings(self.text_input1.text,
                              self.text_input2.text,
                              self.text_input3.text)
        self.popup.popup.dismiss()


class BackPanel(BoxLayout):

    def __init__(self, pcs, navi_drawer, face, this_app, p_bar, **kwargs):
        self.pcs = pcs
        self.navi_drawer = navi_drawer
        self.face = face
        self.this_app = this_app
        self.p_bar = p_bar
        self.orientation = 'vertical'
        super(BackPanel, self).__init__(**kwargs)
        self.popup = Popup(title='Настройки',
                           content=AuthorizationPopUp(self.pcs, self),
                           size_hint=(0.7, 0.7))
        button1 = Button(
            text='Учет', size_hint=(1, None),
            #height=50,
        )
        button1.bind(on_release=self.open_defaults)
        button2 = Button(
            text='Отчеты', size_hint=(1, None),
            #height=50,
        )
        button2.bind(on_release=self.open_reports)
        button3 = Button(
            text='Настройки', size_hint=(1, None),
            #height=50,
        )
        button3.bind(on_release=self.open_settings)
        button4 = Button(
            text='Синхронизировать', size_hint=(1, None),
            #height=50,
            on_press=partial(self.do_synchronization)
        )
        button5 = Button(
            text='Выход', size_hint=(1, None),
            #height=50,
        )
        button5.bind(on_release=self.exit_program)
        self.add_widget(button1)
        self.add_widget(button2)
        self.add_widget(button3)
        self.add_widget(button4)
        self.add_widget(button5)

    def open_defaults(self, *largs):
        self.navi_drawer.anim_to_state('closed')
        self.face.prepare_action_chooser()

    def open_reports(self, *largs):
        self.navi_drawer.anim_to_state('closed')
        self.face.prepare_report_view()

    def open_settings(self, *largs):
        self.navi_drawer.anim_to_state('closed')
        self.popup.open(largs)

    def do_synchronization(self, *args):
        # разбить на потоки получилось внутри этих процедур:
        self.navi_drawer.anim_to_state('closed')
        self.pcs.set_progress = self.set_progress
        self.pcs.post_data()
        self.pcs.get_data()
        self.face.show_all_new()

    def exit_program(self, *largs):
        self.this_app.stop()

    def set_progress(self, value):
        self.p_bar.value = value

class MyMoney(App):
    def build(self):
        pcs = PocketClass.Pockets('MyPythonMoney.db')
        p_bar = ProgressBar()
        face = MyFace(pcs, size_hint_y=None)
        face.bind(minimum_height=face.setter('height'))
        # layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        # layout.bind(minimum_height=layout.setter('height'))

        navi_drawer = NavigationDrawer()
        scroll_view = ScrollView(size_hint=(None, None),
                                 size=Window.size,
                                 pos_hint={'center_x':.5, 'center_y':.5},
                                 do_scroll_x=False, do_scroll_y=True)
        back_panel = BackPanel(pcs, navi_drawer, face, p_bar, self)

        scroll_view.add_widget(face)
        m_view = BoxLayout(
            padding=0,
            spacing=0,
            size_hint=(1, None),
            orientation='vertical')
        m_view.add_widget(scroll_view)
        m_view.add_widget(p_bar)
        navi_drawer.add_widget(back_panel)
        navi_drawer.add_widget(m_view)
        return navi_drawer

    def on_stop(self):
        # self.face.pcs.close_db()
        pass

if __name__ == '__main__':
    Builder.load_file('main.kv')
    MyMoney().run()
