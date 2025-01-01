from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from LikesGraphScreen import LikesGraphScreen
from ProfileCreationScreen import ProfileCreationScreen
from admin import AdminScreen
from admin_login import AdminLoginScreen
from login import LoginScreen
from signup import SignupScreen
from mainscreen import MainPage
from upload_recipe import UploadRecipe
from viewrecipes import ViewRecipe
from profile import ProfileScreen
from favourites import Favourites
from your_recipes import YourRecipesScreen
from landing import LandingScreen


class MyApp(App):
    user_id = None
    username = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LandingScreen(name='landing'))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(MainPage(name='main_page', screen_manager=sm))
        sm.add_widget(UploadRecipe(name='upload_recipe'))
        sm.add_widget(ViewRecipe(name='view_recipe'))
        sm.add_widget(Favourites(name='favourites'))
        sm.add_widget(YourRecipesScreen(name='your_recipes'))
        sm.add_widget(ProfileCreationScreen(name="profile_creation"))
        profile_screen = ProfileScreen(name='profile_screen')
        sm.add_widget(AdminScreen(name='admin'))
        sm.add_widget(AdminLoginScreen(name='adminlogin'))
        profile_screen.user_id = self.user_id  # Set user_id separately
        sm.add_widget(profile_screen)

        sm.current = 'landing'

        return sm

    def set_user_details(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.profile_screen.set_user_id(user_id)

if __name__ == "__main__":
    MyApp().run()