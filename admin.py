import pandas as pd
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
import mysql.connector
from fpdf import FPDF
from login import LoginScreen  # Ensure login.py has LoginScreen class


class AdminScreen(Screen):
    def __init__(self, screen_manager=None, **kwargs):
        super(AdminScreen, self).__init__(**kwargs)
        self.screen_manager = screen_manager  # Ensure screen_manager is passed and set
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        self.header = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)
        self.logo = Image(source='logo.png', size_hint=(None, 1), width=50)
        self.title = Label(text='Admin Dashboard', font_size='24sp', color=(0, 0, 0, 1))
        self.header.add_widget(self.logo)
        self.header.add_widget(self.title)
        self.layout.add_widget(self.header)

        # Navigation Bar
        self.nav_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=10, spacing=10)

        # Visualization Dropdown
        self.visualization_spinner = Spinner(
            text='Visualizations',
            values=('Bar Graph', 'Pie Chart', 'Histogram', 'Line Graph'),
            size_hint=(None, None),
            size=(150, 44)
        )
        self.visualization_spinner.bind(text=self.on_visualization_select)
        self.nav_bar.add_widget(self.visualization_spinner)

        # Export to HTML Button
        self.export_html_button = Button(text='Export to HTML', size_hint=(None, None), size=(150, 44))
        self.export_html_button.bind(on_press=self.export_to_html)
        self.nav_bar.add_widget(self.export_html_button)

        # Export to CSV Button
        self.export_csv_button = Button(text='Export to CSV', size_hint=(None, None), size=(150, 44))
        self.export_csv_button.bind(on_press=self.export_to_csv)
        self.nav_bar.add_widget(self.export_csv_button)

        # Export to PDF Button
        self.export_pdf_button = Button(text='Export to PDF', size_hint=(None, None), size=(150, 44))
        self.export_pdf_button.bind(on_press=self.export_to_pdf)
        self.nav_bar.add_widget(self.export_pdf_button)

        # Logout Button
        self.logout_button = Button(text='Logout', size_hint=(None, None), size=(100, 44))
        self.logout_button.bind(on_press=self.logout)
        self.nav_bar.add_widget(self.logout_button)

        self.layout.add_widget(self.nav_bar)

        # Main content area with ScrollView
        self.main_content = ScrollView(size_hint=(1, 0.8))
        self.content_layout = GridLayout(cols=5, padding=10, spacing=10, size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.main_content.add_widget(self.content_layout)
        self.layout.add_widget(self.main_content)

        self.add_widget(self.layout)

        # Fetch and display database data
        self.fetch_and_display_users()

    def fetch_users_from_db(self):
        print("Connecting to the database...")
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database="yumshare"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, email FROM users")
            users = cursor.fetchall()
            print(f"Fetched users: {users}")  # Log the retrieved data
            return users
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            if connection.is_connected():
                connection.close()
                print("Closing the database connection.")

    def fetch_recipes_uploaded_count(self, user_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database="yumshare"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE user_id = %s", (user_id,))
            count = cursor.fetchone()[0]
            return count
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return 0
        finally:
            if connection.is_connected():
                connection.close()

    def fetch_favourites_count(self, user_id):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database="yumshare"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM likes WHERE user_id = %s", (user_id,))
            count = cursor.fetchone()[0]
            return count
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return 0
        finally:
            if connection.is_connected():
                connection.close()

    def fetch_and_display_users(self):
        print("Fetching users from the database...")
        users = self.fetch_users_from_db()  # Call the database function
        if not users:
            print("No users found or an error occurred.")
            return

        # Clear the content layout
        self.content_layout.clear_widgets()

        # Add headers
        headers = ['User ID', 'Username', 'Email', 'No of Recipes Uploaded', 'No of Favourites']
        for header in headers:
            self.content_layout.add_widget(Label(text=header, size_hint_y=None, height=40, color=(0, 0, 0, 1)))
        print("Headers added")

        # Add database data
        self.users_data = []
        for user in users:
            user_id, username, email = user
            print(f"Processing user: {user_id}, {username}, {email}")
            recipes_uploaded_count = self.fetch_recipes_uploaded_count(user_id)
            favourites_count = self.fetch_favourites_count(user_id)
            print(f"Adding row: {user_id}, {username}, {email}, {recipes_uploaded_count}, {favourites_count}")
            self.content_layout.add_widget(Label(text=str(user_id), size_hint_y=None, height=40, color=(0, 0, 0, 1)))
            self.content_layout.add_widget(Label(text=username, size_hint_y=None, height=40, color=(0, 0, 0, 1)))
            self.content_layout.add_widget(Label(text=email, size_hint_y=None, height=40, color=(0, 0, 0, 1)))
            self.content_layout.add_widget(
                Label(text=str(recipes_uploaded_count), size_hint_y=None, height=40, color=(0, 0, 0, 1)))
            self.content_layout.add_widget(
                Label(text=str(favourites_count), size_hint_y=None, height=40, color=(0, 0, 0, 1)))
            self.users_data.append({
                "user_id": user_id,
                "username": username,
                "email": email,
                "recipes_uploaded_count": recipes_uploaded_count,
                "favourites_count": favourites_count
            })

        # Adjust content layout height and refresh
        self.content_layout.height = self.content_layout.minimum_height
        self.content_layout.canvas.ask_update()

    def on_visualization_select(self, spinner, text):
        print(f"Selected visualization: {text}")
        data = self.users_data
        user_ids = [user["user_id"] for user in data]
        uploads = [user["recipes_uploaded_count"] for user in data]
        favourites = [user["favourites_count"] for user in data]

        if text == "Bar Graph":
            self.display_bar_graph(user_ids, uploads, favourites)
        elif text == "Pie Chart":
            self.display_pie_chart(user_ids, uploads)
        elif text == "Histogram":
            self.display_histogram(user_ids, uploads, favourites)
        elif text == "Line Graph":
            self.display_line_graph(user_ids, uploads, favourites)

    def display_bar_graph(self, user_ids, uploads, favourites):
        plt.figure(figsize=(10, 6))
        plt.bar(user_ids, uploads, label="Uploads")
        plt.bar(user_ids, favourites, label="Favourites", bottom=uploads)
        plt.xlabel('User ID')
        plt.ylabel('Count')
        plt.title('Uploads and Favourites by User ID')
        plt.legend()
        plt.show()

    def display_pie_chart(self, user_ids, uploads):
        plt.figure(figsize=(10, 6))
        plt.pie(uploads, labels=user_ids, autopct='%1.1f%%', startangle=140)
        plt.title('Uploads by User ID')
        plt.show()

    def display_histogram(self, user_ids, uploads, favourites):
        plt.figure(figsize=(10, 6))
        plt.hist([uploads, favourites], label=["Uploads", "Favourites"], bins=len(user_ids), alpha=0.7)
        plt.xlabel('Count')
        plt.ylabel('Frequency')
        plt.title('Histogram of Uploads and Favourites')
        plt.legend()
        plt.show()

    def display_line_graph(self, user_ids, uploads, favourites):
        plt.figure(figsize=(10, 6))
        plt.plot(user_ids, uploads, marker='o', label="Uploads")
        plt.plot(user_ids, favourites, marker='o', label="Favourites")
        plt.xlabel('User ID')
        plt.ylabel('Count')
        plt.title('Line Graph of Uploads and Favourites by User ID')
        plt.legend()
        plt.show()

    def export_to_html(self, instance):
        print("Exporting data to HTML...")
        df = pd.DataFrame(self.users_data)
        df.to_html('users_data.html', index=False)
        print("Data exported to users_data.html")

    def export_to_csv(self, instance):
        print("Exporting data to CSV...")
        df = pd.DataFrame(self.users_data)
        df.to_csv('users_data.csv', index=False)
        print("Data exported to users_data.csv")

    def export_to_pdf(self, instance):
        print("Exporting data to PDF...")
        df = pd.DataFrame(self.users_data)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add a cell
        pdf.cell(200, 10, txt="User Data", ln=True, align='C')

        # Add table headers
        col_width = pdf.w / 5.5
        pdf.ln(10)
        for col in df.columns:
            pdf.cell(col_width, 10, col, border=1)
        pdf.ln(10)

        # Add table data
        for index, row in df.iterrows():
            for col in df.columns:
                pdf.cell(col_width, 10, str(row[col]), border=1)
            pdf.ln(10)

        pdf.output("users_data.pdf")
        print("Data exported to users_data.pdf")

    def logout(self, instance):
        print("Logging out...")
        # Redirect to the landing screen
        self.screen_manager.current = 'landing'
        # Clear the user data
        app = App.get_running_app()
        app.user_id = None
        app.username = None


class MainApp(App):
    user_id = None  # Initialize user_id in the app instance
    username = None  # Initialize username in the app instance

    def build(self):
        # Set the background color and window size
        Window.clearcolor = (1, 1, 1, 1)  # White background
        Window.size = (800, 600)  # Set the window size

        sm = ScreenManager()
        admin_screen = AdminScreen(screen_manager=sm, name='adminscreen')
        login_screen = LoginScreen(name='landing')
        sm.add_widget(admin_screen)
        sm.add_widget(login_screen)
        sm.current = 'landing'  # Correct initial screen name
        return sm


if __name__ == "__main__":
    MainApp().run()