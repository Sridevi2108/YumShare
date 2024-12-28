from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.uix.popup import Popup  # Import the Popup class
import mysql.connector
from io import BytesIO
from kivy.core.image import Image as CoreImage


class YourRecipesScreen(Screen):
    def __init__(self, **kwargs):
        super(YourRecipesScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        self.header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)
        self.title = Label(text='Your Recipes', font_size='24sp', color=(0, 0, 0, 1))
        self.header.add_widget(self.title)

        # Back button
        self.back_button = Button(text='Back', size_hint_x=None, width=100)
        self.back_button.bind(on_press=self.go_back)
        self.header.add_widget(self.back_button)

        self.layout.add_widget(self.header)

        # Main content area with ScrollView
        self.main_content = ScrollView(size_hint=(1, 0.9))
        self.recipes_layout = GridLayout(cols=3, padding=10, spacing=10, size_hint_y=None)
        self.recipes_layout.bind(minimum_height=self.recipes_layout.setter('height'))
        self.main_content.add_widget(self.recipes_layout)
        self.layout.add_widget(self.main_content)

        self.add_widget(self.layout)

    def on_enter(self):
        """Fetch and display user recipes each time the screen is entered."""
        self.fetch_and_display_user_recipes()

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

    def fetch_and_display_user_recipes(self):
        """Fetch the recipes uploaded by the currently logged-in user and display them."""
        user_id = App.get_running_app().user_id

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            self.recipes_layout.add_widget(
                Label(text="Failed to connect to the database.", font_size='16sp', color=(1, 0, 0, 1)))
            return

        cursor = db.cursor()
        try:
            # Fetch the recipes uploaded by the user
            cursor.execute(
                "SELECT id, title, ingredients, steps, image FROM recipes WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,))
            recipes = cursor.fetchall()

            # Clear current recipes from the layout
            self.recipes_layout.clear_widgets()

            if not recipes:
                self.recipes_layout.add_widget(Label(text="No recipes found.", font_size='16sp', color=(0, 0, 0, 1)))
                return

            # Display fetched recipes
            for recipe in recipes:
                self.display_recipe(recipe)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.recipes_layout.add_widget(Label(text="Error fetching recipes.", font_size='16sp', color=(1, 0, 0, 1)))
        finally:
            cursor.close()
            db.close()

    def display_recipe(self, recipe):
        recipe_id, title, ingredients, steps, image_data = recipe

        # Recipe container
        recipe_container = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(1, None), height=300)

        # Display image if available
        if image_data:
            image_stream = BytesIO(image_data)
            core_image = CoreImage(image_stream, ext="png")  # Adjust 'png' to the image format
            recipe_image = Image(texture=core_image.texture, size_hint=(1, None), height=200)
            recipe_container.add_widget(recipe_image)
        else:
            recipe_container.add_widget(Label(text="No image available", font_size='14sp', color=(1, 0, 0, 1)))

        # Add title below the image
        recipe_container.add_widget(Label(text=title, font_size='16sp', halign='center', size_hint_y=None, height=30))

        # Add buttons below the image
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        view_button = Button(text='View', size_hint_x=None, width=80)
        view_button.bind(on_press=lambda instance: self.go_to_view_recipe(recipe_id))
        buttons_layout.add_widget(view_button)

        buttons_layout.size_hint_x = 0.9  # Ensure the buttons layout is centered
        buttons_layout.pos_hint = {'center_x': 0.5}

        recipe_container.add_widget(buttons_layout)
        self.recipes_layout.add_widget(recipe_container)

    def go_to_view_recipe(self, recipe_id):
        if self.manager:
            view_recipe_screen = self.manager.get_screen('view_recipe')
            view_recipe_screen.display_recipe(recipe_id)
            self.manager.current = 'view_recipe'

    def go_back(self, instance):
        """Navigate back to the main page or previous screen."""
        self.manager.current = 'main_page'  # Ensure this matches the name of your main screen

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()