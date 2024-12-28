from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
from kivy.core.window import Window
from login import LoginScreen
from signup import SignupScreen
from mainscreen import MainPage
from upload_recipe import UploadRecipe
from viewrecipes import ViewRecipe
from profile import ProfileScreen  # Importing the ProfileScreen

# Set the window background color to white
Window.clearcolor = (1, 1, 1, 1)

# Set the video provider
Config.set('kivy', 'video', 'ffpyplayer')

class MainApp(App):
    user_id = None
    user_name=None # Store user_id here

    def build(self):
        # Create the screen manager
        sm = ScreenManager()

        # Add screens to the screen manager
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(MainPage(name='main_page', screen_manager=sm))  # Pass the screen manager to MainPage
        sm.add_widget(UploadRecipe(name='upload_recipe'))
        sm.add_widget(ViewRecipe(name='view_recipe'))

        # Add the ProfileScreen
        sm.add_widget(ProfileScreen(name='profile_screen', user_id=self.user_id))

        # Set user_id in ProfileScreen after it is added to the screen manager
        # Set the default screen
        sm.current = 'login'  # Default to login screen (or whichever screen you want to show first)

        return sm

if __name__ == "__main__":
    MainApp().run()
