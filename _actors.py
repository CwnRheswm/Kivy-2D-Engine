import math
import os
import random

from kivy.graphics import Color, Rectangle, Ellipse #Assess neccesity
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock, ClockBase
from kivy.core.image import Image as Sheet
from kivy.properties import AliasProperty
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.vector import Vector

'''
-------------------------
Initial class is Actor, which is an instantiation of the Scatter() class
    This should hold on the common functions and variables that every "Actor"
    in the game needs.
This is further instantiated by each unique Actor() class, i.e. Flan(), Fruit(), Floor(), Etc()
    these hold the specific information for each of those classes
    e.g. only Flan() and Fruit() [and maybe some of the other obsticle actors] have Expression()s
    the Flan faces, the blueberry fruit's "shine"
The basic collision system for straight line object is uniform, and the basic collision for
circular objects should be unifrom. I.e. only two types of collision functions should be neccessary
Collectable materials have a different collision becuase you don't (typically) bounce off of them
you collect them upon collision. They also don't [typically] respond to gravity.

#Collision functions should return necessary information to its parent [B/WBoard()]

Perform collisions with screen. Grab all actors, project their position into the next step
and determine which if any will collided given their velocity. Then run collision functions.

Animations======================
    stand: basic animation, movement animation for Fruits
        Flan: 3 frame animation of light bouncing
            FlanEyes: 5 or so different eye types that lay on top of the flan
                      e.g. Angry, Happy, Gleeful, Sleepy, Bored
        Fruit: 1 frame animation that simply rotates as it bounces around
            FruitEyes: basic eyes
    stand1:
        Flan: 
            FlanEyes:
        Fruit:
            FruitEyes:
    stand2:
    hit: animation when struck by another Actor()
        Flan: bounce/jiggle
            FlanEyes: respond appropriately
        Fruit: nothing
            FruitEyes: get wide
    plucked: immediately after being plucked
        Flan: squeezed like a balloon to one side
            FlanEyes: respond with bigger eyes and animated expressions
                      e.g. Angry gets mad, Gleeful acts tickled
    annoyed: after being plucked and held long
        Flan: extension of plucked, wiggle and shake
            FlanEyes: extend the expression
    angry: after being plucked and held too long, eventually settles down and resets to plucked
        Flan: extension of annoyed
            FlanEyes: even bigger expression than annoyed
    walk:
        Fruit: walking along surfaces, before start and after hitting finish
            FruitEyes: normal
    climb:
        Fruit: climbing up or down any ladders they might climb
            FruitEyes: normal
    double:
        Flan: animation on double ability use
    move:
        Flan: animation on move ability use
    swipe:
        Flan: animation on swipe ability use, e.g. chili tongue
    hold:
        Flan: animation on hold ability use
-------------------------
'''

FLANSIZE = [150, 75]

class Sprite(Image): #will need to add animations
    def __init__(self,size,image):
        Image.__init__(self)

        sheet = Sheet((os.path.join('Images',image + '.png'))).texture
        
        #width = sheet.width
        #height = sheet.height
        #width = FLANSIZE[0]
        #height = FLANSIZE[1]
        self.pos = (0,0)

        self.animations = {}
        #self.stand = sheet.get_region(0, 0, width, height)
        #self.texture = self.stand
        self.texture = sheet
        self.size = (size)

        #with self.canvas:
            #Color(1,0,0,1)
            #Rectangle(size = self.size)


    def add_anim(self, **attr):
        '''
        method for adding sheet regions to an animation dictionary
        '''
        pass
    
class Actor(Scatter):
    def __init__(self):
        Scatter.__init__(self)

        self.do_scale = False
        self.do_rotate = False
        self.do_translation = False

        # set movement attributes
        self.attach = None
        self.impacts = {}#[None, None]      #list of the friction and elastic of an impacted target
        #self.impactPt = [[]]            #does Actor() have a point-of-impact due to interesecting another widget
        #self.impactLn = []              #the Actor()'s line and the target's line that are intersecting
        self.cog = None                 #center of gravity, average of all points
        self.prevSlope = None           #holds Actor()s previous slope in the case of rotational collision computations
        self.selfSlope = None           #holds Actor()s current slope in the case of rotational collision computation
        self.surfSlope = None           #holds the surface slope of a widget with which an Actor() has collided or intersected
        self.rotDir = 0                 #holds the Actor()s current rotation direction; 1 = counterclockwise, -1 = clockwise, 0 = none
        self.touch_dt = 0.0             #holds the float for how long a touch has been on an Actor()
        self.target = []                #holds a list of the widgets with which an Actor() has collided
        self.vDelt = Vector(0.0,0.0)    #holds the current change of velocity the Actor() is experiencing
        self.velocity = Vector(0.0,0.0) #holds the current velocity the Actor() will experience in the next step
        self.friction = 0.01            #friction experienced by objects that intersect against the Actor()
        self.elastic = 1                #elasticity experience by objects that bounce off of the Actor()
        self.bounce = 0.01              #the amount the actor will bounce on collisions
        self.stability = [25,45,55]     #the three thresholds where behaviour relating to a slope changes
        self.movement = []              #list of positions through which an Actor() with a set movement pattern will move
        self.rotSpd = 1                 #how quickly an Actor() will move
        self.rotBound = []              #list of two rotation position that define a max and min rotation boundary for an Actor()
        self.scaling = 1
        
class Flan(Actor):
    def __init__(self, attr):
        Actor.__init__(self)
        print(attr)
        #self.xy = self.center
        self.scaling = 0.45
        self.size = Vector(FLANSIZE) * self.scaling
        self.rotate = self.rotation
        
        if 'flav' in attr.keys():
            self.set_flavour(attr['flav'])
        if 'img' in attr.keys():
            self.image = attr['img']
        if 'size' in attr.keys():
            self.size = attr['size']
        if 'cent' in attr.keys():
            self.center = attr['cent']
        if 'rotation' in attr.keys():
            self.rotation = attr['rotation']
        if 'elas' in attr.keys():
            self.elastic = attr['elas']
        if 'fric' in attr.keys():
            self.friction = attr['fric']
        if 'boun' in attr.keys():
            self.bounce = attr['boun']
        if 'rSpd' in attr.keys():
            self.rotSpd = attr['rSpd']
        if 'shap' in attr.keys():
            self.shape = attr['shap']

        #self.size = Vector(FLANSIZE) * self.scale #self.sprite.size
        self.sprite = Sprite(self.size, self.image)
        self.add_widget(self.sprite)
        
        self.animations = {}
        #add
        self.abilities = {'move': None,
                          'double': None,
                          'hold': None,
                          'swipe': None}
        
    def set_flavour(self, flavour):
        if flavour == 'vla': #vanilla, basic
            #self.expression =
            self.elastic = 0.85
            self.friction = 1
            self.bounce = 0.0
            self.rotSpd = 1
            self.shape = {'rect': 17}
            self.image = 'vanilla'
        elif flavour == 'chl': #chili, spicy & fire tongue
            pass

    
    
class Fruit(Actor):
    def __init__(self, attr):
        Actor.__init__(self)

        self.size = (25,25)

        if 'flav' in attr.keys():
            self.set_flavour(attr['flav'])
        if 'img' in attr.keys():
            self.image = attr['img']
            
        self.sprite = Sprite((25,25), self.image)
        self.add_widget(self.sprite)
        self.size = self.sprite.size
        
        self.xy = self.center
        self.rotate = self.rotation
        
        if 'size' in attr.keys():
            self.size = attr['size']
        if 'cent' in attr.keys():
            self.center = attr['cent']
        if 'elas' in attr.keys():
            self.elastic = attr['elas']
        if 'fric' in attr.keys():
            self.friction = attr['fric']
        if 'boun' in attr.keys():
            self.bounce = attr['boun']
        if 'rSpd' in attr.keys():
            self.rotSpd = attr['rSpd']
        if 'shap' in attr.keys():
            self.shape = attr['shap']

    def set_flavour(self, flavour):
        if 'blb' in flavour:
            #self.image = 'blueberry.png'
            self.elastic = 1
            self.friction = 0
            self.bounce = 1
            self.rotSpd = 1
            self.shape = {'circ': 8}
            self.image = 'blue1'

class Floor(Actor):
    def __init__(self, attr):
        Actor.__init__(self)
        
        if 'size' in attr.keys():
            self.size = attr['size']
        if 'rotation' in attr.keys():
            self.rotation = attr['rotation']
        if 'mat' in attr.keys():
            self.set_material(attr['mat'])
        if 'img' in attr.keys():
            self.image = attr['img']
        if 'cent' in attr.keys():
            self.center = attr['cent']
           
        #self.sprite = Sprite(self.size)#, self.image)
        #self.add_widget(self.sprite)
        
        self.xy = self.center
        self.rotate = self.rotation

        if 'elas' in attr.keys():
            self.elastic = attr['elas']
        if 'fric' in attr.keys():
            self.friction = attr['fric']
        if 'boun' in attr.keys():
            self.bounce = attr['boun']
        if 'rSpd' in attr.keys():
            self.rotSpd = attr['rSpd']
        if 'poI' in attr.keys():
            self.attach = attr['poI']
        if 'rBnd' in attr.keys():
            self.rotMin = attr['rBnd'][0]
            self.rotMax = attr['rBnd'][1]
            self.rotDirect = attr['rBnd'][2]
        if 'mvmt' in attr.keys():
            self.movement = []
            for pos in attr['mvmt']:
                self.movement.append(pos)
        if 'shap' in attr.keys():
            self.shape = attr['shap']
        if 'alt' in attr.keys():
            self.alt = attr['alt']
        else:
            self.alt = 'None'

        with self.canvas:
            Color(1,0,0,1)
            Rectangle(size = self.size)
        
    def set_material(self, material):
        if 'plc' in material:
            self.elastic = 1
            self.friction = .9
            self.bounce = 1
            self.rotSpd = 1
            self.shape = {'rect': 0}
        elif 'gls' in material:
            pass
#class ...(Actor):
#    pass
