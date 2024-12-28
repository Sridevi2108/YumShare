from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
import mysql.connector
from io import BytesIO
from kivy.core.image import Image as CoreImage
from upload_recipe import UploadRecipe  # Import the UploadRecipe screen
from viewrecipes import ViewRecipe  # Import the ViewRecipe screen
from search import search_recipes  # Import the search function

Window.clearcolor = (1, 1, 1, 1)  # Set the background color to white

class ImageButton(ButtonBehavior, BoxLayout):
    def __init__(self, image_source, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'  # Arrange icon and text vertically
        self.size_hint = (None, None)  # Set size dynamically in the layout
        self.icon = Image(source=image_source, size_hint=(1, 0.7))
        self.label = Label(
            text=text,
            size_hint=(1, 0.3),
            font_size='14sp',
            halign='center',
            valign='middle',
        )
        self.label.bind(size=self.label.setter('text_size'))  # Proper text alignment
        self.add_widget(self.icon)
        self.add_widget(self.label)

class MainPage(Screen):
    def __init__(self, screen_manager=None, **kwargs):
        super(MainPage, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        self.header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)
        self.logo = Image(source='logo.png', size_hint=(None, 1), width=50)
        self.title = Label(text='YumShare Dashboard', font_size='24sp', color=(0, 0, 0, 1))
        self.header.add_widget(self.logo)
        self.header.add_widget(self.title)
        self.layout.add_widget(self.header)

        # Search bar with dropdown and cancel button
        self.search_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)
        self.search_criteria = Spinner(
            text='Ingredients',
            values=('Ingredients', 'Serving Size', 'Cook Time'),
            size_hint=(0.25, None),
            height=44
        )
        self.search_input = TextInput(hint_text="Search", size_hint=(0.55, None), height=44)
        self.search_button = Button(text="Search", on_press=self.perform_search, size_hint=(0.1, None), height=44)
        self.cancel_button = Button(text="Cancel", on_press=self.cancel_search, size_hint=(0.1, None), height=44)
        self.search_bar.add_widget(self.search_criteria)
        self.search_bar.add_widget(self.search_input)
        self.search_bar.add_widget(self.search_button)
        self.search_bar.add_widget(self.cancel_button)
        self.layout.add_widget(self.search_bar)

        # Main content area with ScrollView
        self.main_content = ScrollView(size_hint=(1, 0.7))
        self.recipes_layout = GridLayout(cols=3, padding=10, spacing=10, size_hint_y=None)
        self.recipes_layout.bind(minimum_height=self.recipes_layout.setter('height'))
        self.main_content.add_widget(self.recipes_layout)
        self.layout.add_widget(self.main_content)

        # Navigation bar
        self.nav_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.1,
            spacing=10,
        )
        self.create_nav_buttons()
        self.layout.add_widget(self.nav_bar)

        self.add_widget(self.layout)

        # Flag to track whether a refresh is needed
        self.needs_refresh = False

        # Fetch and display recent recipes
        self.fetch_and_display_recipes()

        # Bind to window resize event
        Window.bind(on_resize=self.on_window_resize)

        # Variable to hold the currently active comment box
        self.active_comment_box = None

    def create_nav_buttons(self):
        self.nav_bar.clear_widgets()
        nav_buttons = [
            ('Home', 'homepic.png', self.mainscreen),
            ('Search Recipe', 'search-icon.png', self.mainscreen),
            ('Upload Recipe', 'upload_icon.png', self.go_to_upload_recipe),
            ('Favourites', 'favourite_icon.png', self.mainscreen),
            ('Your Recipes', 'your_recipes.png', self.mainscreen),
            ('Profile', 'user_img.png', self.go_to_profile),
        ]

        # Calculate dynamic button size based on screen width
        button_width = (Window.width - 70) / len(nav_buttons)  # Subtract total spacing
        button_height = Window.height * 0.1

        for text, img_src, callback in nav_buttons:
            nav_btn = ImageButton(image_source=img_src, text=text)
            nav_btn.size = (button_width, button_height)
            nav_btn.bind(on_press=callback)
            self.nav_bar.add_widget(nav_btn)

    def mainscreen(self, instance):
        # Clear current widgets in the recipes_layout before adding new ones
        self.recipes_layout.clear_widgets()

        # Add the welcome label to the recipes_layout
        self.recipes_layout.add_widget(Label(text='Welcome to the YumShare Dashboard!'))

        # Fetch and display recent recipes
        self.fetch_and_display_recipes()

    def perform_search(self, instance):
        criteria = self.search_criteria.text
        query = self.search_input.text

        # Adjust search parameters based on selected criteria
        if criteria == 'Ingredients':
            results = search_recipes(ingredients=query)
        elif criteria == 'Serving Size':
            results = search_recipes(serving_size=query)
        elif criteria == 'Cook Time':
            results = search_recipes(cook_time=query)
        else:
            results = []

        # Clear current widgets in the recipes_layout before adding new ones
        self.recipes_layout.clear_widgets()

        if not results:
            self.recipes_layout.add_widget(Label(text="No recipes found.", font_size='16sp', color=(0, 0, 0, 1)))
        else:
            for recipe in results:
                self.display_recipe(recipe)

    def cancel_search(self, instance):
        # Clear the search input
        self.search_input.text = ""

        # Reset the main content area to display recent recipes
        self.fetch_and_display_recipes()

    def go_to_upload_recipe(self, instance):
        if self.screen_manager:
            self.screen_manager.current = 'upload_recipe'

    def go_to_view_recipe(self, recipe_id):
        if self.screen_manager:
            view_recipe_screen = self.screen_manager.get_screen('view_recipe')
            view_recipe_screen.display_recipe(recipe_id)
            self.screen_manager.current = 'view_recipe'

    def go_to_profile(self, instance):
        """Navigate to the profile screen with user info."""
        if self.screen_manager:
            # Assuming the user is logged in and you have their user_id
            user_id = 1  # Replace with the logged-in user's ID
            profile_screen = self.screen_manager.get_screen('profile_screen')
            profile_screen.set_user_id(user_id)  # Pass the user_id to the profile screen
            self.screen_manager.current = 'profile_screen'

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

    def fetch_and_display_recipes(self):
        """Fetch the most recent recipes from the database and display them."""
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            self.recipes_layout.add_widget(
                Label(text="Failed to connect to the database.", font_size='16sp', color=(1, 0, 0, 1)))
            return

        cursor = db.cursor()
        try:
            # Fetch the 9 most recent recipes
            cursor.execute("SELECT id, title, ingredients, steps, image FROM recipes ORDER BY created_at DESC LIMIT 9")
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

    def post_comment(self, recipe_id, comment_text):
        user_id = App.get_running_app().user_id  # Get logged-in user's ID
        username = App.get_running_app().username  # Get logged-in user's username

        if user_id is None or username is None:
            self.show_popup("Error", "User not logged in.")
            return

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO comments (user_id, recipe_id, username, comment) VALUES (%s, %s, %s, %s)",
                           (user_id, recipe_id, username, comment_text))
            db.commit()
            print("Comment posted successfully!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
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
        like_button = Button(text='Like', size_hint_x=None, width=80)
        like_button.bind(on_press=lambda instance: self.like_recipe(recipe_id, title))
        comment_button = Button(text='Comment', size_hint_x=None, width=80)
        comment_button.bind(on_press=lambda instance: self.show_comment_input(recipe_id, recipe_container))
        view_button = Button(text='View', size_hint_x=None, width=80)
        view_button.bind(on_press=lambda instance: self.go_to_view_recipe(recipe_id))
        buttons_layout.add_widget(like_button)
        buttons_layout.add_widget(comment_button)
        buttons_layout.add_widget(view_button)

        buttons_layout.size_hint_x = 0.9  # Ensure the buttons layout is centered
        buttons_layout.pos_hint = {'center_x': 0.5}

        recipe_container.add_widget(buttons_layout)
        self.recipes_layout.add_widget(recipe_container)

        # Display comments below the buttons
        self.display_comments(recipe_id, recipe_container)

    def on_window_resize(self, instance, width, height):
        """Adjust layout dynamically when the window is resized."""
        self.create_nav_buttons()

    def set_needs_refresh(self):
        """Set the needs_refresh flag to true so that the main page refreshes the recipes."""
        self.needs_refresh = True

    def refresh_recipes(self):
        """Refresh the recipes if needed."""
        if self.needs_refresh:
            self.fetch_and_display_recipes()
            self.needs_refresh = False

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
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def display_comments(self, recipe_id, recipe_container):
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute("SELECT id, user_id, username, comment FROM comments WHERE recipe_id = %s ORDER BY created_at ASC",
                           (recipe_id,))
            comments = cursor.fetchall()

            # Display comments below the recipe
            if comments:
                comments_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100)
                for comment in comments:
                    comment_id, user_id, username, comment_text = comment
                    comment_label = Label(text=f"{username}: {comment_text}", font_size='12sp', color=(0, 0, 0, 1))

                    # Add edit and delete buttons for the user's own comments
                    if user_id == App.get_running_app().user_id:
                        edit_button = Button(text="Edit", size_hint=(None, None), size=(50, 20))
                        delete_button = Button(text="Delete", size_hint=(None, None), size=(50, 20))
                        edit_button.bind(on_press=lambda instance, cid=comment_id: self.show_edit_comment_input(recipe_id, cid, comment_text, recipe_container))
                        delete_button.bind(on_press=lambda instance, cid=comment_id: self.delete_comment(recipe_id, cid, recipe_container))
                        comment_buttons = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
                        comment_buttons.add_widget(edit_button)
                        comment_buttons.add_widget(delete_button)
                        comment_container = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
                        comment_container.add_widget(comment_label)
                        comment_container.add_widget(comment_buttons)
                    else:
                        comment_container = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
                        comment_container.add_widget(comment_label)

                    comments_layout.add_widget(comment_container)

                recipe_container.add_widget(comments_layout)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def show_comment_input(self, recipe_id, recipe_container):
        # Close any existing comment box
        if self.active_comment_box:
            recipe_container.remove_widget(self.active_comment_box)
            self.active_comment_box = None

        # Create a new layout for the comment input and button
        comment_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=100)
        comment_input = TextInput(hint_text="Enter your comment", size_hint=(1, None), height=40)
        comment_button = Button(text="Submit Comment", size_hint=(1, None), height=40)
        comment_button.bind(on_press=lambda instance: self.submit_comment(recipe_id, comment_input.text, comment_layout, recipe_container))

        # Add the comment input and button to the layout
        comment_layout.add_widget(comment_input)
        comment_layout.add_widget(comment_button)

        # Add the comment layout to the recipe container, right below the image
        recipe_container.add_widget(comment_layout, index=2)  # Ensure it is added right below the image

        # Set the active comment box
        self.active_comment_box = comment_layout

    def submit_comment(self, recipe_id, comment_text, comment_layout, recipe_container):
        if comment_text:
            self.post_comment(recipe_id, comment_text)
            recipe_container.remove_widget(comment_layout)
            self.fetch_and_display_recipes()
            self.comment_box_open = False
        else:
            self.show_popup("Error", "Comment cannot be empty.")

    def edit_comment(self, comment_id, recipe_id, recipe_container):
        if self.comment_box_open:
            return
        self.comment_box_open = True

        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute("SELECT comment FROM comments WHERE id = %s", (comment_id,))
            comment_text = cursor.fetchone()[0]

            comment_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=100)
            comment_input = TextInput(text=comment_text, size_hint=(1, None), height=40)
            update_button = Button(text="Update Comment", size_hint=(1, None), height=40)
            update_button.bind(
                on_press=lambda instance: self.update_comment(comment_id, comment_input.text, comment_layout,
                                                              recipe_container))

            comment_layout.add_widget(comment_input)
            comment_layout.add_widget(update_button)

            recipe_container.add_widget(comment_layout, index=2)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()
    def update_comment(self, comment_id, new_text, comment_layout, recipe_container):
        if new_text:
            db = self.connect_to_database()
            if db is None:
                print("Failed to connect to the database.")
                return

            cursor = db.cursor()
            try:
                cursor.execute("UPDATE comments SET comment = %s WHERE id = %s", (new_text, comment_id))
                db.commit()
                print("Comment updated successfully!")
                recipe_container.remove_widget(comment_layout)
                self.fetch_and_display_recipes()
                self.comment_box_open = False
            except mysql.connector.Error as err:
                print(f"Error: {err}")
            finally:
                cursor.close()
                db.close()
        else:
            self.show_popup("Error", "Comment cannot be empty.")

    def delete_comment(self, comment_id, recipe_id, recipe_container):
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
            db.commit()
            print("Comment deleted successfully!")
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

class MainApp(App):
    user_id = None  # Initialize user_id in the app instance
    username = None  # Initialize username in the app instance

    def build(self):
        sm = ScreenManager()

        # Add the MainPage screen
        main_page = MainPage(sm, name='main_page')
        sm.add_widget(main_page)

        # Add the UploadRecipe screen
        upload_recipe = UploadRecipe(name='upload_recipe')
        sm.add_widget(upload_recipe)

        # Add the ViewRecipe screen
        view_recipe = ViewRecipe(name='view_recipe')
        sm.add_widget(view_recipe)

        return sm

if __name__ == "__main__":
    MainApp().run()