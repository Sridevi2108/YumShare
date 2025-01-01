from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from io import BytesIO
import mysql.connector
from kivy.core.image import Image as CoreImage

class ImageButton(ButtonBehavior, BoxLayout):
    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.icon = Image(source=image_source, size_hint=(1, 0.7), allow_stretch=True, keep_ratio=True)
        self.label = Label(
            text=text,
            size_hint=(1, 0.3),
            font_size='20sp',
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1)
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.icon)
        self.add_widget(self.label)

class YourRecipesScreen(Screen):
    def __init__(self, **kwargs):
        super(YourRecipesScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with self.canvas.before:
            self.bg = Rectangle(source="background-img.png", pos=self.pos, size=Window.size)
        self.bind(size=self.update_bg, pos=self.update_bg)

        self.header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)
        self.title = Label(text='Your Recipes', font_size='24sp', color=(0, 0, 0, 1))
        self.header.add_widget(self.title)
        self.back_button = Button(text='Back', size_hint_x=None, width=100)
        self.back_button.bind(on_press=self.go_back)
        self.header.add_widget(self.back_button)
        self.layout.add_widget(self.header)

        self.main_content = ScrollView(size_hint=(1, 0.9))
        self.recipes_layout = GridLayout(cols=3, padding=10, spacing=10, size_hint_y=None)
        self.recipes_layout.bind(minimum_height=self.recipes_layout.setter('height'))
        self.main_content.add_widget(self.recipes_layout)
        self.layout.add_widget(self.main_content)

        self.nav_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=80,
            padding=10,
            spacing=10,
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
        for text, img_src, callback in nav_buttons:
            nav_btn = ImageButton(image_source=img_src, text=text)
            nav_btn.size_hint = (1 / len(nav_buttons), 1)
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

    def on_enter(self):
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
        user_id = App.get_running_app().user_id
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            self.recipes_layout.add_widget(
                Label(text="Failed to connect to the database.", font_size='16sp', color=(1, 0, 0, 1)))
            return

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT id, title, ingredients, steps, image, (SELECT COUNT(*) FROM likes WHERE likes.recipe_id = recipes.id) AS likes FROM recipes WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,))
            recipes = cursor.fetchall()
            self.recipes_layout.clear_widgets()
            if not recipes:
                self.recipes_layout.add_widget(Label(text="No recipes found.", font_size='16sp', color=(0, 0, 0, 1)))
                return
            for recipe in recipes:
                self.display_recipe(recipe)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.recipes_layout.add_widget(Label(text="Error fetching recipes.", font_size='16sp', color=(1, 0, 0, 1)))
        finally:
            cursor.close()
            db.close()

    def display_recipe(self, recipe):
        recipe_id, title, ingredients, steps, image_data, likes = recipe
        recipe_container = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(1, None), height=300)
        if image_data:
            image_stream = BytesIO(image_data)
            core_image = CoreImage(image_stream, ext="png")
            recipe_image = Image(texture=core_image.texture, size_hint=(1, None), height=200)
            recipe_container.add_widget(recipe_image)
        else:
            recipe_container.add_widget(Label(text="No image available", font_size='14sp', color=(1, 0, 0, 1)))
        recipe_container.add_widget(Label(text=title, font_size='16sp', halign='center', size_hint_y=None, height=30))
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=2, height=100, spacing=10)

        view_likes_button = Button(text=f'View Likes ({likes})', size_hint_x=2, width=100)
        view_likes_button.bind(on_press=lambda instance, recipe_id=recipe_id: self.show_likes(recipe_id))
        buttons_layout.add_widget(view_likes_button)

        delete_button = Button(text='Delete', size_hint_x=2, width=100)
        delete_button.bind(on_press=lambda instance, recipe_id=recipe_id: self.confirm_delete(recipe_id))
        buttons_layout.add_widget(delete_button)

        buttons_layout.size_hint_x = 0.9
        buttons_layout.pos_hint = {'center_x': 0.5}
        recipe_container.add_widget(buttons_layout)
        self.recipes_layout.add_widget(recipe_container)

    def confirm_delete(self, recipe_id):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Are you sure you want to delete this recipe?', font_size='18sp'))

        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        yes_button = Button(text='Yes', size_hint_x=0.5)
        no_button = Button(text='No', size_hint_x=0.5)

        buttons_layout.add_widget(yes_button)
        buttons_layout.add_widget(no_button)

        content.add_widget(buttons_layout)

        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.8, 0.5))
        yes_button.bind(on_press=lambda instance: self.delete_recipe(recipe_id, popup))
        no_button.bind(on_press=popup.dismiss)
        popup.open()

    def delete_recipe(self, recipe_id, popup):
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            # Delete related comments first
            cursor.execute("DELETE FROM comments WHERE recipe_id = %s", (recipe_id,))
            db.commit()

            # Delete the recipe
            cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
            db.commit()

            self.fetch_and_display_user_recipes()  # Refresh the recipes list
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()
            popup.dismiss()

    def show_likes(self, recipe_id):
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT title, (SELECT COUNT(*) FROM likes WHERE likes.recipe_id = recipes.id) AS likes FROM recipes WHERE id = %s",
                (recipe_id,))
            likes_data = cursor.fetchone()
            if likes_data:
                title, likes = likes_data
                content = BoxLayout(orientation='vertical', padding=10, spacing=10)
                content.add_widget(Label(text=f'Recipe: {title}', font_size='18sp'))
                content.add_widget(Label(text=f'Number of Likes: {likes}', font_size='18sp'))
                ok_button = Button(text="OK", size_hint_y=None, height=50)
                content.add_widget(ok_button)
                popup = Popup(title='Recipe Likes', content=content, size_hint=(0.8, 0.5))
                ok_button.bind(on_press=popup.dismiss)
                popup.open()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def go_back(self, instance):
        self.manager.current = 'main_page'

class MyApp(App):
    user_id = None  # Initialize user_id in the app instance
    username = None  # Initialize username in the app instance

    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(YourRecipesScreen(name='your_recipes'))
        screen_manager.add_widget(Screen(name='main_page'))  # Add the main page screen
        screen_manager.add_widget(Screen(name='upload_recipe'))  # Add the upload recipe screen
        screen_manager.add_widget(Screen(name='favourites'))  # Add the favourites screen
        screen_manager.add_widget(Screen(name='profile_screen'))  # Add the profile screen
        return screen_manager

if __name__ == '__main__':
    MyApp().run()