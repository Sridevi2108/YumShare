from turtle import Screen
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.core.image import Image as CoreImage
from plyer import filechooser
from PIL import Image as PILImage
from io import BytesIO
import mysql.connector


class ProfileCreationScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileCreationScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.name_input = TextInput(hint_text="Name", multiline=False)
        self.email_input = TextInput(hint_text="Email", multiline=False)
        self.phone_input = TextInput(hint_text="Phone Number", multiline=False)
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False)

        layout.add_widget(Label(text="Create New Profile"))
        layout.add_widget(self.name_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.phone_input)
        layout.add_widget(self.password_input)

        create_profile_button = Button(text="Create Profile")
        create_profile_button.bind(on_press=self.create_profile)
        layout.add_widget(create_profile_button)

        self.add_widget(layout)

    def create_profile(self, instance):
        name = self.name_input.text
        email = self.email_input.text
        phone = self.phone_input.text
        password = self.password_input.text

        if not name or not email or not phone or not password:
            self.show_popup("Error", "All fields are required.")
            return

        db = connect_to_db()
        if db is None:
            self.show_popup("Error", "Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
                           (name, email, phone, hashed_password.decode('utf-8')))
            db.commit()
            user_id = cursor.lastrowid
            App.get_running_app().user_id = user_id

            self.show_popup("Success", "Profile created successfully.")
            self.manager.current = 'profile_screen'
            self.manager.get_screen('profile_screen').set_user_id(user_id)
        except mysql.connector.Error as err:
            self.show_popup("Database Error", f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()