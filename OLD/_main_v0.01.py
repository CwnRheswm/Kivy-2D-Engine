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
        oP = Vector(400,400)
        #gP = Vector(812,456)
        bd = Vector((250,250),(500,400))
        vt = Vector(0,0)
        rP = Vector(400,300)
        rS = 135
        
        a,b = find_impact_points(oP,bd,vt,rP,rS)
        #print ('ab: ',a,b)

        xy = Vector(400, 510)
        poI = Vector(400,410)
        uv = Vector(((xy[0] - poI[0]) * math.cos(math.radians(-180)))
                    - ((xy[1] - poI[1]) * math.sin(math.radians(-180))),
                    ((xy[0] - poI[0]) * math.sin(math.radians(-180)))
                    + ((xy[1] - poI[1]) * math.cos(math.radians(-180))))
        pq = Vector(((xy[0] - poI[0]) * math.cos(math.radians(-180*0.25)))
                    - ((xy[1] - poI[1]) * math.sin(math.radians(-180*0.25))),
                    ((xy[0] - poI[0]) * math.sin(math.radians(-180*0.25)))
                    + ((xy[1] - poI[1]) * math.cos(math.radians(-180*0.25))))
        ij = Vector(((xy[0] - poI[0]) * math.cos(math.radians(-135)))
                    - ((xy[1] - poI[1]) * math.sin(math.radians(-135))),
                    ((xy[0] - poI[0]) * math.sin(math.radians(-135)))
                    + ((xy[1] - poI[1]) * math.cos(math.radians(-135))))
        lm = Vector(((xy[0] - poI[0]) * math.cos(math.radians(-90)))
                    - ((xy[1] - poI[1]) * math.sin(math.radians(-90))),
                    ((xy[0] - poI[0]) * math.sin(math.radians(-90)))
                    + ((xy[1] - poI[1]) * math.cos(math.radians(-90))))
        uv = uv + poI
        pq = pq + poI
        ij = ij + poI
        lm = lm + poI
        
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(size=(800, 600), pos=(0,0))

            Color(0,0,1,1)
            Ellipse(size=(15,15), pos=(xy[0]-7.5, xy[1]-7.5))
            Color(1,1,0,1)
            Ellipse(size=(10,10), pos=(uv[0]-5, uv[1]-5))
            Color(0,1,1,1)
            #Ellipse(size=(10,10), pos=(395,295))
            #Ellipse(size=(10,10), pos=(pq[0]-5, pq[1]-5))
            #Ellipse(size=(10,10), pos=(ij[0]-5, ij[1]-5))
            #Ellipse(size=(10,10), pos=(lm[0]-5, lm[1]-5))
            
            Color(1,0,0,1)
            Ellipse(size =(10,10), pos=(b[0][0]-5, b[0][1]-5))
            Color(1,0,0,1)
            Ellipse(size =(10,10), pos=(b[1][0]-5, b[1][1]-5))
            Line(width = 1, points =(b[0][0], b[0][1], b[1][0], b[1][1]))
            Color(1,0,1,1)
            Ellipse(size =(5,5), pos=(b[2][0]-2.5, b[2][1]-2.5))
            Ellipse(size =(5,5), pos=(b[10][0]-2.5, b[10][1]-2.5))
            Line(width = 1, points=(b[10][0], b[10][1], b[17][0], b[17][1]))
            #Ellipse(size =(5,5), pos=(b[11][0]-2.5, b[11][1]-2.5))
            Color(1,1,0,1)
            Ellipse(size =(5,5), pos=(b[3][0]-2.5, b[3][1]-2.5))
            Line(width = 1, points = (b[2][0],b[2][1],b[3][0],b[3][1]))

            Color(0,1,0,1)
            #Ellipse(size =(5,5), pos=(b[4][0]-2.5, b[4][1]-2.5))
            #Ellipse(size =(5,5), pos=(b[5][0]-2.5, b[5][1]-2.5))
            Line(width = 1, points=(b[4][0], b[4][1], b[5][0], b[5][1]))
            #Ellipse(size =(5,5), pos=(b[6][0]-2.5, b[6][1]-2.5))

            #Color(0,0,1,1)
            #Ellipse(size =(5,5), pos=(b[7][0]-2.5, b[7][1]-2.5))
            #Color(0,1,1,1)
            #Ellipse(size =(5,5), pos=(b[8][0]-2.5, b[8][1]-2.5))
            #Line(width=1, points=(b[8][0],b[8][1],b[4][0],b[4][1]))
            #Line(width=1, points=(b[8][0],b[8][1],b[5][0],b[5][1]))

            #Color(0,0,0,1)
            #Ellipse(size =(5,5), pos=(b[9][0]-2.5, b[9][1]-2.5))

            [h,k],r = b[12]
            print ('center: ',h,k, 'radius: ',r)
            Color(1,0,0,1)
            Ellipse(size=(10,10), pos=(h-5, k-5))
            u,v = int(h-r), int(h+r)
            for x in range(u,v):
                #(x-p)^2 +(y-q)^2 - r^2 = 0
                #x^2 - 2px + p^2 + q^2 - r^2 = 2yq - y^2
                y = k + math.sqrt(round((r**2-((x-h)**2))))
                #y = (A*(x**2)) + (B*x) + C
                Color(0,0,1,1)
                Ellipse(size=(2,2), pos=(x-1, y-1))
                y = k - math.sqrt(round((r**2-((x-h)**2))))
                Color(0.2,0.2,1,1)
                Ellipse(size=(2,2), pos=(x-1, y-1))
            '''i,j = h-50, k-50
            Color(0,0,0,1)
            Ellipse(size=(10,10), pos=(i-5, j-5))
            u,v = int(i-r), int(i+r)
            for x in range(u,v):
                y = j + math.sqrt(round((r**2-((x-i)**2))))
                Color(0,0.5,1,1)
                Ellipse(size=(2,2), pos=(x-1, y-1))
                y = j - math.sqrt(round((r**2-((x-i)**2))))
                Ellipse(size=(2,2), pos=(x-1, y-1))
            i,j = h-25, k-25
            Color(0.5,0,0,1)
            Ellipse(size=(10,10), pos=(i-5, j-5))
            u,v = int(i-r), int(i+r)
            for x in range(u,v):
                y = j + math.sqrt(round((r**2-((x-i)**2))))
                Color(0,0.2,0.5,1)
                Ellipse(size=(2,2), pos=(x-1, y-1))
                y = j - math.sqrt(round((r**2-((x-i)**2))))
                Ellipse(size=(2,2), pos=(x-1, y-1))'''


            #Ellipse calculations
            '''
            the major axis is found by finding line between both foci, original point of rotation and point of rotation plus any velocity
            the minor axis if found be bisecting that line
            b = the radius length of the minor axis is found by the length of from the original point of rotation to the original rotating point
            a = the radius length of the major axis is found by adding the radius length of the minor axis to the length between a focus and the center
            
            '''
            
            ya = 100 #minor axis
            xa = 100 + math.sqrt(((h -h)**2) + ((k - (k-50))**2))
            print('major axis: ' + str(xa))
            h,k = h-50, k-50
            h1,k1=h+50,k+50
            h2,k2=h-50,k-50
            rads = math.atan2(h1-h2, k1-k2)
            deg = 180/math.pi
            print('deg :', deg)
            u = Vector(math.cos(deg),math.sin(deg))
            v = Vector(-math.sin(deg),math.cos(deg))
            print(u,v)
            Color(0,1,0,1)
            Ellipse(size=(4,4), pos=(h1-2,k1-2))
            Color(0,0,1,1)
            Ellipse(size=(4,4), pos=(h2-2,k2-2))
            '''for theta in range(0,360):#135,135+360):
                #theta = theta-135
                x = h + xa*math.cos(theta)
                y = k + ya*math.sin(theta)
                x,y = Vector(h,k) + Vector((xa*math.cos(theta))*u) + Vector((ya*math.sin(theta))*v)
                Color(1,1,0.2,1)
                Ellipse(size=(2,2), pos=(x-1,y-1))
                #if (theta-135)%20 == 0:
                if int((180/math.pi) * math.atan2((x)-h1,(y)-k1)) == 0 or int((180/math.pi) * math.atan2((x)-h1,(y)-k1)) == 90 or int((180/math.pi) * math.atan2((x)-h2,(y)-k2)) == 180 or int((180/math.pi) * math.atan2((x)-h2,(y)-k2)) ==270:
                    #Color(1,0,0,1)
                    #Line(width=1, points=(h,k,x,y))
                    p1 = [x - h1, y - k1] #hk1_to_xy
                    p2 = [h2- h1, k2- k1] #hk1_to_h2

                    p2_2 = p2[0]**2 + p2[1]**2
                    p1_2 = p1[0]*p2[0] + p1[1]*p2[0]

                    t = p1_2 / p2_2
                    xv, yv = h1 + p2[0] * t, k1 + p2[1] * t
                    #print('Line '+str(theta/20)+' length = '+str(math.sqrt(((x-xv)**2) + ((y-yv)**2))))
                    Color(0,0,1,1)
                    Line(width = 1, points=(xv,yv,x,y))

                    #v = Vector(h1,k1) - Vector(h2,y2)
                    print('xy: ' +str(theta)+' '+str(x)+' '+str(y))
                    Color(1,0,1,1)
                    Ellipse(size=(10,10), pos=(x-5,y-5))

                    #if theta==0:
                    #print('Line 0: '+str(math.sqrt(((x-h1)**2) + ((y-k1)**2))))'''
                    
            int1, int2 = b[13]
            int3, int4 = b[14]
            #print ('intercepts of circle: ' + str(int1) + ' and ' + str(int2))
            #print ('intercepts on line: ' + str(int3) + ' and ' + str(int4))
            Color(1,0.7,0.7,1)
            Ellipse(size=(20,20), pos=(b[13][0][0] - 10, b[13][0][1] - 10))
            Line(width = 1, points=(b[13][0][0],b[13][0][1],b[16][0],b[16][1]))
            Color(1,0.7,0,1)
            Ellipse(size=(16,16), pos=(int3[0] - 8, int3[1] - 8))

            #Color(0.2,0.7,0.4,1)
            #Ellipse(size=(12,12), pos=(b[13][1][0] - 6, b[13][1][1] -6))
            #Color(0.2,0.7,0,1)
            #Ellipse(size=(16,16), pos=(int4[0] - 8, int4[1] - 8))

            Color(1,1,0.3,1)
            Ellipse(size=(8,8), pos=(b[15][0] - 4, b[15][1] - 4))

            '''a,b,c = b[18]
            for x in range(0,800):
                y = (a*(x**2)) + (b*x) + c
                Color(0,0,0,1)
                Ellipse(size=(2,2), pos=(x-1,y-1))'''
            Color(1,1,1,1)
            Rectangle(size=(self.size))
            u,v = 60, -100
            h,k = 0,100.0
            rads = -90
            for i in range(h,int(k)):
                pq = Vector(((((xy[0] + (u*(i/k))) - (poI[0] + (u*(i/k)))) * math.cos(math.radians(rads *(i/k))))
                            - ((xy[1] + (v*(i/k))) - (poI[1] + (v*(i/k)))) * math.sin(math.radians(rads *(i/k)))),
                            (((xy[0] + (u*(i/k))) - (poI[0] + (u*(i/k)))) * math.sin(math.radians(rads *(i/k))))
                            + (((xy[1] + (v*(i/k))) - (poI[1] + (v*(i/k)))) * math.cos(math.radians(rads *(i/k)))))
                pq = pq + (poI[0] + (u*(i/k)), poI[1] + (v*(i/k)))

                ij = Vector(((((xy[0] + (u*(i/k))) - (poI[0] + (u*(i/k)))) * math.cos(math.radians(-rads *(i/k))))
                            - ((xy[1] + (v*(i/k))) - (poI[1] + (v*(i/k)))) * math.sin(math.radians(-rads *(i/k)))),
                            (((xy[0] + (u*(i/k))) - (poI[0] + (u*(i/k)))) * math.sin(math.radians(-rads *(i/k))))
                            + (((xy[1] + (v*(i/k))) - (poI[1] + (v*(i/k)))) * math.cos(math.radians(-rads *(i/k)))))
                ij = ij + (poI[0] + (u*(i/k)), poI[1] + (v*(i/k)))
                Color(0,0,0,1)
                Ellipse(size=(2,2), pos=(pq[0]-1, pq[1]-1))
                Color(0,0,1,1)
                Ellipse(size=(2,2), pos=(ij[0]-1, ij[1]-1))
                Color(1,0,0,1)
                Ellipse(size=(2,2), pos=(poI[0]+ (u*(i/k)), poI[1] + (v*(i/k))))
                Color(0,1,0,1)
                Line(width = 1, points=(b[4][0], b[4][1], b[5][0], b[5][1]))

                [x1,y1],[x2,y2] = [bd[0][0],bd[0][1]],[bd[1][0],bd[1][1]]
                x,y = pq[0], pq[1]
                print((x,y),i)
                if ( (((y1-y2) * (x-x1)) + ((x2-x1) * (y-y1))) ) <= 0:
                    #print( (((y1-y2) * (x-x1)) + ((x2-x1) * (y-y1))) )
                    #Color(1,1,0,1)
                    #Ellipse(size=(10,10), pos=(x-5, y-5))
                    pq2 = pq
                    pq3 = line_intersect([[pq2[0],pq2[1]], [pq1[0],pq1[1]]],[[x1,y1],[x2,y2]])
                    print(pq3)
                    Color(1,1,0,1)
                    Ellipse(size=(10,10), pos=(pq3[0]-5, pq3[1]-5))

                    print('pq3 - pq1: ' +str(math.sqrt(((pq3[0] - pq1[0]) ** 2) + ((pq3[1] - pq1[1]) ** 2)))+ '; pq2 - pq1: ' +str(math.sqrt(((pq2[0] - pq1[0]) ** 2) + ((pq2[1] - pq1[1]) ** 2))))
                    percent = (math.sqrt(((pq3[0] - pq1[0]) ** 2) + ((pq3[1] - pq1[1]) ** 2))) / (math.sqrt(((pq2[0] - pq1[0]) ** 2) + ((pq2[1] - pq1[1]) ** 2)))
                    print('percent: '+str(percent))
                    #percentMovement = ((i + (i-1)) / 2) / k
                    percentMovement = ((i - 1) + percent) / k
                    print('percentMovement: '+str(percentMovement))

                    pq4 = Vector(((((xy[0] + (u*(percentMovement))) - (poI[0] + (u*(percentMovement)))) * math.cos(math.radians(rads *(percentMovement))))
                                  - ((xy[1] + (v*(percentMovement))) - (poI[1] + (v*(percentMovement)))) * math.sin(math.radians(rads *(percentMovement)))),
                                  (((xy[0] + (u*(percentMovement))) - (poI[0] + (u*(percentMovement)))) * math.sin(math.radians(rads *(percentMovement))))
                                  + (((xy[1] + (v*(percentMovement))) - (poI[1] + (v*(percentMovement)))) * math.cos(math.radians(rads *(percentMovement)))))
                    pq4 = Vector(pq4 + (poI[0] + (u*(percentMovement)), poI[1] + (v*(percentMovement))))
                    print(pq4)
                    Color(1,0,0,1)
                    Ellipse(size=(10,10), pos=(pq4[0]-5, pq4[1]-5))
                    if (point_on_lines(pq4, [[[x1,y1],[x2,y2]]])):
                        break
                    print( (((y1-y2) * (pq[0] - x1)) + ((x2 - x1) * (pq[1] - y1))) )

                    AP = Vector(pq4 - Vector(bd[0]))
                    print('AP: '+str(AP)+str(((pq4[0]-bd[0][0]),(pq[1]-bd[0][1]))))
                    AB = Vector(Vector(bd[1]) - Vector(bd[0]))
                    print('AB: '+str(AB))
                    ab2 = AB[0]**2 + AB[1]**2
                    ap_ab = AP[0]*AB[0] + AP[1]*AB[1]
                    t = ap_ab / ab2
                    print('t: '+str(t))
                    closest_point = Vector(Vector(bd[0]) + (AB * t))
                    closest_point = round(closest_point[0],2), round(closest_point[1],2)
                    
                    #M = (y2-y1)/(x2-x1)
                    #B = y1 - M*x1
                    #closest_point = (abs(pq4[1] - (M * pq[0]) - B )) / (math.sqrt((M**2) + 1))
                    print('closest: ' + str(pq4) + ' ' +str(closest_point))
                    #break
                pq1 = pq

            '''theta = (math.pi * 90)/180
            radius = 100
            a = -50
            x = (poI[0] + a) + radius * cos(theta)'''
            print( (((y1 - y2) * (350 - x1)) + ((x2 - x1) * (700 - y1))) )
            print( (((y1 - y2) * (350 - x1)) + ((x2 - x2) * (200 - y1))) )
                            
            
class FlanQuest(App):
    def build(self):
        root = Widget()
        win = Window
        #win.fullscreen = True
        #root.add_widget(SplashScreen())
        root.add_widget(TestBoard())
        
        return root

    '''Needs functions to listen to SplashScreen() and what it returns and to switch
    to BlackBoard() or WhiteBoard()
    '''

if __name__ == "__main__":
    FlanQuest().run()
    
