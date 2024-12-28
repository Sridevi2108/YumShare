from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from login import LoginScreen
from signup import SignupScreen
from mainscreen import MainPage
from upload_recipe import UploadRecipe
from viewrecipes import ViewRecipe
from profile import ProfileScreen
from favourites import Favourites
from your_recipes import YourRecipesScreen

class MyApp(App):
    user_id = None
    username = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(MainPage(name='main_page', screen_manager=sm))
        sm.add_widget(UploadRecipe(name='upload_recipe'))
        sm.add_widget(ViewRecipe(name='view_recipe'))
        sm.add_widget(Favourites(name='favourites'))
        sm.add_widget(ProfileScreen(name='profile_screen', user_id=self.user_id))
        sm.add_widget(YourRecipesScreen(name='your_recipes'))

        sm.current = 'login'

        return sm

if __name__ == "__main__":
    MyApp().run()