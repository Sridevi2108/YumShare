import tkinter as tk
from tkinter import ttk
from recipe_window import open_recipe_window
from view_recipe import open_view_recipes_window

# Initialize main window
root = tk.Tk()
root.title("YumShare")

# Apply custom styles
style = ttk.Style()
style.configure('TFrame', background='#f0f0f0')
style.configure('TButton', background='#4CAF50', foreground='black', font=('Arial', 14, 'bold'))
style.configure('TLabel', background='#f0f0f0', font=('Arial', 14))
style.configure('TEntry', font=('Arial', 14))

# Header Section
header_frame = ttk.Frame(root, style='TFrame')
header_frame.pack(fill='x')

logo_label = ttk.Label(header_frame, text="YumShare", font=('Arial', 28, 'bold'))
logo_label.pack(side='left', padx=10, pady=10)

search_entry = ttk.Entry(header_frame, width=50, font=('Arial', 14))
search_entry.pack(side='left', padx=10)

search_button = ttk.Button(header_frame, text="Search", style='TButton')
search_button.pack(side='left', padx=10)

get_app_button = ttk.Button(header_frame, text="Get App", style='TButton')
get_app_button.pack(side='right', padx=10)

new_recipe_button = ttk.Button(header_frame, text="Create New Recipe", style='TButton', command=open_recipe_window)
new_recipe_button.pack(side='right', padx=10)

# Add View Recipes Button
view_recipes_button = ttk.Button(header_frame, text="View Recipes", style='TButton', command=open_view_recipes_window)
view_recipes_button.pack(side='right', padx=10)

# Language Selection
language_frame = ttk.Frame(root, style='TFrame')
language_frame.pack(fill='x', padx=10, pady=10)

languages = ["English", "Hindi", "Bengali", "Gujarati", "Tamil", "Marathi"]
for lang in languages:
    lang_button = ttk.Button(language_frame, text=lang, style='TButton')
    lang_button.pack(side='left', padx=5, pady=5)

# Main Banner
banner_frame = ttk.Frame(root, style='TFrame')
banner_frame.pack(fill='x', padx=10, pady=10)

banner_label = ttk.Label(banner_frame, text="Winter Series: 11 November - 29 December", font=('Arial', 16, 'bold'))
banner_label.pack()

# Side Navigation Bar
side_nav_frame = ttk.Frame(root, style='TFrame')
side_nav_frame.pack(side='left', fill='y', padx=10, pady=10)

nav_options = ["Search", "Premium", "Recipe Stats", "Activity", "Your Collection"]
for option in nav_options:
    nav_button = ttk.Button(side_nav_frame, text=option, style='TButton')
    nav_button.pack(fill='x', pady=5)

# Your Collection Sub-options
collection_frame = ttk.Frame(side_nav_frame, style='TFrame')
collection_frame.pack(fill='x', pady=10)

collection_options = ["All", "Saved", "Cooked", "Your recipes", "Published"]
for option in collection_options:
    collection_button = ttk.Button(collection_frame, text=f"{option} (0)", style='TButton')
    collection_button.pack(fill='x', pady=2)

# Popular Searches Section
popular_search_frame = ttk.Frame(root, style='TFrame')
popular_search_frame.pack(fill='x', padx=10, pady=10)

popular_search_label = ttk.Label(popular_search_frame, text="Today's popular searches", font=('Arial', 16, 'bold'))
popular_search_label.pack()

popular_searches = ["kabuli chana", "amla", "jackfruit flour", "bathua"]
for search in popular_searches:
    search_label = ttk.Label(popular_search_frame, text=search, style='TLabel')
    search_label.pack(side='left', padx=10)

# Function to handle search
def search_action():
    search_query = search_entry.get()
    print(f"Searching for: {search_query}")
    # Update search results dynamically here

search_button.config(command=search_action)

# Function to update popular searches dynamically
def update_popular_searches():
    new_popular_searches = ["methi", "bhindi", "paneer", "dal"]

    # Clear existing search labels but keep the popular_search_label
    for widget in popular_search_frame.winfo_children():
        if widget != popular_search_label:
            widget.destroy()  # Clear existing popular searches

    # Repack the popular_search_label in case it's misplaced
    popular_search_label.pack(pady=5)

    for search in new_popular_searches:
        search_label = ttk.Label(popular_search_frame, text=search, style='TLabel')
        search_label.pack(side='left', padx=10)

# Call this function when you need to update the popular searches
update_popular_searches()

# Run the application
root.mainloop()
