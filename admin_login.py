from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
import mysql.connector

class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super(AdminLoginScreen, self).__init__(**kwargs)
        self.layout = AnchorLayout(anchor_x='center', anchor_y='center', padding=20)
        self.build_ui()
        self.add_widget(self.layout)

    def build_ui(self):
        form_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(0.5, None))
        form_layout.bind(minimum_height=form_layout.setter("height"))

        # Title
        title = Label(
            text="[b][color=#000000]Welcome Back Admin![/color][/b]",
            markup=True,
            font_size='32sp',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=50
        )
        form_layout.add_widget(title)

        # Admin Name Input
        self.adminname_input = TextInput(
            hint_text='Admin Name',
            size_hint=(1, None),
            height=40,
            multiline=False,
            padding=(10, 10)
        )
        form_layout.add_widget(Label(text='Admin Name', size_hint=(1, None), height=40))
        form_layout.add_widget(self.adminname_input)

        # Password Input
        self.password_input = TextInput(
            hint_text='Password',
            size_hint=(1, None),
            height=40,
            multiline=False,
            password=True,
            padding=(10, 10)
        )
        form_layout.add_widget(Label(text='Password', size_hint=(1, None), height=40))
        form_layout.add_widget(self.password_input)

        # Login Button
        login_button = Button(
            text='Login',
            on_release=self.login,
            size_hint=(None, None),
            width=200,
            height=50,
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.8, 0.4, 1)
        )
        form_layout.add_widget(login_button)

        self.layout.add_widget(form_layout)

    def login(self, instance):
        adminname = self.adminname_input.text
        password = self.password_input.text

        if self.verify_credentials(adminname, password):
            self.manager.current = 'admin'
            print("Admin login successful!")
        else:
            self.show_popup("Invalid Credentials", "Incorrect admin name or password.")

    def verify_credentials(self, adminname, password):
        # Verify admin credentials from the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="yumshare"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE adminname = %s AND password = %s", (adminname, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return bool(result)

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()