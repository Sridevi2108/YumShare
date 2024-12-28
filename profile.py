from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Line, Color
from kivy.uix.button import Button
from kivy.core.window import Window
from datetime import datetime

import mysql.connector  # Make sure to install mysql-connector-python

class ProfileScreen(Screen):
    def __init__(self, user_id=None, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.user_id = user_id
        self.layout.add_widget(Label(text=f"User ID: {self.user_id}"))
        self.graph_section = BoxLayout(size_hint=(1, 1), orientation='vertical')
        self.layout.add_widget(self.graph_section)
        back_button = Button(text="Back", size_hint=(None, None), size=(100, 50))
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)
        self.add_widget(self.layout)

    def set_user_id(self, user_id):
        self.user_id = user_id
        print(f"User ID set to: {self.user_id}")

    def on_pre_enter(self):
        # Fetch user data based on user_id and display content (e.g., graph)
        self.fetch_recipe_data_and_plot()

    def go_back(self, instance):
        self.manager.current = 'main_page'

    def fetch_recipe_data_and_plot(self):
        # Fetch the number of recipe uploads per day for the current user
        user_id = self.user_id
        data = self.get_recipe_data_for_user(user_id)

        if not data:
            self.graph_section.add_widget(Label(text="No recipe data available"))
            return

        # Extract dates and counts
        dates = [row[0] for row in data]  # row[0] is already a datetime.date object
        counts = [row[1] for row in data]

        # Draw the graph
        self.draw_recipe_upload_graph(dates, counts)

    def get_recipe_data_for_user(self, user_id):
        # Connect to the MySQL database and fetch data for the user
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='yumshare'
        )

        cursor = connection.cursor()
        query = """
        SELECT DATE(created_at) AS upload_date, COUNT(*) AS recipe_count
        FROM recipes
        WHERE user_id = %s
        GROUP BY DATE(created_at)
        ORDER BY upload_date;
        """
        cursor.execute(query, (user_id,))
        data = cursor.fetchall()

        cursor.close()
        connection.close()

        return data

    def draw_recipe_upload_graph(self, dates, counts):
        # Prepare the Kivy canvas to draw the graph
        self.graph_section.clear_widgets()

        # Define the graph canvas
        graph_widget = BoxLayout(size_hint=(1, 1))
        graph_widget.canvas.clear()

        with graph_widget.canvas:
            # Set up the axes (simple grid)
            Color(0, 0, 0, 1)  # Black for axes
            Line(points=[50, 50, 50, 400], width=2)  # Y-axis
            Line(points=[50, 50, 400, 50], width=2)  # X-axis

            # Draw the data points and lines connecting them
            max_y = max(counts)  # Max recipe count
            min_x = min(dates)  # Min date
            max_x = max(dates)  # Max date

            # Scale factors to fit the graph within the box
            scale_x = 350 / (max_x - min_x).days  # Scale for x-axis (dates)
            scale_y = 300 / max_y  # Scale for y-axis (recipe count)

            # Plot the data points and connect them with lines
            prev_x, prev_y = None, None
            for i, date in enumerate(dates):
                # Convert date to x-axis position
                x = 50 + (date - min_x).days * scale_x
                # Convert recipe count to y-axis position
                y = 50 + counts[i] * scale_y

                if prev_x is not None:
                    # Draw a line between the previous point and the current point
                    Color(0, 0, 1, 1)  # Blue color for the line
                    Line(points=[prev_x, prev_y, x, y], width=2)

                # Draw a point at the current position
                Color(1, 0, 0, 1)  # Red color for the point
                Line(circle=(x, y, 5), width=2)

                prev_x, prev_y = x, y

        # Add the graph widget to the layout
        self.graph_section.add_widget(graph_widget)
