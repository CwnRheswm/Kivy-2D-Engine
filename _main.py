import math, cProfile

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.uix.widget import Widget
from kivy.vector import Vector

from _welcome import SplashScreen
#from _boards import BlackBoard, WhiteBoard, line_intersect, point_on_lines
#from impactpoints import find_impact_points
'''
--------
Class "main"(App)
    def build:
        loads the app, makes root Widget

        this actually needs to handle the switch between "books", i.e. SplashScreen(),
        BlackBoard(), WhiteBoard(), Etc()

class SplashScreen(Widget)
    front page of app

    child :: MainMenu(GridLayout)
        Buttons:
            Levels:
                open up the levels screen to select a level to load
            Village:
                open up your village to look at resources and construct buildings
            Settings:
                open up the settings pane
            Credits:
                read the credits
            DLC:
                open pane to browse currently available DLC
            Primal Breath (Games/Gamers/Studio/Factory/Atelier/Workshop/Alchemists):
                eventually a link to other products by PB* in the relivent app store

    level page
    child :: ScrollView
        child :: Grid Layout(levels)
            Buttons:
                1 - XX, change depending on device
    child :: Button(next page)
        move level selection page to next zone (1 - XX)

    child :: Button(previous page)
        move level selection page to previous zone (1 - XX)

    village page
    ????

    settings page
    child :: ScrollView
        child :: Float Layout(settings)
            various buttons/sliders/etc. for changing settings options, sound, and what-not

    credits page
    child :: ScrollView
        automatically scroll through the credits

    child :: Button(back)
        go back to main menu

    dlc page
    ????

    PB*
    push to app store with filter PB*

class BlackBoard(Scatter)
    basic backdrop for every level

    child :: Background(Image)
        dessert case background for the level

    child :: Actors(Scatter)
        child :: Sprite(Image)
        child :: Expression(Image)
        a scatter and Image for every collisionable object in the level
            includes: flan, fruit, floors, objects, etc.

def load_level()
    parses level files and passes them to BlackBoard

class WhiteBoard(Widget) [Stencil]
    basic level editor backdrop, holds background Images, actors, etc., but also has
    functions for editing

    child :: Background(Image)
        dessert case background for the level

    child :: Actors(Scatter)
        child :: Sprite(Image)
        child :: Expression(Image)
        a scatter and Image for every collisionable object in the level
            includes: flan, fruit, floors, objects, etc.

    child :: Drawer(ScrollView)
        child :: Tray(GridLayout)
            children :: Buttons()

    functions for displaying sliders and such for editing

class Flan(Actor)
class Fruit(Actor)
class Floor(Actor)
class ...(Actor)
'''
#Does each Actor need a new class, or can they all be one Actor class with various
#functions and variables? Either different Actor method instantiations or Flan/Fruit/Etc.
#are instantiations of the Actor method
'''
class Drawer(ScrollView)
    drawer that can slide in and out of view
    should be able to handle being docked on any side of the screen and hold anything it is given
    i.e. handle what is in the drawer and what it does by passing that to a Drawer instantiation
    Drawer handles holding a Tray (GridLayout), sliding in and out of view, and passing bindings
    from the Tray upwards
    
    child :: Tray(GridLayout)
        children :: various buttons

class

: SplashScreen
: : MainMenu(GridLayout)
: : : Back(Button)
: : : Levels/Village/Settings/Credits/DLC/PB*(Buttons)
: : LevelPage(GridLayout)
: : : Back(Button)
: : : Level X - XX(Buttons)
: : : NextPage(Button)
: : : PreviousPage(Button)
: : VillagePage(??)
: : SettingsPage(ScrollView)
: : : Back(Button)
: : : Settings(FloatLayout)
: : : : Options(Buttons/RadialButtons/Sliders/Etc.)
: : CreditsPage(ScrollView)
: : : Credits(Labels)
: : : Back(Button)
: : DLCPage (??)
: : PB* (??)
: BlackBoard(Scatter)
: : Background(Image)
: : Flans(Actor)
: : Fruit(Actor)
: : Floor(Actor)
--- Actor(Scatter)

--------
'''
            
class FlanQuest(App):
    def build(self):
        root = Widget()
        win = Window
        #win.fullscreen = True
        root.add_widget(SplashScreen())
        
        return root
    def on_start(self):
        self.profile = cProfile.Profile()
        self.profile.enable()
    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('myapp.txt')

    '''Needs functions to listen to SplashScreen() and what it returns and to switch
    to BlackBoard() or WhiteBoard()
    '''

if __name__ == "__main__":
    FlanQuest().run()
    
