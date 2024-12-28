from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import mainthread
import mysql.connector
from io import BytesIO
from kivy.core.image import Image as CoreImage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class ViewRecipe(Screen):
    def __init__(self, **kwargs):
        super(ViewRecipe, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Labels to display recipe details
        self.title_label = Label(text='Title', font_size='24sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.title_label)

        self.recipe_image = Image(size_hint=(1, None), height=300, source='default_image.png')  # Default image
        self.layout.add_widget(self.recipe_image)

        self.ingredients_label = Label(text='Ingredients', font_size='16sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.ingredients_label)

        self.steps_label = Label(text='Steps', font_size='16sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.steps_label)

        self.serving_label = Label(text='Serving Size', font_size='16sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.serving_label)

        self.cook_time_label = Label(text='Cook Time', font_size='16sp', size_hint_y=None, height=40)
        self.layout.add_widget(self.cook_time_label)

        # Button to generate PDF
        self.generate_pdf_button = Button(text="Generate PDF", size_hint=(None, None), size=(200, 50))
        self.generate_pdf_button.bind(on_press=self.generate_pdf)
        self.layout.add_widget(self.generate_pdf_button)

        self.add_widget(self.layout)

    def display_recipe(self, recipe_id):
        """Display the recipe details and fetch them from the database."""
        db = self.connect_to_database()
        if db is None:
            print("Failed to connect to the database.")
            return

        cursor = db.cursor()
        try:
            cursor.execute(
                f"SELECT title, ingredients, steps, serving_size, cook_time, image FROM recipes WHERE id = {recipe_id}")
            recipe = cursor.fetchone()

            if recipe:
                title, ingredients, steps, serving_size, cook_time, image_data = recipe
                self.update_labels(title, ingredients, steps, serving_size, cook_time)

                if image_data:
                    image_stream = BytesIO(image_data)
                    try:
                        core_image = CoreImage(image_stream, ext="png")
                        self.recipe_image.texture = core_image.texture
                    except Exception as e:
                        print(f"Error loading image: {e}")
                        self.recipe_image.source = 'default_image.png'
                else:
                    self.recipe_image.source = 'default_image.png'

            else:
                print("Recipe not found.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            db.close()

    def update_labels(self, title, ingredients, steps, serving_size, cook_time):
        """Update the labels with the recipe details."""
        self.title_label.text = title if title else "Not available"
        self.ingredients_label.text = f"Ingredients: {ingredients}" if ingredients else "Not available"
        self.steps_label.text = f"Steps: {steps}" if steps else "Not available"
        self.serving_label.text = f"Serving Size: {serving_size}" if serving_size else "Not available"
        self.cook_time_label.text = f"Cook Time: {cook_time} minutes" if cook_time else "Not available"

    def connect_to_database(self):
        """Connect to the MySQL database."""
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

    def generate_pdf(self, instance):
        """Generate the PDF file with the recipe details."""
        title = self.title_label.text
        ingredients = self.ingredients_label.text
        steps = self.steps_label.text
        serving_size = self.serving_label.text
        cook_time = self.cook_time_label.text

        # Check if any of the fields are "Not available"
        if "Not available" in [title, ingredients, steps, serving_size, cook_time]:
            print("Some recipe details are missing, cannot generate PDF.")
            return

        # Set the PDF file path (you can adjust the path and filename as needed)
        pdf_filename = os.path.join(os.getcwd(), f"{title}_recipe.pdf")

        # Create a canvas for the PDF
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, f"Recipe: {title}")

        # Image (if any)
        image_path = "default_image.png"  # Default image if no image is available
        if self.recipe_image.texture:
            # Save the texture as a temporary image file (to be able to load it for PDF)
            self.recipe_image.texture.save("temp_image.png")
            image_path = "temp_image.png"

            # Optionally, rotate the image before drawing
            # Set parameters for the image (width, height, x, y)
            image_width = 200
            image_height = 200
            x_position = 50
            y_position = height - 300

            # Draw the image (flip vertically by adjusting Y position)
            c.drawImage(image_path, x_position, y_position, width=image_width, height=image_height)

            # Remove the temporary image after drawing
            if os.path.exists("temp_image.png"):
                os.remove("temp_image.png")

        # Ingredients
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 350, "Ingredients:")
        c.drawString(50, height - 370, ingredients)

        # Steps
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 400, "Steps:")
        c.drawString(50, height - 420, steps)

        # Serving Size
        c.drawString(50, height - 450, f"Serving Size: {serving_size}")

        # Cook Time
        c.drawString(50, height - 470, f"Cook Time: {cook_time}")

        # Save the PDF
        c.save()
        print(f"PDF generated successfully: {pdf_filename}")

