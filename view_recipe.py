import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
from io import BytesIO

# Database connection
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="yumshare"
        )
        print("Database connection successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        messagebox.showerror("Error", f"Database connection error: {err}")
        return None

# Function to fetch recipes from the database
def fetch_recipes():
    db = connect_to_db()
    if db is None:
        return []

    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, title, ingredients, steps, image FROM recipes")
        recipes = cursor.fetchall()
        print("Recipes fetched successfully!")
        return recipes
    except mysql.connector.Error as err:
        print(f"Error fetching recipes: {err}")
        return []
    finally:
        cursor.close()
        db.close()

# Function to open detailed view of a recipe
def open_recipe_detail(recipe):
    _, title, ingredients, steps, image_data = recipe

    detail_window = tk.Toplevel()
    detail_window.title(f"Recipe: {title}")

    title_label = tk.Label(detail_window, text=f"Title: {title}", font=('Arial', 18, 'bold'))
    title_label.pack(pady=10)

    ingredients_label = tk.Label(detail_window, text=f"Ingredients:\n{ingredients}", font=('Arial', 14))
    ingredients_label.pack(pady=10)

    steps_label = tk.Label(detail_window, text=f"Instructions:\n{steps}", font=('Arial', 14))
    steps_label.pack(pady=10)

    if image_data:
        image = Image.open(BytesIO(image_data))
        image = image.resize((400, 400))
        image = ImageTk.PhotoImage(image)
        image_label = tk.Label(detail_window, image=image)
        image_label.image = image
        image_label.pack(pady=10)

    close_button = tk.Button(detail_window, text="Close", command=detail_window.destroy)
    close_button.pack(pady=10)

# Function to open the view recipes window
def open_view_recipes_window():
    recipes = fetch_recipes()
    print("Number of recipes fetched:", len(recipes))  # Debugging: Print number of recipes

    view_window = tk.Toplevel()
    view_window.title("View Recipes")

    if not recipes:
        tk.Label(view_window, text="No recipes found.").pack(pady=10)
        return

    for i, recipe in enumerate(recipes):
        _, title, ingredients, steps, image_data = recipe

        frame = tk.Frame(view_window)
        frame.grid(row=i // 3, column=i % 3, padx=10, pady=10)

        if image_data:
            image = Image.open(BytesIO(image_data))
            image = image.resize((200, 200))
            image = ImageTk.PhotoImage(image)
            image_label = tk.Label(frame, image=image)
            image_label.image = image
            image_label.pack()
            image_label.bind("<Button-1>", lambda e, r=recipe: open_recipe_detail(r))

        title_label = tk.Label(frame, text=title, font=('Arial', 12, 'bold'))
        title_label.pack(pady=5)

    close_button = tk.Button(view_window, text="Close", command=view_window.destroy)
    close_button.grid(row=(len(recipes) // 3) + 1, columnspan=3, pady=10)

# Main script to run the view window if this file is executed directly
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Recipe Viewer")
    open_view_recipes_window()
    root.mainloop()
