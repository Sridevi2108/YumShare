import mysql.connector
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from plyer import filechooser
import os

class UploadRecipe(Screen):
    def __init__(self, **kwargs):
        super(UploadRecipe, self).__init__(**kwargs)

        # Connect to the database
        self.conn = self.connect_to_database()
        self.cursor = self.conn.cursor()
        self.create_table()

        # Create the main layout with a ScrollView
        root_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView(size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        scroll_view.add_widget(layout)

        # Top section with buttons
        top_section = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10, spacing=10)
        back_btn = Button(text='Back', size_hint_x=None, width=150)
        publish_btn = Button(text='Publish', size_hint_x=None, width=100)
        publish_btn.bind(on_press=self.publish_recipe)

        # Back button action to navigate to the previous screen
        back_btn.bind(on_press=self.go_back)

        top_section.add_widget(back_btn)
        top_section.add_widget(publish_btn)
        layout.add_widget(top_section)

        # Title and author
        title_section = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10, spacing=10)
        title_section.add_widget(Label(text='Upload Your Recipe', font_size=24, size_hint_x=0.7))
        user_label = Label(text='ss @cook_111471207', font_size=18, size_hint_x=0.3, halign='right')
        title_section.add_widget(user_label)
        layout.add_widget(title_section)

        # Button to upload image
        upload_btn = Button(text='Upload from Computer', size_hint_y=None, height=50)
        upload_btn.bind(on_press=self.open_file_chooser)
        layout.add_widget(upload_btn)

        # Image preview
        self.image_preview = Image(size_hint_y=None, height=200)
        self.image_path = None
        layout.add_widget(self.image_preview)

        # Recipe details
        details_layout = GridLayout(cols=2, padding=10, spacing=10, size_hint_y=None, height=150)
        details_layout.add_widget(Label(text='Title:', font_size=18))
        self.title_input = TextInput(hint_text='My best-ever pea soup', font_size=18)
        details_layout.add_widget(self.title_input)
        details_layout.add_widget(Label(text='Serving Size:', font_size=18))
        self.serving_size_input = TextInput(hint_text='2 servings', font_size=18)
        details_layout.add_widget(self.serving_size_input)
        details_layout.add_widget(Label(text='Cook Time:', font_size=18))
        self.cook_time_input = TextInput(hint_text='20 minutes', font_size=18)
        details_layout.add_widget(self.cook_time_input)
        layout.add_widget(details_layout)

        # ScrollView for steps and ingredients
        steps_ingredients_layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        steps_ingredients_layout.bind(minimum_height=steps_ingredients_layout.setter('height'))

        # Ingredients
        steps_ingredients_layout.add_widget(Label(text='Ingredients', font_size=20))
        self.ingredients_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.ingredients_layout.bind(minimum_height=self.ingredients_layout.setter('height'))
        steps_ingredients_layout.add_widget(self.ingredients_layout)

        # Button to add ingredient field
        add_ingredient_btn = Button(text='Add Ingredient', size_hint_y=None, height=40)
        add_ingredient_btn.bind(on_press=self.add_ingredient_field)
        steps_ingredients_layout.add_widget(add_ingredient_btn)

        # Steps
        steps_ingredients_layout.add_widget(Label(text='Steps', font_size=20))
        self.steps_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.steps_list.bind(minimum_height=self.steps_list.setter('height'))
        steps_ingredients_layout.add_widget(self.steps_list)

        # Button to add step field
        add_step_btn = Button(text='Add Step', size_hint_y=None, height=40)
        add_step_btn.bind(on_press=self.add_step_field)
        steps_ingredients_layout.add_widget(add_step_btn)

        layout.add_widget(steps_ingredients_layout)
        root_layout.add_widget(scroll_view)
        self.add_widget(root_layout)

    def go_back(self, instance):
        """Navigate back to the main page or previous screen."""
        self.manager.current = 'main_page'  # Ensure this matches the name of your main screen

    def connect_to_database(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="yumshare"
        )

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                user_id INT NOT NULL,
                                title VARCHAR(100) NOT NULL,
                                ingredients TEXT NOT NULL,
                                steps TEXT NOT NULL,
                                image BLOB,
                                serving_size VARCHAR(50),
                                cook_time VARCHAR(50),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES users(id)
                            )''')
        self.conn.commit()

    def open_file_chooser(self, instance):
        filechooser.open_file(on_selection=self.update_image_preview)

    def update_image_preview(self, selection):
        if selection:
            self.image_path = selection[0]
            self.image_preview.source = self.image_path

    def add_ingredient_field(self, *args):
        ingredient_number = len(self.ingredients_layout.children) + 1
        ingredient_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        ingredient_label = Label(text=f'{ingredient_number}.', size_hint_x=0.1, font_size=18)
        ingredient_text_input = TextInput(hint_text='250g flour', size_hint_x=0.7, font_size=18)
        delete_ingredient_btn = Button(text='Delete', size_hint_x=0.2)
        delete_ingredient_btn.bind(on_press=lambda x: self.remove_ingredient_field(ingredient_layout))
        ingredient_layout.add_widget(ingredient_label)
        ingredient_layout.add_widget(ingredient_text_input)
        ingredient_layout.add_widget(delete_ingredient_btn)
        self.ingredients_layout.add_widget(ingredient_layout)

    def remove_ingredient_field(self, ingredient_layout):
        self.ingredients_layout.remove_widget(ingredient_layout)
        self.update_ingredient_numbers()

    def update_ingredient_numbers(self):
        for index, ingredient_layout in enumerate(reversed(self.ingredients_layout.children), start=1):
            ingredient_label = ingredient_layout.children[2]
            ingredient_label.text = f'{index}.'

    def add_step_field(self, *args):
        step_number = len(self.steps_list.children) + 1
        step_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        step_label = Label(text=f'{step_number}.', size_hint_x=0.1, font_size=18)
        step_text_input = TextInput(hint_text='Mix the flour and water until they thicken.', multiline=True, size_hint_x=0.7, font_size=18)
        delete_step_btn = Button(text='Delete', size_hint_x=0.2)
        delete_step_btn.bind(on_press=lambda x: self.remove_step_field(step_layout))
        step_layout.add_widget(step_label)
        step_layout.add_widget(step_text_input)
        step_layout.add_widget(delete_step_btn)
        self.steps_list.add_widget(step_layout)

    def remove_step_field(self, step_layout):
        self.steps_list.remove_widget(step_layout)
        self.update_step_numbers()

    def update_step_numbers(self):
        for index, step_layout in enumerate(reversed(self.steps_list.children), start=1):
            step_label = step_layout.children[2]
            step_label.text = f'{index}.'

    def publish_recipe(self, instance):
        title = self.title_input.text
        serving_size = self.serving_size_input.text
        cook_time = self.cook_time_input.text
        ingredients = "\n".join([child.children[1].text for child in reversed(self.ingredients_layout.children)])
        steps = "\n".join([child.children[1].text for child in reversed(self.steps_list.children)])

        # Read the image data
        if self.image_path:
            with open(self.image_path, 'rb') as file:
                image_data = file.read()
        else:
            image_data = None

        # Insert recipe data into the database
        self.cursor.execute('''INSERT INTO recipes (user_id, title, ingredients, steps, image, serving_size, cook_time)
                               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                            (1, title, ingredients, steps, image_data, serving_size, cook_time))  # Replace 1 with the actual user_id
        self.conn.commit()

        # Show popup message
        self.show_popup("Recipe uploaded successfully")

    def show_popup(self, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, font_size=18)
        close_button = Button(text='Close', size_hint=(1, 0.2))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_button)

        popup = Popup(title='Success', content=popup_layout, size_hint=(0.8, 0.4), auto_dismiss=False)
        close_button.bind(on_press=popup.dismiss)
        popup.bind(on_dismiss=self.redirect_to_main_page)
        popup.open()

    def redirect_to_main_page(self, instance):
        self.manager.get_screen('main_page').needs_refresh = True
        self.manager.current = 'main_page'

    def save_recipe(self, instance):
        # Implement saving functionality here
        print("Recipe saved!")
        self.manager.current = 'main_page'