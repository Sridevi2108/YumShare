from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.image import Image as CoreImage
from plyer import filechooser
from PIL import Image as PILImage
from io import BytesIO
import mysql.connector
import bcrypt

class ImageButton(ButtonBehavior, BoxLayout):
    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.icon = Image(source=image_source, size_hint=(1, 0.7), allow_stretch=True, keep_ratio=True)
        self.label = Label(
            text=text,
            size_hint=(1, 0.3),
            font_size='14sp',
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1)
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.icon)
        self.add_widget(self.label)

class MainPage(Screen):
    def __init__(self, **kwargs):
        super(MainPage, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Main Page'))
        self.add_widget(layout)

class UploadRecipeScreen(Screen):
    def __init__(self, **kwargs):
        super(UploadRecipeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Upload Recipe Screen'))
        self.add_widget(layout)

class FavouritesScreen(Screen):
    def __init__(self, **kwargs):
        super(FavouritesScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Favourites Screen'))
        self.add_widget(layout)

class YourRecipesScreen(Screen):
    def __init__(self, **kwargs):
        super(YourRecipesScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Your Recipes Screen'))
        self.add_widget(layout)

class ProfileScreen(Screen):
    def __init__(self, screen_manager=None, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        root_layout = BoxLayout(orientation='vertical')
        with self.canvas.before:
            self.bg = Rectangle(source="background-img.png", pos=self.pos, size=Window.size)
        self.bind(size=self.update_bg, pos=self.update_bg)

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.photo_section = BoxLayout(orientation='vertical', size_hint_y=0.4, padding=10, spacing=10)
        self.profile_image = Image(source="default-profile.png", size_hint=(None, None), size=(150, 150),
                                   allow_stretch=True, keep_ratio=True)
        self.photo_section.add_widget(self.profile_image)
        self.layout.add_widget(self.photo_section)

        self.details_section = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.name_label = Label(text="Name: ", font_size='18sp', color=(0, 0, 0, 1))
        self.email_label = Label(text="Email: ", font_size='18sp', color=(0, 0, 0, 1))
        self.phone_label = Label(text="Phone: ", font_size='18sp', color=(0, 0, 0, 1))
        self.bio_label = Label(text="Bio: ", font_size='18sp', color=(0, 0, 0, 1))
        self.hobby_label = Label(text="Hobby: ", font_size='18sp', color=(0, 0, 0, 1))

        self.details_section.add_widget(self.name_label)
        self.details_section.add_widget(self.email_label)
        self.details_section.add_widget(self.phone_label)
        self.details_section.add_widget(self.bio_label)
        self.details_section.add_widget(self.hobby_label)
        self.layout.add_widget(self.details_section)

        self.button_section = BoxLayout(orientation='horizontal', spacing=20, padding=10, size_hint_y=0.2)
        self.update_button = Button(text="Update Profile", size_hint=(None, None), size=(150, 50),
                                    background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1), background_normal='')
        self.update_button.bind(on_press=self.open_edit_popup)

        self.account_button = Button(text="Account", size_hint=(None, None), size=(150, 50),
                                     background_color=(0.8, 0.4, 0.4, 1), color=(1, 1, 1, 1), background_normal='')
        self.account_button.bind(on_press=self.open_account_popup)

        self.button_section.add_widget(self.update_button)
        self.button_section.add_widget(self.account_button)
        self.layout.add_widget(self.button_section)

        self.add_widget(self.layout)

        self.user_id = None
        self.nav_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        self.layout.add_widget(self.nav_bar)
        self.create_nav_buttons()

        # Bind the window size change to the update_nav_buttons method
        Window.bind(size=self.update_nav_buttons)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def create_nav_buttons(self):
        self.nav_bar.clear_widgets()
        nav_buttons = [
            ('Main Page', 'homepic.png', self.go_to_main_page),
            ('Upload Recipe', 'upload_icon.png', self.go_to_upload_recipe),
            ('Favourites', 'favourite_icon.png', self.go_to_favourites),
            ('Your Recipes', 'your_recipes.png', self.go_to_your_recipes),
            ('Profile', 'user_img.png', self.go_to_profile),
        ]

        button_width = (Window.width - 70) / len(nav_buttons)
        button_height = Window.height * 0.1

        for text, img_src, callback in nav_buttons:
            nav_btn = ImageButton(image_source=img_src, text=text)
            nav_btn.size = (button_width, button_height)
            nav_btn.bind(on_press=callback)
            self.nav_bar.add_widget(nav_btn)

    def update_nav_buttons(self, *args):
        # Update the navigation buttons' sizes dynamically
        button_width = (Window.width - 70) / len(self.nav_bar.children)
        button_height = Window.height * 0.1
        for nav_btn in self.nav_bar.children:
            nav_btn.size = (button_width, button_height)

    def go_to_main_page(self, instance):
        self.manager.current = 'main_page'

    def go_to_upload_recipe(self, instance):
        self.manager.current = 'upload_recipe'

    def go_to_favourites(self, instance):
        self.manager.current = 'favourites'

    def go_to_your_recipes(self, instance):
        self.manager.current = 'your_recipes'

    def go_to_profile(self, instance):
        self.manager.current = 'profile_screen'

    def on_pre_enter(self):
        self.fetch_profile_data()

    def set_user_id(self, user_id):
        self.user_id = user_id
        self.fetch_profile_data()

    def fetch_profile_data(self):
        if not self.user_id:
            print("User ID is not set.")
            return

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute("SELECT name, email, phone, profile_photo, bio, hobby FROM users WHERE id = %s",
                           (self.user_id,))
            user_info = cursor.fetchone()

            if user_info:
                name, email, phone, profile_photo, bio, hobby = user_info
                self.name_label.text = f"Name: {name}"
                self.email_label.text = f"Email: {email}"
                self.phone_label.text = f"Phone: {phone}"
                self.bio_label.text = f"Bio: {bio}"
                self.hobby_label.text = f"Hobby: {hobby}"

                if profile_photo:
                    image_stream = BytesIO(profile_photo)
                    core_image = CoreImage(image_stream, ext="png")
                    self.profile_image.texture = core_image.texture
            else:
                # Clear labels if no data is found
                self.name_label.text = "Name: "
                self.email_label.text = "Email: "
                self.phone_label.text = "Phone: "
                self.bio_label.text = "Bio: "
                self.hobby_label.text = "Hobby: "

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def open_edit_popup(self, instance):
        if self.user_id is None:
            print("User ID is not set.")
            return

        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.email_input = TextInput(text=self.email_label.text.replace("Email: ", ""), hint_text='Enter email')
        self.phone_input = TextInput(text=self.phone_label.text.replace("Phone: ", ""), hint_text='Enter phone number')
        self.bio_input = TextInput(text=self.bio_label.text.replace("Bio: ", ""), hint_text='Enter bio', multiline=True)
        self.hobby_input = TextInput(text=self.hobby_label.text.replace("Hobby: ", ""), hint_text='Enter hobby')

        self.photo_button = Button(text='Choose Profile Photo')
        self.photo_button.bind(on_press=self.choose_photo)

        save_button = Button(text='Save', size_hint=(None, None), size=(100, 50))
        save_button.bind(on_press=self.save_profile_details)

        popup_content.add_widget(Label(text='Update Profile Details'))
        popup_content.add_widget(self.email_input)
        popup_content.add_widget(self.phone_input)
        popup_content.add_widget(self.bio_input)
        popup_content.add_widget(self.hobby_input)
        popup_content.add_widget(self.photo_button)
        popup_content.add_widget(save_button)

        self.popup = Popup(title='Edit Profile', content=popup_content, size_hint=(0.8, 0.8))
        self.popup.open()

    def open_account_popup(self, instance):
        if self.user_id is None:
            print("User ID is not set.")
            return

        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.name_input = TextInput(text=self.name_label.text.replace("Name: ", ""), hint_text='Enter name')
        self.email_input = TextInput(text=self.email_label.text.replace("Email: ", ""), hint_text='Enter email')
        self.phone_input = TextInput(text=self.phone_label.text.replace("Phone: ", ""), hint_text='Enter phone number')
        self.password_input = TextInput(hint_text='Enter new password', password=True)

        save_button = Button(text='Save', size_hint=(None, None), size=(100, 50))
        save_button.bind(on_press=self.save_account_details)

        popup_content.add_widget(Label(text='Update Account Details'))
        popup_content.add_widget(self.name_input)
        popup_content.add_widget(self.email_input)
        popup_content.add_widget(self.phone_input)
        popup_content.add_widget(self.password_input)
        popup_content.add_widget(save_button)

        self.account_popup = Popup(title='Edit Account', content=popup_content, size_hint=(0.8, 0.8))
        self.account_popup.open()

    def choose_photo(self, instance):
        filechooser.open_file(on_selection=self.on_photo_selected)

    def on_photo_selected(self, selection):
        if selection:
            self.photo_path = selection[0]

    def save_profile_details(self, instance):
        if not self.user_id:
            print("User ID is not set.")
            return

        email = self.email_input.text
        phone = self.phone_input.text
        bio = self.bio_input.text
        hobby = self.hobby_input.text
        profile_photo = None

        if hasattr(self, 'photo_path'):
            with open(self.photo_path, 'rb') as file:
                image = PILImage.open(file)
                image = image.resize((200, 200), PILImage.LANCZOS)
                image_byte_array = BytesIO()
                image.save(image_byte_array, format='PNG')
                profile_photo = image_byte_array.getvalue()

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (self.user_id,))
            user_exists = cursor.fetchone()[0] > 0

            if user_exists:
                cursor.execute("UPDATE users SET email = %s, phone = %s, bio = %s, hobby = %s WHERE id = %s",
                               (email, phone, bio, hobby, self.user_id))
                if profile_photo:
                    cursor.execute("UPDATE users SET profile_photo = %s WHERE id = %s",
                                   (profile_photo, self.user_id))
            else:
                cursor.execute("""
                    INSERT INTO users (id, email, phone, bio, hobby, profile_photo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (self.user_id, email, phone, bio, hobby, profile_photo))

            db.commit()
            self.popup.dismiss()
            self.fetch_profile_data()

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def save_account_details(self, instance):
        if not self.user_id:
            print("User ID is not set.")
            return

        name = self.name_input.text
        email = self.email_input.text
        phone = self.phone_input.text
        password = self.password_input.text

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE users SET name = %s, email = %s, phone = %s, password = %s WHERE id = %s",
                               (name, email, phone, hashed_password.decode('utf-8'), self.user_id))
            else:
                cursor.execute("UPDATE users SET name = %s, email = %s, phone = %s WHERE id = %s",
                               (name, email, phone, self.user_id))

            db.commit()
            self.account_popup.dismiss()
            self.fetch_profile_data()

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()
    def connect_to_database(self):
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database="yumshare"
            )
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def go_back(self, instance):
        self.manager.current = 'main_page'

class TestApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainPage(name='main_page'))
        sm.add_widget(UploadRecipeScreen(name='upload_recipe'))
        sm.add_widget(FavouritesScreen(name='favourites'))
        sm.add_widget(YourRecipesScreen(name='your_recipes'))
        sm.add_widget(ProfileScreen(name='profile_screen', screen_manager=sm))
        return sm

if __name__ == '__main__':
    TestApp().run()