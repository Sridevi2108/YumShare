from tkinter import ttk


# Function to handle search
def search_action(search_entry):
    search_query = search_entry.get()
    print(f"Searching for: {search_query}")
    # Update search results dynamically here


# Function to update popular searches dynamically
def update_popular_searches(popular_search_frame, popular_search_label):
    new_popular_searches = ["methi", "bhindi", "paneer", "dal"]

    for widget in popular_search_frame.winfo_children():
        widget.destroy()  # Clear existing popular searches

    popular_search_label.pack()

    for search in new_popular_searches:
        search_label = ttk.Label(popular_search_frame, text=search, style='TLabel')
        search_label.pack(side='left', padx=10)
