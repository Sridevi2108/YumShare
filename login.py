import mysql.connector
import bcrypt
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.uix.popup import Popup

def connect_to_db():
    """Create and return a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",  # Adjust if using a remote database
        user="root",  # Replace with your MySQL username
        password="password",  # Replace with your MySQL password
        database="yumshare"  # The database name
    )

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Root Layout (Responsive Horizontal Split)
        root_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1))

        # Left Side: Login Form
        left_side = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(0.6, 1))
        form_layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint=(0.8, None))
        form_layout.bind(minimum_height=form_layout.setter("height"))

        # Logo and Welcome Text
        logo_label = Label(
            text="[b][color=2ecc71]Yumshare[/color][/b]",
            markup=True,
            font_size="32sp",
            halign="center",
            size_hint=(1, None),
            height=dp(40)
        )
        form_layout.add_widget(logo_label)

        welcome_text = Label(
            text="Welcome Back\nSign in with your email address and password.",
            halign="center",
            valign="middle",
            font_size="16sp",
            size_hint=(1, None),
            height=dp(60),
        )
        welcome_text.bind(size=welcome_text.setter("text_size"))
        form_layout.add_widget(welcome_text)

        # Email Input
        self.email_input = TextInput(
            hint_text="Email Address",
            size_hint=(1, None),
            height=dp(40),
            multiline=False
        )
        form_layout.add_widget(self.email_input)

        # Password Input
        self.password_input = TextInput(
            hint_text="Password",
            password=True,
            size_hint=(1, None),
            height=dp(40),
            multiline=False
        )
        form_layout.add_widget(self.password_input)

        # Remember Me and Forgot Password
        extra_options_layout = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(30))

        # Remember Me Checkbox
        remember_me = CheckBox(size_hint=(None, None), size=(dp(20), dp(20)))
        remember_label = Label(
            text="Remember me",
            halign="left",
            valign="middle",
            size_hint=(None, None),
            size=(dp(120), dp(20)),
        )
        extra_options_layout.add_widget(remember_me)
        extra_options_layout.add_widget(remember_label)

        # Forgot Password Link
        forgot_password_label = Label(
            text="[u][color=2ecc71]Forgot Password?[/color][/u]",
            markup=True,
            halign="right",
            valign="middle",
            size_hint=(1, None),
            height=dp(20),
        )
        extra_options_layout.add_widget(forgot_password_label)

        form_layout.add_widget(extra_options_layout)

        # Sign In Button
        sign_in_button = Button(
            text="Sign In",
            size_hint=(1, None),
            height=dp(40),
            background_color=(0.2, 0.8, 0.4, 1),
        )
        sign_in_button.bind(on_press=self.on_login)
        form_layout.add_widget(sign_in_button)

        # Signup Button
        signup_button = Button(
            text="Don't have an account? Sign Up",
            size_hint=(1, None),
            height=dp(40),
            background_color=(1, 1, 1, 0),
            color=(0.2, 0.8, 0.4, 1),
        )
        signup_button.bind(on_press=self.go_to_signup)
        form_layout.add_widget(signup_button)

        left_side.add_widget(form_layout)
        root_layout.add_widget(left_side)

        # Right Side: Background Image
        right_image = Image(
            source="food_image.jpg",  # Replace with your food background image path
            size_hint=(0.4, 1),
            allow_stretch=True,
            keep_ratio=False,
        )
        root_layout.add_widget(right_image)

        self.add_widget(root_layout)

    def on_login(self, instance):
        email = self.email_input.text
        password = self.password_input.text

        if not email or not password:
            self.show_popup("Error", "Please fill in both email and password fields.")
            return

        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, password FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            # Store the user_id and username after successful login
            user_id, username = result[0], result[1]
            App.get_running_app().user_id = user_id  # Store the user_id in the app instance
            App.get_running_app().username = username  # Store the username in the app instance

            # Redirect to the main screen
            self.manager.current = 'main_page'
            print(f"Login successful! User ID: {user_id}, Username: {username}")
        else:
            self.show_popup("Invalid Credentials", "Incorrect email or password.")

        cursor.close()
        db.close()

    def go_to_signup(self, instance):
        self.manager.current = "signup"

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()

class MyApp(App):
    user_id = None
    username = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        # Add other screens (e.g., SignupScreen, MainPage) as needed
        return sm

if __name__ == "__main__":
    MyApp().run()