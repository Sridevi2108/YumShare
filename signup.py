import mysql.connector
import bcrypt
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

def connect_to_db():
    """Create and return a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",  # Adjust if using a remote database
        user="root",  # Replace with your MySQL username
        password="password",  # Replace with your MySQL password
        database="yumshare"  # The database name
    )

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Root Layout
        root_layout = BoxLayout(orientation="horizontal", size_hint=(1, 1))

        # Left Side: Background Image
        left_image = Image(
            source="food_image.jpg",  # Replace with your background image path
            size_hint=(0.4, 1),
            allow_stretch=True,
            keep_ratio=False
        )
        root_layout.add_widget(left_image)

        # Right Side: Signup Form
        form_layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15), size_hint=(0.6, 1))

        # Header
        header = Label(
            text="[b][color=2ecc71]Create Your Account[/color][/b]",
            markup=True,
            font_size="24sp",
            size_hint=(1, 0.1),
            halign="center",
            valign="middle"
        )
        form_layout.add_widget(header)

        # Name Input Field
        self.name_input = TextInput(
            hint_text="Name",
            size_hint=(1, None),
            height=dp(40),
            font_size="16sp",
            multiline=False,
            padding=[dp(10), dp(10)]
        )
        form_layout.add_widget(self.name_input)

        # Email Input Field
        self.email_input = TextInput(
            hint_text="Email",
            size_hint=(1, None),
            height=dp(40),
            font_size="16sp",
            multiline=False,
            padding=[dp(10), dp(10)]
        )
        form_layout.add_widget(self.email_input)

        # Phone Number Input Field
        self.phone_input = TextInput(
            hint_text="Phone No",
            size_hint=(1, None),
            height=dp(40),
            font_size="16sp",
            multiline=False,
            padding=[dp(10), dp(10)]
        )
        form_layout.add_widget(self.phone_input)

        # Password Input Field
        self.password_input = TextInput(
            hint_text="Password",
            password=True,
            size_hint=(1, None),
            height=dp(40),
            font_size="16sp",
            multiline=False,
            padding=[dp(10), dp(10)]
        )
        form_layout.add_widget(self.password_input)

        # Create Account Button
        create_account_button = Button(
            text="Create Account",
            background_color=(0.2, 0.8, 0.4, 1),
            size_hint=(1, None),
            height=dp(40),
            font_size="16sp"
        )
        create_account_button.bind(on_press=self.on_signup)
        form_layout.add_widget(create_account_button)

        # Back to Login Button
        back_to_login = Button(
            text="[u][color=2ecc71]Already have an account? Log In[/color][/u]",
            markup=True,
            size_hint=(1, None),
            height=dp(40),
            background_color=(1, 1, 1, 0),
            color=(0.2, 0.8, 0.4, 1),
            font_size="14sp"
        )
        back_to_login.bind(on_press=self.go_to_login)
        form_layout.add_widget(back_to_login)

        # Add form layout to root layout
        root_layout.add_widget(form_layout)
        self.add_widget(root_layout)

    def on_signup(self, instance):
        # Get user input
        name = self.name_input.text
        email = self.email_input.text
        phone = self.phone_input.text
        password = self.password_input.text

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert into the database
        db = connect_to_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, phone) VALUES (%s, %s, %s, %s)",
                (name, email, hashed_password, phone)
            )
            db.commit()
            print("User created successfully!")
            # Clear the input fields
            self.name_input.text = ""
            self.email_input.text = ""
            self.phone_input.text = ""
            self.password_input.text = ""
            # Redirect to the login screen
            self.go_to_login(instance)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def go_to_login(self, instance):
        self.manager.current = "login"
