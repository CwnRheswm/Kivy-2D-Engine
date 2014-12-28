import math

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.uix.widget import Widget
from kivy.vector import Vector

from _welcome import SplashScreen
from _boards import BlackBoard, WhiteBoard, line_intersect, point_on_lines
from impactpoints import find_impact_points
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
class TestBoard(Widget):
    def __init__(self):
        Widget.__init__(self)

        self.size = (800,600)
        bd = Vector((250,250),(500,400))
        u,v = Vector(60,-100)
        rad = 135
        
        xy = Vector(400, 510)
        poI = Vector(400,410)
        
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(size=(self.size))
            for rads in (340,360):
                steps = 100.0
                Color(0,1,0,1)
                Line(width = 1, points=(bd[0][0], bd[0][1], bd[1][0], bd[1][1]))

                for i in range(0,int(steps)):
                    pq = Vector(((((xy[0] + (u*(i/steps))) - (poI[0] + (u*(i/steps)))) * math.cos(math.radians(rads *(i/steps))))
                                 - ((xy[1] + (v*(i/steps))) - (poI[1] + (v*(i/steps)))) * math.sin(math.radians(rads *(i/steps)))),
                                (((xy[0] + (u*(i/steps))) - (poI[0] + (u*(i/steps)))) * math.sin(math.radians(rads *(i/steps))))
                                + (((xy[1] + (v*(i/steps))) - (poI[1] + (v*(i/steps)))) * math.cos(math.radians(rads *(i/steps)))))
                    pq = pq + (poI[0] + (u*(i/steps)), poI[1] + (v*(i/steps)))

                    Color(0,0,0,1)
                    Ellipse(size=(2,2), pos=(pq[0]-1, pq[1]-1))
                    Color(1,0,0,1)
                    Ellipse(size=(2,2), pos=(poI[0]+ (u*(i/steps)), poI[1] + (v*(i/steps))))
                    
                    [x1,y1],[x2,y2] = [bd[0][0],bd[0][1]],[bd[1][0],bd[1][1]]
                    x,y = pq[0], pq[1]
                    #print((x,y),i)
                    if ( (((y1-y2) * (x-x1)) + ((x2-x1) * (y-y1))) ) <= 0:
                        pq2 = pq
                        pq3 = line_intersect([[pq2[0],pq2[1]], [pq1[0],pq1[1]]],[[x1,y1],[x2,y2]])
                        #Color(1,1,0,1)
                        #Ellipse(size=(10,10), pos=(pq3[0]-5, pq3[1]-5))

                        percent = (math.sqrt(((pq3[0] - pq1[0]) ** 2) + ((pq3[1] - pq1[1]) ** 2))) / (math.sqrt(((pq2[0] - pq1[0]) ** 2) + ((pq2[1] - pq1[1]) ** 2)))
                        percentMovement = ((i - 1) + percent) / steps
                        
                        pq4 = Vector(((((xy[0] + (u*(percentMovement))) - (poI[0] + (u*(percentMovement)))) * math.cos(math.radians(rads *(percentMovement))))
                                      - ((xy[1] + (v*(percentMovement))) - (poI[1] + (v*(percentMovement)))) * math.sin(math.radians(rads *(percentMovement)))),
                                      (((xy[0] + (u*(percentMovement))) - (poI[0] + (u*(percentMovement)))) * math.sin(math.radians(rads *(percentMovement))))
                                      + (((xy[1] + (v*(percentMovement))) - (poI[1] + (v*(percentMovement)))) * math.cos(math.radians(rads *(percentMovement)))))
                        pq4 = Vector(pq4 + (poI[0] + (u*(percentMovement)), poI[1] + (v*(percentMovement))))
                        Color(0,1,1,1)
                        Ellipse(size=(10,10), pos=(pq4[0]-5, pq4[1]-5))
                        break
                        '''if (point_on_lines(pq4, [[[x1,y1],[x2,y2]]])):
                            break
                            
                        else:
                            AP = Vector(pq4 - Vector(bd[0]))
                            AB = Vector(Vector(bd[1]) - Vector(bd[0]))
                            ab2 = AB[0]**2 + AB[1]**2
                            ap_ab = AP[0]*AB[0] + AP[1]*AB[1]
                            t = ap_ab / ab2
                            closest_point = Vector(Vector(bd[0]) + (AB * t))
                            closest_point = round(closest_point[0],1), round(closest_point[1],1)
                            print('closest: ',pq4,round(pq4[0],1),round(pq4[1],1), closest_point)
                            break'''
                    pq1 = pq
                            
            
class FlanQuest(App):
    def build(self):
        root = Widget()
        win = Window
        #win.fullscreen = True
        root.add_widget(SplashScreen())
        #root.add_widget(TestBoard())
        
        return root

    '''Needs functions to listen to SplashScreen() and what it returns and to switch
    to BlackBoard() or WhiteBoard()
    '''

if __name__ == "__main__":
    FlanQuest().run()
    
