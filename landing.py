from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp

class LandingScreen(Screen):
    def __init__(self, **kwargs):
        super(LandingScreen, self).__init__(**kwargs)
        self.layout = AnchorLayout(anchor_x='center', anchor_y='center', padding=20)
        self.build_ui()
        self.add_widget(self.layout)

    def build_ui(self):
        form_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(0.5, None))
        form_layout.bind(minimum_height=form_layout.setter("height"))

        # User Button
        user_button = Button(
            text='User',
            on_release=self.go_to_user,
            size_hint=(None, None),
            width=200,
            height=50,
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.8, 0.4, 1)
        )
        form_layout.add_widget(user_button)

        # Admin Button
        admin_button = Button(
            text='Admin',
            on_release=self.go_to_admin,
            size_hint=(None, None),
            width=200,
            height=50,
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.8, 0.4, 1)
        )
        form_layout.add_widget(admin_button)

        self.layout.add_widget(form_layout)

    def go_to_user(self, instance):
        self.manager.current = 'login'

    def go_to_admin(self, instance):
        self.manager.current = 'adminlogin'