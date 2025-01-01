import os
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from fpdf import FPDF
import mysql.connector
from PIL import Image as PILImage


class RecipePopup(Popup):
    def __init__(self, recipe_details, comments, **kwargs):
        super().__init__(**kwargs)
        self.recipe_details = recipe_details
        self.comments = comments
        self.title = f"{recipe_details['title']} - Comments"
        self.size_hint = (0.9, 0.8)

        # Main layout of the popup
        self.popup_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)

        # Left side: Image
        if recipe_details['image']:
            temp_image_path = f'temp_popup_image_{recipe_details["id"]}.png'
            with open(temp_image_path, 'wb') as f:
                f.write(recipe_details['image'])
            self.popup_layout.add_widget(Image(source=temp_image_path, size_hint=(0.5, 1)))

        # Right side: Details and comments
        self.right_layout = BoxLayout(orientation='vertical', spacing=10)
        self.right_layout.add_widget(Label(
            text=f"[b]{recipe_details['title']}[/b]", markup=True, font_size=18
        ))

        # Comments section in a scrollable view
        self.comments_box = ScrollView(size_hint=(1, 0.7))
        self.comments_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.comments_layout.bind(minimum_height=self.comments_layout.setter('height'))
        self.load_comments()
        self.comments_box.add_widget(self.comments_layout)
        self.right_layout.add_widget(self.comments_box)

        # Add comment input field and button
        self.comment_input = TextInput(hint_text="Add your comment here...", size_hint_y=None, height=40)
        self.post_comment_btn = Button(text="Post Comment", size_hint_y=None, height=40)
        self.post_comment_btn.bind(on_press=self.post_comment)
        self.right_layout.add_widget(self.comment_input)
        self.right_layout.add_widget(self.post_comment_btn)

        # Add back button
        back_btn = Button(text="Back", size_hint_y=None, height=40)
        back_btn.bind(on_press=self.dismiss)
        self.right_layout.add_widget(back_btn)

        self.popup_layout.add_widget(self.right_layout)
        self.add_widget(self.popup_layout)

    def load_comments(self):
        """Load comments into the comments layout."""
        self.comments_layout.clear_widgets()
        app = App.get_running_app()
        for comment in self.comments:
            comment_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=10)
            comment_label = Label(
                text=f"{comment['username']}: {comment['comment']}",
                font_size=14, size_hint_x=0.7
            )
            comment_box.add_widget(comment_label)
            # Only show edit and delete buttons for the user's own comments
            if comment['user_id'] == app.user_id:
                edit_btn = Button(text="Edit", size_hint_x=0.15)
                edit_btn.bind(on_press=lambda instance, c=comment: self.edit_comment(c))
                delete_btn = Button(text="Delete", size_hint_x=0.15)
                delete_btn.bind(on_press=lambda instance, c=comment: self.delete_comment(c))
                comment_box.add_widget(edit_btn)
                comment_box.add_widget(delete_btn)
            self.comments_layout.add_widget(comment_box)

    def post_comment(self, instance):
        """Post a new comment to the database."""
        comment_text = self.comment_input.text.strip()
        if comment_text:
            try:
                connection = mysql.connector.connect(
                    host='localhost', user='root', password='password', database='yumshare'
                )
                cursor = connection.cursor()
                app = App.get_running_app()
                query = "INSERT INTO comments (user_id, recipe_id, username, comment) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (app.user_id, self.recipe_details['id'], app.username, comment_text))
                connection.commit()
                connection.close()
                self.comment_input.text = ""  # Clear the input field
                print("Comment posted successfully!")

                # Refresh comments
                self.refresh_comments()
            except Exception as e:
                print(f"Error posting comment: {e}")

    def edit_comment(self, comment):
        """Edit an existing comment."""
        app = App.get_running_app()
        if comment['user_id'] != app.user_id:
            print("You can only edit your own comments.")
            return

        edit_popup = Popup(title="Edit Comment", size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical', padding=10)

        comment_input = TextInput(text=comment['comment'], size_hint_y=None, height=40)
        save_btn = Button(text="Save", size_hint_y=None, height=40)
        cancel_btn = Button(text="Cancel", size_hint_y=None, height=40)

        def save_edit(instance):
            new_comment = comment_input.text.strip()
            if new_comment:
                try:
                    connection = mysql.connector.connect(
                        host='localhost', user='root', password='password', database='yumshare'
                    )
                    cursor = connection.cursor()
                    query = "UPDATE comments SET comment = %s WHERE id = %s"
                    cursor.execute(query, (new_comment, comment['id']))
                    connection.commit()
                    connection.close()
                    print("Comment updated successfully!")
                    edit_popup.dismiss()
                    self.refresh_comments()
                except Exception as e:
                    print(f"Error updating comment: {e}")

        save_btn.bind(on_press=save_edit)
        cancel_btn.bind(on_press=edit_popup.dismiss)

        content.add_widget(comment_input)
        content.add_widget(save_btn)
        content.add_widget(cancel_btn)
        edit_popup.content = content
        edit_popup.open()

    def delete_comment(self, comment):
        """Delete an existing comment."""
        app = App.get_running_app()
        if comment['user_id'] != app.user_id:
            print("You can only delete your own comments.")
            return

        try:
            connection = mysql.connector.connect(
                host='localhost', user='root', password='password', database='yumshare'
            )
            cursor = connection.cursor()
            query = "DELETE FROM comments WHERE id = %s"
            cursor.execute(query, (comment['id'],))
            connection.commit()
            connection.close()
            print("Comment deleted successfully!")
            self.refresh_comments()
        except Exception as e:
            print(f"Error deleting comment: {e}")

    def refresh_comments(self):
        """Refresh the comments section after posting a new comment."""
        try:
            connection = mysql.connector.connect(
                host='localhost', user='root', password='password', database='yumshare'
            )
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, user_id, username, comment FROM comments WHERE recipe_id = %s ORDER BY created_at ASC"
            cursor.execute(query, (self.recipe_details['id'],))
            self.comments = cursor.fetchall()
            connection.close()
            self.load_comments()  # Reload comments into the layout
        except Exception as e:
            print(f"Error refreshing comments: {e}")


class ViewRecipe(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recipe_id = None  # Store the ID of the recipe being viewed
        self.layout = None  # Main layout for the screen

    def set_recipe_id(self, recipe_id):
        self.recipe_id = recipe_id  # Set the current recipe ID
        self.clear_widgets()  # Clear existing widgets before adding new ones

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)

        # Load recipe details and UI elements
        self.load_recipe_details()
        self.add_view_comments_button()
        self.add_download_button()
        self.add_back_button()

    def load_recipe_details(self):
        try:
            connection = mysql.connector.connect(
                host='localhost', user='root', password='password', database='yumshare'
            )
            cursor = connection.cursor(dictionary=True)

            # Fetch recipe details using the recipe ID
            query = "SELECT title, ingredients, steps, image, cook_time, serving_size FROM recipes WHERE id = %s"
            cursor.execute(query, (self.recipe_id,))
            recipe = cursor.fetchone()
            connection.close()

            if recipe:
                # Display the recipe title
                self.layout.add_widget(Label(
                    text=f"[b]{recipe['title']}[/b]", markup=True, font_size=24
                ))

                # Display the recipe image if available
                if recipe['image']:
                    temp_image_path = f'temp_recipe_image_{self.recipe_id}.png'
                    with open(temp_image_path, 'wb') as f:
                        f.write(recipe['image'])
                    self.layout.add_widget(Image(source=temp_image_path, size_hint=(1, None), height=300))

                # Display ingredients, steps, cooking time, and serving size
                self.layout.add_widget(Label(
                    text=f"Ingredients:\n{recipe['ingredients']}", font_size=16
                ))
                self.layout.add_widget(Label(
                    text=f"Steps:\n{recipe['steps']}", font_size=16
                ))
                self.layout.add_widget(Label(
                    text=f"Cooking Time: {recipe['cook_time']} mins", font_size=16
                ))
                self.layout.add_widget(Label(
                    text=f"Serving Size: {recipe['serving_size']}", font_size=16
                ))
            else:
                # Show error if recipe is not found
                self.layout.add_widget(Label(text="Recipe not found.", font_size=18))
        except Exception as e:
            # Handle errors while loading recipe details
            self.layout.add_widget(Label(text="Failed to load recipe details.", font_size=18))
            print(f"Error: {e}")

    def add_view_comments_button(self):
        # Button to open the comments popup
        view_comments_btn = Button(text="View Comments", size_hint_y=None, height=40)
        view_comments_btn.bind(on_press=self.open_comments_popup)
        self.layout.add_widget(view_comments_btn)

    def open_comments_popup(self, instance):
        try:
            connection = mysql.connector.connect(
                host='localhost', user='root', password='password', database='yumshare'
            )
            cursor = connection.cursor(dictionary=True)

            # Fetch comments for the current recipe
            query = "SELECT id, user_id, username, comment FROM comments WHERE recipe_id = %s ORDER BY created_at ASC"
            cursor.execute(query, (self.recipe_id,))
            comments = cursor.fetchall()

            # Fetch recipe details for the popup header
            query = "SELECT title, image FROM recipes WHERE id = %s"
            cursor.execute(query, (self.recipe_id,))
            recipe_details = cursor.fetchone()

            connection.close()

            if recipe_details:
                recipe_details['id'] = self.recipe_id
                popup = RecipePopup(recipe_details, comments)
                popup.open()
        except Exception as e:
            print(f"Error fetching comments: {e}")

    def add_download_button(self):
        # Button to download the recipe as a PDF
        download_btn = Button(text="Download Recipe as PDF", size_hint_y=None, height=40)
        download_btn.bind(on_press=self.download_recipe)
        self.layout.add_widget(download_btn)

    def download_recipe(self, instance):
        try:
            connection = mysql.connector.connect(
                host='localhost', user='root', password='password', database='yumshare'
            )
            cursor = connection.cursor(dictionary=True)
            query = "SELECT title, ingredients, steps, cook_time, serving_size, image FROM recipes WHERE id = %s"
            cursor.execute(query, (self.recipe_id,))
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
                    temp_image_path = f'temp_recipe_image_for_pdf_{self.recipe_id}.png'
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

    def add_back_button(self):
        back_btn = Button(text="Back", size_hint_y=None, height=40)
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)

    def go_back(self, instance):
        if self.manager:
            self.manager.current = 'main_page'


if __name__ == "__main__":
    class MainApp(App):
        user_id = 1
        username = "test_user"

        def build(self):
            sm = ScreenManager()
            view_recipe = ViewRecipe(name='view_recipe')
            sm.add_widget(view_recipe)
            view_recipe.set_recipe_id(1)
            return sm


    MainApp().run()