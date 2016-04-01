from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class SMApp(App):

    def build(self):
        layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        root = ScrollView(size_hint=(None, None), size=(400, 400),
            pos_hint={'center_x':.5, 'center_y':.5})
        root.add_widget(layout)

        for i in range(30):
            btn = Label(text=str(i), size_hint_y=None, height=40)
            layout.add_widget(btn)

        return root

if __name__ == '__main__':
    SMApp().run()