from kivy.app import App
from kivy.graphics import Rectangle
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.image import Image as CoreImage
from io import BytesIO
import mysql.connector
from kivy.core.window import Window
from kivy.uix.popup import Popup
from PIL import Image as PILImage
from fpdf import FPDF


class ImageButton(ButtonBehavior, BoxLayout):
    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'  # Arrange icon and text vertically
        self.size_hint = (None, None)  # Set size dynamically in the layout
        self.icon = Image(source=image_source, size_hint=(1, 0.7), allow_stretch=True, keep_ratio=True)
        self.label = Label(
            text=text,
            size_hint=(1, 0.3),
            font_size='20sp',  # Increased font size to match MainPage
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1)
        )
        self.label.bind(size=self.label.setter('text_size'))  # Proper text alignment
        self.add_widget(self.icon)
        self.add_widget(self.label)


class Favourites(Screen):
    def __init__(self, **kwargs):
        super(Favourites, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with self.canvas.before:
            self.bg = Rectangle(source="background-img.png", pos=self.pos, size=Window.size)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Header with Back button and title
        self.header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10, spacing=10)
        self.back_button = Button(text="Back", size_hint_x=None, width=80)
        self.back_button.bind(on_press=self.go_back)
        self.title_label = Label(text="Your Liked Recipes", font_size='24sp', size_hint_x=1)
        self.header.add_widget(self.back_button)
        self.header.add_widget(self.title_label)

        self.layout.add_widget(self.header)

        # ScrollView to display the recipes
        self.scroll_view = ScrollView()
        self.recipes_layout = GridLayout(cols=1, padding=10, spacing=10, size_hint_y=None)
        self.recipes_layout.bind(minimum_height=self.recipes_layout.setter('height'))
        self.scroll_view.add_widget(self.recipes_layout)

        self.layout.add_widget(self.scroll_view)

        # Navigation bar
        self.nav_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=80,  # Increased height for the navigation bar
            padding=10,  # Add padding to the navigation bar
            spacing=10,  # Add spacing between buttons
        )
        self.create_nav_buttons()
        self.layout.add_widget(self.nav_bar)

        self.add_widget(self.layout)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def create_nav_buttons(self):
        self.nav_bar.clear_widgets()
        nav_buttons = [
            ('Home', 'homepic.png', self.go_to_main_page),
            ('Upload Recipe', 'upload_icon.png', self.go_to_upload_recipe),
            ('Favourites', 'favourite_icon.png', self.go_to_favourites),
            ('Your Recipes', 'your_recipes.png', self.go_to_your_recipes),
            ('Profile', 'user_img.png', self.go_to_profile),
        ]

        # Set size_hint_x for dynamic button width
        for text, img_src, callback in nav_buttons:
            nav_btn = ImageButton(image_source=img_src, text=text)
            nav_btn.size_hint = (1 / len(nav_buttons), 1)  # Dynamic width based on the number of buttons
            nav_btn.bind(on_press=callback)
            self.nav_bar.add_widget(nav_btn)

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

    def go_back(self, instance):
        """Navigate back to the main screen."""
        self.manager.current = 'main_page'

    def set_user_id(self, user_id):
        """Set the user ID and fetch the favorite recipes."""
        self.user_id = user_id
        self.fetch_and_display_favorites()

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

    def fetch_and_display_favorites(self):
        """Fetch the favorite recipes for the logged-in user and display them."""
        if not hasattr(self, 'user_id'):
            print("User ID is not set.")
            return

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            # Query to fetch favorite recipes for the user
            cursor.execute("""
                SELECT r.id, r.title, r.ingredients, r.steps, r.image, r.serving_size, r.cook_time
                FROM recipes r
                JOIN likes l ON r.id = l.recipe_id
                WHERE l.user_id = %s
                ORDER BY l.time DESC
            """, (self.user_id,))

            recipes = cursor.fetchall()

            # Clear the current list of recipes
            self.recipes_layout.clear_widgets()

            if not recipes:
                self.recipes_layout.add_widget(Label(text="No liked recipes found.", font_size='16sp'))
                return

            # Display the fetched recipes
            for recipe in recipes:
                self.display_recipe(recipe)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def display_recipe(self, recipe):
        """Display a recipe in the favorites list."""
        recipe_id, title, ingredients, steps, image_data, serving_size, cook_time = recipe

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

        # Add buttons below the title
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        remove_button = Button(text='Remove from Likes', size_hint_x=1, width=10)
        remove_button.bind(on_press=lambda instance: self.remove_from_likes(recipe_id))
        pdf_button = Button(text='Download PDF', size_hint_x=1, width=10)
        pdf_button.bind(on_press=lambda instance: self.download_recipe(recipe_id))
        buttons_layout.add_widget(remove_button)
        buttons_layout.add_widget(pdf_button)

        recipe_container.add_widget(buttons_layout)
        self.recipes_layout.add_widget(recipe_container)

    def remove_from_likes(self, recipe_id):
        """Remove a recipe from the likes."""
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM likes WHERE user_id = %s AND recipe_id = %s", (self.user_id, recipe_id))
            db.commit()
            self.fetch_and_display_favorites()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def download_recipe(self, recipe_id):
        """Download the recipe as a PDF."""
        try:
            connection = mysql.connector.connect(
                host='localhost', user='root', password='password', database='yumshare'
            )
            cursor = connection.cursor(dictionary=True)
            query = "SELECT title, ingredients, steps, cook_time, serving_size, image FROM recipes WHERE id = %s"
            cursor.execute(query, (recipe_id,))
            recipe = cursor.fetchone()
            connection.close()

            if recipe:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Title
                pdf.cell(200, 10, txt=recipe['title'], ln=True, align='C')

                # Image
                if recipe['image']:
                    temp_image_path = f'temp_recipe_image_for_pdf_{recipe_id}.png'
                    with open(temp_image_path, 'wb') as f:
                        f.write(recipe['image'])
                    image = PILImage.open(temp_image_path)
                    image = image.resize((150, 150))
                    image.save(temp_image_path)
                    pdf.image(temp_image_path, x=80, y=20, w=50, h=50)

                pdf.ln(60)  # Move below the image

                # Ingredients, Steps, Cooking Time, and Serving Size
                pdf.multi_cell(0, 10, txt=f"Ingredients:\n{recipe['ingredients']}")
                pdf.multi_cell(0, 10, txt=f"Steps:\n{recipe['steps']}")
                pdf.cell(0, 10, txt=f"Cooking Time: {recipe['cook_time']} mins", ln=True)
                pdf.cell(0, 10, txt=f"Serving Size: {recipe['serving_size']}", ln=True)

                app = App.get_running_app()
                pdf_output_path = f"{app.username}_{recipe['title']}.pdf"
                pdf.output(pdf_output_path)
                print("Recipe PDF downloaded successfully!")

                # Show popup notification
                self.show_download_popup(pdf_output_path)
        except Exception as e:
            print(f"Error downloading recipe as PDF: {e}")

    def show_download_popup(self, pdf_path):
        """Show a popup notification when the PDF is successfully downloaded."""
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=f"PDF successfully downloaded:\n{pdf_path}"))
        close_btn = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(close_btn)

        popup = Popup(title="Download Complete", content=content, size_hint=(0.8, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class MainPage(Screen):
    # ... [other methods and code]

    def like_recipe(self, recipe_id, recipe_name):
        """Handle the like functionality."""
        user_id = App.get_running_app().user_id  # Access the user_id from the app instance
        username = App.get_running_app().username  # Access the username from the app instance

        if user_id is None or username is None:
            self.show_popup("Error", "User ID or Username is not set. Please log in again.")
            return

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            # Check if the user has already liked the recipe
            cursor.execute("SELECT * FROM likes WHERE user_id = %s AND recipe_id = %s", (user_id, recipe_id))
            existing_like = cursor.fetchone()

            if existing_like:
                print("User has already liked this recipe.")
                return

            # Insert a new like record
            cursor.execute("INSERT INTO likes (user_id, username, recipe_id, recipe_name) VALUES (%s, %s, %s, %s)",
                           (user_id, username, recipe_id, recipe_name))
            db.commit()
            print("Recipe liked successfully!")

            # Refresh the recipes to show the updated number of likes
            self.fetch_and_display_recipes()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
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


class MyApp(App):
    user_id = None  # Initialize user_id in the app instance
    username = None  # Initialize username in the app instance

    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(Favourites(name='favourites'))
        screen_manager.add_widget(Screen(name='main_page'))  # Add the main page screen
        screen_manager.add_widget(Screen(name='upload_recipe'))  # Add the upload recipe screen
        screen_manager.add_widget(Screen(name='your_recipes'))  # Add the your recipes screen
        screen_manager.add_widget(Screen(name='profile_screen'))  # Add the profile screen
        screen_manager.add_widget(Screen(name='view_recipe'))  # Add the view recipe screen
        return screen_manager


if __name__ == '__main__':
    MyApp().run()