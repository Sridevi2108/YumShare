import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import mysql.connector

# Database connection
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="password",  # Replace with your MySQL password
        database="yumshare"
    )

# Function to upload the recipe to the database
def upload_recipe_to_db(user_id, title, ingredients, steps, image_data=None):
    db = connect_to_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO recipes (user_id, title, ingredients, steps, image)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, title, ingredients, steps, image_data))
        db.commit()
        messagebox.showinfo("Success", "Recipe uploaded successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error uploading recipe: {err}")
    finally:
        db.close()

# Function to handle image upload
def upload_image(label):
    image_path = filedialog.askopenfilename(title="Select Recipe Image",
                                            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
    if image_path:
        image = Image.open(image_path)
        image = image.resize((200, 200))  # Resize image to a standard thumbnail size
        image = ImageTk.PhotoImage(image)
        label.config(image=image)
        label.image = image
        with open(image_path, 'rb') as file:
            return file.read()  # Return image data
    return None

# Function to add a new ingredient
def add_ingredient(entry, listbox):
    ingredient = entry.get()
    if ingredient:
        listbox.insert(tk.END, ingredient)
        entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter an ingredient.")

# Function to delete selected ingredient
def delete_ingredient(listbox):
    selected = listbox.curselection()
    if selected:
        listbox.delete(selected)
    else:
        messagebox.showerror("Error", "Please select an ingredient to delete.")

# Function to add a new step
def add_step(entry, listbox):
    step = entry.get()
    if step:
        listbox.insert(tk.END, step)
        entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter a step.")

# Function to delete selected step
def delete_step(listbox):
    selected = listbox.curselection()
    if selected:
        listbox.delete(selected)
    else:
        messagebox.showerror("Error", "Please select a step to delete.")

# Upload Recipe Window
def upload_recipe(user_id):
    upload_window = tk.Toplevel()
    upload_window.title("Upload Recipe")

    tk.Label(upload_window, text="Recipe Title").grid(row=0, column=0, padx=10, pady=5)
    title_entry = tk.Entry(upload_window, width=40)
    title_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(upload_window, text="Ingredients").grid(row=1, column=0, padx=10, pady=5)
    ingredient_entry = tk.Entry(upload_window, width=40)
    ingredient_entry.grid(row=1, column=1, padx=10, pady=5)

    ingredient_listbox = tk.Listbox(upload_window, width=40, height=6)
    ingredient_listbox.grid(row=2, column=1, padx=10, pady=5)

    add_ingredient_button = tk.Button(upload_window, text="Add Ingredient", command=lambda: add_ingredient(ingredient_entry, ingredient_listbox))
    add_ingredient_button.grid(row=3, column=0, padx=10, pady=5)

    delete_ingredient_button = tk.Button(upload_window, text="Delete Ingredient", command=lambda: delete_ingredient(ingredient_listbox))
    delete_ingredient_button.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(upload_window, text="Steps").grid(row=4, column=0, padx=10, pady=5)
    step_entry = tk.Entry(upload_window, width=40)
    step_entry.grid(row=4, column=1, padx=10, pady=5)

    step_listbox = tk.Listbox(upload_window, width=40, height=6)
    step_listbox.grid(row=5, column=1, padx=10, pady=5)

    add_step_button = tk.Button(upload_window, text="Add Step", command=lambda: add_step(step_entry, step_listbox))
    add_step_button.grid(row=6, column=0, padx=10, pady=5)

    delete_step_button = tk.Button(upload_window, text="Delete Step", command=lambda: delete_step(step_listbox))
    delete_step_button.grid(row=6, column=1, padx=10, pady=5)

    image_label = tk.Label(upload_window, text="No Image Selected")
    image_label.grid(row=7, columnspan=2, pady=10)

    image_data = None
    image_button = tk.Button(upload_window, text="Upload Image", command=lambda: upload_image(image_label))
    image_button.grid(row=8, columnspan=2, pady=10)

    def save_recipe():
        title = title_entry.get()
        ingredients = "\n".join(ingredient_listbox.get(0, tk.END))  # Convert listbox items to string
        steps = "\n".join(step_listbox.get(0, tk.END))  # Convert listbox items to string

        if title and ingredients and steps:
            # Call function to upload to database
            upload_recipe_to_db(user_id, title, ingredients, steps, image_data)
            upload_window.destroy()
        else:
            messagebox.showerror("Error", "All fields are required.")

    save_button = tk.Button(upload_window, text="Save Recipe", command=save_recipe)
    save_button.grid(row=9, columnspan=2, pady=10)

    upload_window.mainloop()
