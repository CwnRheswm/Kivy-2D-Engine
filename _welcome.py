from functools import partial

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.vector import Vector

from _boards import BlackBoard#, WhiteBoard
#from workingboard import BlackBoard

'''
_welcome.py contains SlashScreen() which is available outside and is the main front screen
showing the logo and contains the main menu and all the sub menus and will launch a
particular level or the editor

SplashScreen() is called and added to root()
    it drops the logo(Image()) onto the background(Image())
    after the logo drops you click the screen and open the main menu
        logo is pushed to the top of the screen (over 1.4 seconds) and
        the main menu is opened (1.6 seconds)

    MainMenu(FloatLayout()) contains 5 Buttons: level, village, settings, dlc, credits
        portrait                        landscape
         _______                 ___________   __________
        |_______|               |___________| |__________|
         _______
        |_______|                ______   ______   ______
         _______                |______| |______| |______|
        |_______|               
         _______
        |_______|
         _______
        |_______|

    On MainMenu Button click: self.parent.level_menu()

    Also loads the VBW (Vital Breath Workshops) logo and link, probably in the bottom right
        Button() with on_release binding to open Google Play/App Store/Website for other VBW apps
        Back Button(), return to MainMenu()

    Each MainMenu Button loads another screen with the relevant information
        LevelPage(Widget()) : removes the MainMenu
            background(Image()) : background for each bakery area

            {
            Bakery(GridLayout())
                ame_0,ame_1,#...n(Button())
                    on_release: start the level
                        
            Patisserie(GridLayout())
                frn_0,fre_1,#...n(Button())
            Etc.
            }

            {
            Previous Button(Button()) : button to move to the previuos group of levels
            Next Button(Button()) : button to move the next group of levels (if opened)
            }

            VBW button
'''
def move_over_time(actor, pos, deltaDist, dT):
    dist, direction = get_direction(actor.pos, pos)
    
    #if (dist < deltaDist and dist > Vector(0,0)) or (dist > deltaDist and dist < Vector(0,0)):
    if Vector(abs(dist[0]), abs(dist[1])) < Vector(abs(deltaDist[0]), abs(deltaDist[1])):
        target = pos
        actor.moving = False
        return False
    else:
        #print(deltaDist[1], direction[1])
        x = actor.x + (abs(deltaDist[0]) * direction[0])
        y = actor.y + (abs(deltaDist[1]) * direction[1])
        target = (x,y)
        #print(actor.pos, target)
    actor.pos = target

def get_direction(position, target):
    dist = Vector(target) - Vector(position)
    direction = dist.normalize()
    return dist, direction

class LevelPage(GridLayout):
    '''
    Level menu for selecting what level you want to play.
    Levels become available as the previous level is completed with at least 1 star
    Each page in the level should have 10 - 30 levels, depending on how much that
    crowds the page.
    
    If Editor is set to TRUE, an EDITOR button is added outside of the main level menu

    Upon selecting a level, this should cause a RETURN to SplashScreen() that causes it to
    cede to BlackBoard(). Upon selecting the EDITOR(Button) this should cause a RETURN to
    SplashScreen() that causes it to cede to WhiteBoard()

    1 GridLayout:
        X(Buttons) for levels
    4 Buttons:
        Next
        Previous
        PBW
        Back
    '''
    def __init__(self):
        GridLayout.__init__(self)
        #background = Image()
        #background.pos = (0,0)
        
        self.size = (0.80 * Window.width, 0.70 * Window.height)
        self.pos = (0.1 * Window.width, 0.1 * Window.height)
        #print(self.size)
        self.spacing = 25
        #self.bind(minimum_size = self.setter('size'))
        col_default_width = 1
        self.cols = 6
        self.col_default_width = (self.width / 7)
        self.col_force_default = True
        self.rows = 5
        self.row_default_height = (self.height / 6)
        self.row_force_default = True

        self.location = 'ame'

        ame_0 = Button(text = '0')
        ame_1 = Button(text = '1')
        self.add_widget(ame_0)
        self.add_widget(ame_1)

    #def add_bind(self, button):
    #    button.bind(on_release = self.button_release)

    #def button_release(self, instance):
    #    print (instance.text)   

class SettingsPage(GridLayout):
    '''
    Settings menu for selecting various settings. Not sure what settings ATM.

    Allows you to set and change settings that are read/written to a small file,
    has a Back(Button) to return you to MainMenu() when done
    '''
    pass

class CreditsPage(ScrollView):
    '''
    Credits ScrollView that autoscrolls through Credits.

    Has a Back(Button) to reutrn you to MainMenu() when done.
    '''
    pass

class DLCPage(GridLayout):
    '''
    DLC Page with GridLayout that lists currently available DLC and which ones you
    have already bought and downloaded

    Has a Back(Button) to return you to MainMenu() when done.
    '''
    pass

class MainMenu(FloatLayout):
    '''
    Main menu for selecting what you want to do.
    Has Buttons for Levels, to access the Village, to go to Settings, to see the Credits,
    to look at available DLC and to puruse other products by PBW (Primal Breath Workshop; Vital Breath Games/Studio/Workshop)

    1 column grid layout,
    landscape (??)
    sits under the self.logo for the game
    #no settings, just buttons for major settings (volume, music on/off)
    X Buttons:
        Level
        Village
        Settings
        Credits
        DLC
    '''
    def __init__(self):
        FloatLayout.__init__(self)

        #self.cols = 1
        self.size_hint = None, None
        self.size = Window.width/2, ((Window.height / 4) * 2)
        self.pos_hint = None, None
        self.pos = (Window.width/2 - self.width/2), 10

        if Window.width > Window.height:
            w1 = 0.95
            w2 = 0.25
            h = 0.25
            spacing = 0.1
            padding = 0.025
        else:
            w1, w2 = 1, 1
            h = 0.18
            
        settings = Button(text = 'Settings', size_hint_y = h, size_hint_x = w2, pos_hint = {'x': padding, 'y': 0})
        credit = Button(text = 'Credits', size_hint_y = h, size_hint_x = w2, pos_hint = {'x': padding + spacing + w2, 'y': 0})
        dlc = Button(text = 'DLC', size_hint_y = h, size_hint_x = w2, pos_hint = {'x': padding + (spacing * 2) + (w2 * 2), 'y': 0})
        level = Button(text = 'Levels', size_hint_y = h, size_hint_x = w1, pos_hint = {'x': padding, 'y': 1 - h}) #add imagery
        village = Button(text = 'Village', size_hint = (w1,h), pos_hint = {'x': padding, 'y': 1 - (2 * h) - spacing})
        
        self.add_widget(level)
        self.add_widget(village)
        self.add_widget(settings)
        self.add_widget(credit)
        self.add_widget(dlc)

    #def add_bind(self, button):
    #    button.bind(on_release = self.button_release)

    #def button_release(self, instance):
    #    print (instance.text)

class SplashScreen(Widget):
    '''
    Main "Front Page" of the app.

    Splash Screen that shows a background image, the main self.logo of the game and holds
    the MainMenu(GridLayout)

    2 Images:
        Background
        self.logo
    1 GridLayout:
        MainMenu
    1 Button:
        Primal Breath Workshop (loads AppStore filtered to PBW)

    Upon selecting an option in the Main Menu, Main Menu will be replaced with one of the
    other pages

    This cedes to BlackBoard if you load a level, WhiteBoard if you are editing a level
    '''
    def __init__(self):
        Widget.__init__(self)

        self.menu = None

        #load background and self.logo
        background = Image(source = None, size = Window.size, color = (0,1,0,.2))
        self.logo = Image(source = None, size = (500,150), color = (1,0,1,1))
        self.logo.moving = True

        self.add_widget(background)
        self.add_widget(self.logo)

        #set background and move self.logo to center of screen
        background.pos = (0,0)
        self.logo.pos = ((Window.width /2) - (self.logo.width / 2), Window.height + 5)
        #move self.logo down to center over 2 seconds
        time = .3#5.0
        pos = (((Window.width /2) - (self.logo.width /2)), ((Window.height /2) - (self.logo.height /2)))
        deltaDist = (Vector(self.logo.pos) - Vector(pos)) / (60 * time)
        Clock.schedule_interval(partial(move_over_time, self.logo, pos, deltaDist), 1 / 60) #(actor, dest_pos, dT)
        
    def on_touch_up(self, touch):
        #wait for button click
        
        if self.logo.collide_point(*touch.pos) and self.logo.moving == False:
            time = .3#3.0
            pos = (((Window.width /2) - (self.logo.width /2)), (Window.height - (self.logo.height) - 10))
            deltaDist = (Vector(self.logo.pos) - Vector(pos)) / (60 * time)
            self.logo.moving = True
            Clock.schedule_interval(partial(move_over_time, self.logo, pos, deltaDist), 1 / 60)
            Clock.schedule_once(self.main_menu, (time+.2))

        '''if self.menu != None:
            for child in self.menu.children:
                if type(child) == Button:
                    if child.state == 'down':
                        if child.text == 'Levels':
                            self.level_menu()'''

        super(SplashScreen, self).on_touch_up(touch)

    def add_bind(self, button):
        button.bind(on_release = self.button_release)

    def button_release(self, instance):
        if type(self.menu) == LevelPage: #American Bakery
            if self.menu.location == 'ame':
                self.run_level('ame',0)
        if instance.text == 'Levels':
            self.level_menu()
        
    def main_menu(self, dt):
        if self.menu != None:
            self.remove_widget(self.menu)
        self.menu = MainMenu()
        self.add_widget(self.menu)
        for child in self.menu.children:
            self.add_bind(child)
        #self.menu.add_buttons()
        #self.add_widget(self.menu)
        

    def level_menu(self):
        self.remove_widget(self.menu)
        self.remove_widget(self.logo)
        self.menu = LevelPage()
        self.add_widget(self.menu)
        for child in self.menu.children:
            self.add_bind(child)

    def run_level(self, location, level):
        bboard = BlackBoard()
        bboard.load_level(0)
        self.parent.add_widget(bboard)
        self.parent.remove_widget(self)
