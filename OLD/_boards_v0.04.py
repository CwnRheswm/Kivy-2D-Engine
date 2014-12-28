import os, random

from kivy.clock import Clock
from kivy.core.image import Image as Sheet
from kivy.graphics import Color, Line, Ellipse
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.vector import Vector

from math import tan, radians, sin, cos, copysign, sqrt, e as E

from _actors import Flan, Floor, Fruit
from _open_level_file import read_level, save_level

'''
Changelog:
  Need to:
      
'''
def scatter_ghost(target):
    ghost = Scatter()
    ghost.size = target.ize
    ghost.rotation = target.rotation
    ghost.pos = target.pos
    ghost.scale = target.scale
    ghost.velocity = target.velocity
    ghost.clone = target
    ghost.shape = target.shape
    ghost.elastic = target.elastic
    ghost.friction = target.friction
    ghost.bounce = target.bounce
    ghost.rotSpd = target.rotSpd

    return ghost
              
def get_widget_bounds(widget):
    center = widget.center
    rotation = widget.rotation

    widget.center = (0,0)
    widget.rotation = 0

    pointsDict = {}

    if 'circ' in widget.shape:
        points = widget.shape['circ']
        cut_in = 0
        rads = 360/points
        for p in range(points):
            a = cos(radians(360 - (p * rads)))
            b = sin(radians(360 - (p * rads)))
            #print(a, b, Vector(widget.size) /2.0)
            x, y = ((Vector(widget.center) + (Vector(a,b) * (Vector(widget.size) / 2.0))))
            pointsDict[p] = [x,y]
            #print('in bounds: ',p,pointsDict[p])
            
    elif 'rect' in widget.shape:
        points = 4
        cut_in = widget.shape['rect'] * widget.scaling
        pointsDict[0] = Vector(widget.x, widget.y)
        pointsDict[1] = Vector((widget.x + cut_in), widget.top)
        pointsDict[2] = Vector((widget.right - cut_in), widget.top)
        pointsDict[3] = Vector(widget.right, widget.y)
        
    widget.rotation = rotation
    widget.center = center

    cog = [0,0]
    for point in pointsDict.keys():
        x, y = pointsDict[point]
        
        xPrime = ((x * cos(radians(rotation))) + (y * -sin(radians(rotation))))
        yPrime = ((x * sin(radians(rotation))) + (y *  cos(radians(rotation))))

        xPrime, yPrime = Vector(xPrime, yPrime) + Vector(center)
        
        pointsDict[point] = Vector(xPrime, yPrime)
        cog[0] += xPrime
        cog[1] += yPrime

    cog[0] = cog[0] / (len(pointsDict.keys()))
    cog[1] = cog[1] / (len(pointsDict.keys()))
    
    widget.cog = cog
    
    return pointsDict
    
def check_stability(actor, gravity): #(points, impactPt, impactLn, stability, fall):
    #print('semi stable')
    rotDir = 0
    velocity = Vector(0,0)

    impacts = actor.impacts
    push, fall = gravity
    
    #find maximum and minimum x coords of impacted points
    min_x = str()
    max_x = None
    for num in impacts.keys():
        if num != 'rotPt':
            point = impacts[num]['pt']
            if point[0] < min_x:
                min_x = point[0]
                left = num
            if point[0] > max_x:
                max_x = point[0]
                right = num
    
    min_y = str()
    for num in impacts.keys():
        if type(num) == int:
            if impacts[num]['pt'][1] < min_y:
                min_y = impacts[num]['pt'][1]
                bottom = num

    line = None
    targets = []
    for num in impacts.keys():
        if type(num) != str:
            for target in impacts[num].keys():
                if type(target) != str:
                    targets.append(target)
    for target in targets:
        if target in impacts[bottom].keys():
            line = impacts[bottom][target]['ln']#[0]
            hit = target

    if line != []:
        dX = line[0][0] - line[1][0]
        dY = line[0][1] - line[1][1]
        if dX == 0:
            slope = 0
        else:
            slope = dY / dX
        if abs(slope) > tan(radians(actor.stability[0])):
            velocity = Vector(actor.velocity) + (Vector(fall / slope, fall))

    if actor.cog[0] > max_x:
        rotDir = -1
        actor.impacts['rotPt'] = impacts[right]['pt']
    elif actor.cog[0] < min_x:
        rotDir = 1
        actor.impacts['rotPt'] = impacts[left]['pt']
    actor.rotDir = rotDir
    actor.velocity = velocity

def bounce(actor, bounceList):
    print('pre bounce: '+str(actor.velocity))#+'\nimpacts: '+str(actor.impacts))
    bounceThreshold = 0.01 * 30
    rotDir = 0

    velocities = []
    for i in range(len(bounceList)):
        num, target = bounceList[i]
        
        friction = actor.impacts[num][target]['f']
        elastic = actor.impacts[num][target]['e']
        bounce = actor.bounce
        v = actor.velocity

        [x,y],[p,q] = actor.impacts[num][target]['ln']
    
        n = Vector(-(q-y), (p-x)).normalize()
        #print('n: '+str(n)+'\n'+str(x)+' '+str(y)+' '+str(p)+' '+str(q))
        u = (v.dot(n) / n.dot(n)) * n
        w = v - u
        
        new_v = (friction * w * bounce) - ([elastic * bounce * u[0], elastic * bounce * u[1]])
        print('friction * w: '+str(friction*bounce * w)+'\nebu: '+str(elastic * bounce * u[0])+' '+str(elastic * bounce * u[1]))
        velocities.append(new_v)

    a = 0
    b = 0

    for i in range(len(velocities)):
        a += velocities[i][0]
        b += velocities[i][1]
    
    a = a / len(velocities)
    b = b / len(velocities)
    
    velocity = Vector(a,b )
    #print('bounce: ' +str(velocity)+' '+str(actor.velocity))
    if abs(velocity[1]) < bounceThreshold and abs(velocity[0]) < bounceThreshold:
        print('threshold')
        actor.velocity = Vector(0,0)
        print('bounce List: '+str(bounceList))
        for i in range(len(bounceList)):
            num, target = bounceList[i]
            actor.impacts[num][target]['e'] = []
    else:
        actor.velocity = velocity
        print('bounce: '+str(velocity))
        #print('bounce: '+str(actor.impacts))
        for i in range(len(bounceList)):
            num, target = bounceList[i]
            actor.impacts[num].pop(target)
            print(actor.impacts[num])
            if actor.impacts[num].keys() == ['pt']:
                actor.impacts.pop(num)
                #print('pop: ', actor.impacts, num)
            
        if velocity[0] < 0:
            actor.rotDir = 1
        elif velocity[0] > 0:
            actor.rotDir = -1
    #print('bounce velocity: '+str(actor.velocity)+str(velocity))
    
    return
    
def gravity(actors, gravity):
    '''
    '''
    terminalV = 3000.3
    terminalH = 3.3
    push = gravity[0]
    fall = gravity[1] #default of -0.1
    friction = 0.0001
    
    for actor in actors:
        #if type(actor) == Fruit:
            #print('gravity, velocity: '+str(actor.velocity))
        actor.rotDir = 0
        if actor.impacts.keys() != []:
            #print('stable '+str(actor.velocity))
            check_stability(actor, gravity)
                
        else:
            #print('pre gravity: '+str(actor.velocity))
            actor.velocity = Vector(actor.velocity) + Vector(push, fall)
            #print('fall '+str(actor.velocity))
            if abs(actor.velocity[1]) > terminalV:
                actor.velocity[1] = copysign(terminalV, actor.velocity[1])
            #print('post gravity: '+str(actor.velocity))
            #    actor.velocity[1] += -(math.copysign(fall, actor.velocity[1]))
            #if abs(actor.velocity[0]) > 0:
            #    actor.velocity[0] += -(math.copysign(friction, actor.velocity[0]))

def get_ghosts(actors):
    for actor in actors:
        u,v = actor.velocity
        rad = actor.rotSpd
        direction = actor.rotDir
        if 'rotPt' in actor.impacts.keys():
            h,k = actor.impacts['rotPt']
        else:
            h,k = actor.cog
        
        ghostPoints = {}
        for point in actor.pointsDict.keys():
            x,y = actor.pointsDict[point]
            #print(point,str(':  '),x,y)
            new_point = Vector(((((x + u) - (h + u)) * cos(radians(rad * direction))) - (((y + v) - (k + v)) * sin(radians(rad * direction)))),
                               ((((x + u) - (h + u)) * sin(radians(rad * direction))) + (((y + v) - (k + v)) * cos(radians(rad * direction)))))
            #print(new_point)
            new_point = Vector(new_point) + Vector(h + u, k + v)
            #print(new_point)
            ghostPoints[point] = new_point
            
        actor.ghostPoints = ghostPoints
        #if type(actor) == Fruit:
            #print('get ghosts: '+str(actor.ghostPoints[0])+'\n'+str(u)+','+str(v)+'\n'+str(rad)+' '+str(direction)+'\n'+str(h)+','+str(k))
            
        
def pre_collided(actor, point, target):
    if point in actor.impacts.keys():
        if target in actor.impacts[point]['target']:
            return True
    return False
                    
def check_inside(points, lines):
    for point in points:
        x,y = point
        for line in lines:
            [x1,y1],[x2,y2] = line
            if (((y1-y2) * (x-x1)) + ((x2-x1) * (y-y1))) > 0:
                return False
    return True    
        
def get_collisions(actors, scenery):
    collisions = {}
    
    for target in scenery:
        target.ghostPoints = target.pointsDict
        
    for piece in actors + scenery:
        ghostLines =[]
        lines = []
        for i in piece.ghostPoints.keys():
            if i == len(piece.ghostPoints.keys()) - 1:
                j = 0
            else:
                j = i+1

            ghostLines.append([piece.ghostPoints[i], piece.ghostPoints[j]])
            lines.append([piece.pointsDict[i], piece.pointsDict[j]])
        piece.ghostLines = ghostLines
        piece.lines = lines

    for actor in actors:
        for target in actors + scenery:
            if actor != target: #check to make sure you aren't running the target against itself
                
                for point in actor.ghostPoints.keys():  #run each point in the actor against each target's lines
                    if target.collide_point(*(actor.ghostPoints[point])):
                        if check_inside([actor.ghostPoints[point]], target.ghostLines):
                            #if type(actor) == Fruit:
                                #print('collision, actor ghostPoints: '+str(actor.ghostPoints[point]))
                            if actor in collisions.keys():
                                if point in collisions[actor].keys():
                                    collisions[actor][point].append(target)
                                else:
                                    collisions[actor][point] = [target]
                            else:
                                collisions[actor] = {}
                                collisions[actor][point] = [target]
                
                for point in target.ghostPoints.keys(): #run each point in the target against the actors lines
                    if actor.collide_point(*(target.ghostPoints[point])):
                        if check_inside([target.ghostPoints[point]], actor.ghostLines):
                            if actor in collisions.keys():
                                if (point + 100) in collisions[actor].keys():
                                    collisions[actor][point + 100].append(target)
                                else:
                                    collisions[actor][point + 100] = [target]
                            else:
                                collisions[actor] = {}
                                collisions[actor][point + 100] = [target]
        #collisions now is a dictionary
        #collisions{ Flan_x_001 : { 0: Floor_x_005,
        #                           1: [Floor_x_006, Floor_x_007]},
        #            Flan_x_003 : { 3: Floor_x_005},
        #            Flan_x_005 : {100:Floor_x_010} }
        '''
        Flan1 intersects Floor5 @ it's 0 point, and Floor6 @ it's 1 point
        Flan3 intersects Floor5 @ it's 3 point
        Flan5 intersects Floor10@ Floor10's 0 point
        '''

    return collisions

def near(a, b, rtol = E + 5, atol = E + 8):
    return abs(a-b) < 0.01

def line_intersect(line1, line2):
    
    [x1,y1], [x2,y2] = line1
    [u1,v1], [u2,v2] = line2

    (a,b), (c,d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    e,f = u1-x1, v1-y1
    denom = float(a*d - b*c)
    if near(denom, 0):
        return False
    else:
        t = (e*d - b*f) / denom

        px = x1 + t * (x2-x1)
        py = y1 + t * (y2-y1)
        return (Vector(px, py))

def point_on_lines(point, lines):
    for line in lines:
        a, b, c = line[0], line[1], point

        for i in range(0,len(a)):
            a[i] = round(a[i], 1)
            b[i] = round(b[i], 1)
            c[i] = round(c[i], 1)

        crossproduct = (round(((c[1] - a[1]) * (b[0] - a[0])),1)) - (round(((c[0] - a[0]) * (b[1] - a[1])),1))
        if abs(crossproduct) > 10: #0.001:
            return False

        dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1]) * (b[1] - a[1])
        if dotproduct < 0:
            return False

        squaredLength = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])
        if dotproduct > squaredLength:
            return False
    return True

def check_border(body, ghost, lines):
    x,y = body
    p,q = ghost
    #print( lines )
    for line in lines:
        [x1,y1],[x2,y2] = line
        bodySide = copysign(1,(((y1-y2) * (x-x1)) + ((x2-x1) * (y-y1))))
        ghostSide = copysign(1,(((y1-y2) * (p-x1)) + ((x2-x1) * (q-y1))))
        if bodySide != ghostSide or bodySide == 0:
            return line
    return []
            
def find_percent_move(point, pivot, velocity, radian, line):
    x,y = point
    h,k = pivot
    u,v = velocity
    mn = [x,y]

    gx,gy = Vector( ((((x + u) - (h + u)) * cos(radians(radian))) - (((y + v) - (k+v)) * sin(radians(radian)))),
                    ((((x + u) - (h + u)) * sin(radians(radian))) + (((y + v) - (k+v)) * cos(radians(radian)))))
    gx,gy = Vector(gx,gy) + Vector(h+u, k+v)

    movements = {}
    steps = 100.0
    [x1,y1],[x2,y2] = line
    for i in range(0, int(steps)):
        pq = Vector(((((x + (u * (i/steps))) - (h + (u * (i/steps)))) * cos(radians(radian * (i/steps)))) - ((y + (v * (i/steps))) - (k + (v * (i/steps)))) * sin(radians(radian * (i/steps)))),
                    ((((x + (u * (i/steps))) - (h + (u * (i/steps)))) * sin(radians(radian * (i/steps)))) + ((y + (v * (i/steps))) - (k + (v * (i/steps)))) * cos(radians(radian * (i/steps)))))
        pq = Vector(pq) + Vector(h + (u * (i/steps)), k + (v * (i/steps)))
        p,q = pq[0], pq[1]
        if ( (((y1-y2) * (p-x1)) + ((x2-x1) * (q-y1))) ) <= 0: #if the new point is now "inside" the line
            m,n = mn
            if mn == pq:
                ab = mn
            else:
                ab = line_intersect([[m,n],[p,q]], line)
            if ab != False:
                a,b = ab
                if point_on_lines(ab, [line]):
                    percent = (sqrt(((a-x) ** 2) + ((b-y) ** 2))) / (sqrt(((gx-x) ** 2) + ((gy-y) ** 2)))
                    if percent not in movements.keys():
                        movements[percent] = {'pt': ab,
                                              'ln': line}
                    elif percent in movements.keys(): #in case there are two points or lines for the same percent of movement
                        movements[percent]['ln'].append(line)
                break
        mn = pq

    first_impact = 1
    for key in movements.keys():
        if key > first_impact or key == 0:
            movements.pop(key)
        else:
            first_impact = key
    if first_impact in movements.keys():
        pt = movements[first_impact]['pt']
        ln = movements[first_impact]['ln']
    else:
        pt = point
        ln = line
    movements = {'%': first_impact,
                 'pt': pt,
                 'ln': ln}
    
    return movements
        
def get_future_pos(actors, scenery):

    get_ghosts(actors)
    collisions = get_collisions(actors, scenery) #collisions{ actors {points: [targets]} }
    impacts = {}
    
    for actor in actors:
        impact = {}
        if actor in collisions.keys(): #for each actor that collided with another widget,  if any of the actor's ghostPoints are inside any target
            collision = collisions[actor] #assign each actor to impact, for convenience
            for num in collision.keys(): #for each point in collision[actor].keys
                impact[num] = {}
                if 'rotPt' in actor.impacts.keys():
                    h,k = actor.impacts['rotPt']
                else:
                    h,k  = actor.cog
                targets = []
                for target in collision[num]:
                    if type(target) != str:
                        friction = target.friction
                        elastic = target.elastic

                        if num < 100:
                            radian = actor.rotSpd * actor.rotDir
                            u,v = actor.velocity
                            ghost = actor.ghostPoints[num] #the point inside the target, after v/r
                            body = actor.pointsDict[num] #the point outside the target, before v/r
                            lines = target.lines
                            
                        else:
                            radian = -(actor.rotSpd * actor.rotDir)
                            u,v = -actor.velocity
                            x,y = body = target.pointsDict[(num - 100)]
                            ghost = Vector(((((x+u) - (h-u)) * cos(radians(radian)))
                                             - (((y+v) - (k-v)) * sin(radians(radian)))),
                                            (((x+u) - (h-u)) * sin(radians(radian)))
                                            + (((y+v) - (k-v)) * cos(radians(radian))))
                            ghost = ghost + Vector(h-u, k-v)
                            lines = actor.lines
                            
                        movePercent = None
                        if check_inside([body], lines) == False: #if the point isn't already inside the lines
                            targetLine = check_border(body, ghost, lines) # = [[line1],[line2]]
                            #if type(actor) == Fruit:
                                #print('get future position, targetLine = '+str(targetLine))
                            if targetLine != []:
                                movePercent = find_percent_move(body, [h,k], [u,v], radian, targetLine) # = {'%' %, 'pt': [a,b], 'ln': [[lineA],[lineB]] }#TSUZUKU
                                movePercent['f']  = friction
                                movePercent['e']  = elastic
                            else:
                                #if num in actor.impacts.keys():
                                #    movePercent = {'%': -1,  'pt': body, 'ln': actor.impacts[num][target]['ln'], 'f': friction, 'e': []}
                                #elif num - 100 in actor.impacts.keys():
                                #else:
                                movePercent = {'%': -1,  'pt': body, 'ln': [], 'f': friction, 'e': []}
                        else:
                            if num in actor.impacts.keys():
                                if target in actor.impacts[num].keys():
                                    if 'ln' in actor.impacts[num][target].keys():
                                        movePercent = {'%': -1,  'pt': body, 'ln': actor.impacts[num][target]['ln'], 'f': friction, 'e': []}#FIX the line & point, keep eye on % = 1
                        if movePercent != None:
                            impact[num][target] = movePercent

            first_impact = 1
            impacts[actor] = {}
            for num in impact.keys(): #for each point that impact something given a full movement
                for target in impact[num].keys(): #for each target with which the point may interact given a full movement
                    if impact[num][target]['%'] < first_impact and impact[num][target]['%'] > 0:
                        first_impact = impact[num][target]['%']
                for target in impact[num].keys():
                    if impact[num][target]['%'] == first_impact:# or impact[num][target]['%'] < first_impact:
                        if num in impacts[actor].keys():
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f':  impact[num][target]['f'],
                                                           'e':  impact[num][target]['e']}
                        else:
                            impacts[actor]['%'] = first_impact
                            impacts[actor][num] = {}
                            impacts[actor][num]['pt'] = impact[num][target]['pt']
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f':  impact[num][target]['f'],
                                                           'e':  impact[num][target]['e']}
                            impacts[actor]['%'] = impact[num][target]['%']
                        
                    if impact[num][target]['%'] == -1:
                        if num in impacts[actor].keys():
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f':  impact[num][target]['f'],
                                                           'e':  impact[num][target]['e']}
                        else:
                            impacts[actor]['%'] = first_impact
                            impacts[actor][num] = {}
                            impacts[actor][num]['pt'] = impact[num][target]['pt']
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f': impact[num][target]['f'],
                                                           'e': impact[num][target]['e']}
            if '%' not in impacts[actor].keys():
                impacts[actor]['%'] = 0
                            
        if actor not in collisions.keys():
            impacts[actor] = {}
            if 'rotPt' in actor.impacts.keys():
                impacts[actor]['rotPt'] = actor.impacts['rotPt']
            impacts[actor]['%'] = 1
            if 'ln' in actor.impacts.keys():
                impacts[actor]['ln'] = actor.impacts['ln']
    #for actor in impacts.keys():
        #if type(actor) == Fruit:
            #print('impact @ '+str(actor)+':'+str(impacts[actor]))
    return impacts


def move_actors(impacts):
    for actor in impacts.keys():
        
        if 'rotPt' in actor.impacts.keys():
            rotPt = actor.impacts['rotPt']
        else:
            rotPt = actor.cog
        #if type(actor) == Fruit:
            #print(impacts[actor]['%'])
            #print(actor.velocity, Vector(actor.velocity) * impacts[actor]['%'])
        #print('pre impact multiply: '+str(actor.velocity))
        #actor.velocity = Vector(actor.velocity) + Vector((0.1 * impacts[actor]['%']), (0.1 * impacts[actor]['%']))
        #print('post impact multiply: '+str(actor.velocity))
        #if type(actor) == Fruit:
            #print(actor.velocity)   
        actor.pos = Vector(actor.pos) + Vector((actor.velocity[0] * impacts[actor]['%']), actor.velocity[1] * impacts[actor]['%'])
        r = Matrix().rotate(-actor.rotDir * radians(-(actor.rotSpd * impacts[actor]['%'])), 0, 0, 1)
        actor.apply_transform(r, post_multiply = True, anchor = actor.to_local(*((Vector(rotPt) + Vector(actor.velocity))) ) )

        actor.pointsDict = get_widget_bounds(actor)
        bounceList = []
        actor.impacts = {}
        #if type(actor) == Fruit:
            #print('move impacts: '+str(impacts[actor]))
            #print('0  '+str(actor.pointsDict[0])+
            #      '\n2  '+str(actor.pointsDict[1])+
            #      '\n3  '+str(actor.pointsDict[3]))
        for num in impacts[actor].keys():
            if type(num) != str:
                actor.impacts[num]= {}
                for target in impacts[actor][num].keys():
                    if type(target) != str:
                        #print('target: '+str(num)+' '+str(target.pos))
                        actor.impacts[num]['pt'] = impacts[actor][num]['pt']
                        actor.impacts[num][target] = {}
                        actor.impacts[num][target] = {'ln': impacts[actor][num][target]['ln'],
                                                      'f': impacts[actor][num][target]['f'],
                                                      'e': impacts[actor][num][target]['e']}
                        if actor.impacts[num][target]['e'] != []:
                            bounceList.append([num, target])
        
        if 'rotPt' in impacts[actor].keys():
            actor.impacts['rotPt'] = impacts[actor]['rotPt']

        #determine bounce
        if bounceList != []:
            bounce(actor, bounceList) #bounce will also pop any targets and nums that are empty, if all nums are empty, pop 'rotPt'
        if '%' in actor.impacts.keys():
            actor.impacts.pop('%')
        if actor.impacts.keys() == ['rotPt']:
            actor.impacts.pop('rotPt')

def remove_vector(point, cog):
    x,y = point
    p,q = cog

    n = Vector((q-y), -abs(p-x)).normalize()

    return n

class BlackBoard(Scatter):
    '''
    basic background for playing Levels

    this should handle all collisions and inputs for it's children, migrate
    alot if not all of the information that is passed upstream from the Actors
    to here.

    I.e. Handle ALL touch inputs here. If a touch input needs to be processed at
    the level of any children, instead of creating a touch function in the child
    at super() referencing the normal touch, handle the extra touch functions here.
    Cycle through all children and listen for specific events based on type(child) ==
    type(XXXX)
    '''

    def __init__(self):
        Scatter.__init__(self)

        # load basic Scatter attribtues
        self.pos = (0, 0)
        self.scale = 1
        self.do_collide_after_children = True
        self.do_scale = False
        self.do_rotation = False
        self.do_translation = True

        self.capture = []
        self.touch_timer = 0.0
        self.set_up = True

        self.grabbed = None

    def add_actor(self, key, value):
        #print(value)
        if 'Flan' in key:
            actor = Flan(value)#flav = value['flav'], pos = )
            self.flans.append(actor)
        elif 'Fruit' in key:
            actor = Fruit(value)
            self.fruits.append(actor)
        elif 'Floor' in key:
            actor = Floor(value) #pos = value['pos'], rot = value['rotation'], size = value['size'], mat = value['mat'])
            self.floors.append(actor)
        elif 'Obsti' in key:
            actor = Obsticles()
            self.obsticles.append(actor)
        self.add_widget(actor)
        
    def load_level(self, level, filename = 'ame_levels'):
        '''
        Parses out the loaded level file and creates level Scatter attributes for the level

        Accepts:
            BlackBoard, int(level), and the filename w/out file ending
        Loads:
            background image texture
        Assigns:
            class attributes for the level
        '''
        
        # load level variables
        lvl = read_level(filename, level)
        self.pEnergy = lvl['variables']['pEnergy'] #default of -1
        self.gravity = lvl['variables']['gravity'] #default of -0.1
        self.push = lvl['variables']['push'] #default 0

        # load level background
        lvlImage = Image()
        lvlImage.texture = Sheet(os.path.join('Images',lvl['variables']['image'])).texture
        lvlImage.size = lvlImage.texture.size
        self.add_widget(lvlImage)
        self.size = lvlImage.size
        self.size_hint = (None, None)

        self.lstFlan = lvl['flanList']
        self.lstFruit = lvl['fruitList']
        self.lstFloor = lvl['floorList']
        self.lstObsticles = lvl['obsticles']

        # widget tracking lists
        self.flans, self.fruits, self.floors, self.plates, self.start, self.finish, self.obsticles = [], [], [], [], [], [], []
        for key, value in self.lstFloor.items():
            self.add_actor(key, value)
            
        for key, value in self.lstObsticles.items():
            self.add_actor(key, value)
        
        for key, value in self.lstFlan.items():                
            self.add_actor(key, value)

        for widget in (self.flans + self.floors + self.plates + self.start + self.finish + self.obsticles):
            widget.pointsDict = get_widget_bounds(widget)

        self.actors = []#[self.flans + self.fruits + self.obsticles] #only things that should be moving, bc. moving floors are obsticles
        for actor in self.flans + self.fruits + self.obsticles:
            if actor != self.grabbed:
                self.actors.append(actor)
                #print(self.actors)
               
        self.scenery = []
        for scene in self.floors:
            self.scenery.append(scene)
            
        Clock.schedule_interval(self.actor_roll_call, 1/2)

    def actor_roll_call(self, dt):
        '''
        This method determines if an actor should move, whether it collides, or rotates
        through another widget, and then moves each actor according to its velocity as
        metered by whether or not it collides
        It then calls gravity() to update velocity metrics for each actor that is falling

        Scheduled by Clock.schedule()
        Parameters:
            self
        Calls:
            *gravity() # to modify widget.velocity attributes
            get_future_pos() determines if the next move will result in a collision
            move_actors() moves the actors to ghost positions
        Loads:
        Assigns:
        Returns:
        '''
        gravity(self.actors, [self.push, self.gravity]) # if any Actor() is falling or sliding, modifies their velocity and vDelt
        impacts = get_future_pos(self.actors,self.scenery)    # compiles a dictionary of the future percents of velocity/rotation for every actor that changes position, accounts for stunted movement due to collisions
        move_actors(impacts)
        
    def count_time(self, dt):       #should probably be moved out of BlackBoard and placed in a common area, 
        self.prev_time = self.touch_timer
        self.touch_timer += Clock.frametime
        if self.grabbed.collide_point(*self.held):
            if self.prev_time < 11 and self.touch_timer >= 11:
                print('11') #do poke 2
                pass
            elif self.prev_time < 5 and self.touch_timer >= 5:
                print('5') #do poke 1
                pass
            elif self.prev_time < 0.1 and self.touch_timer >= 0.1:
                print('0.4')
                if self.set_up == True:
                    self.grabbed.do_translation = True
                    if self.grabbed in self.actors:
                        self.actors.remove(self.grabbed)
                    
    def bounce_back(self, dt):
        if self.x > -30:
            self.x -= 1
        if self.y > -30:
            self.y -= 1
        if self.right < self.size[0] + 30:
            self.x += 1
        if self.top < self.size[1] + 30:
            self.y += 1

        if self.x < -30 and self.y < -30 and self.right > self.size[0] + 30 and self.top > self.size[0] + 30:
            Clock.unschedule(self.bounce_back)

    def on_touch_down(self, touch):
        
        self.held = touch.pos
        for child in self.children:
            if child in self.flans:
                if child.collide_point(*touch.pos):
                    self.grabbed = child
                    self.grab_pos = child.pos
                    Clock.schedule_interval(self.count_time, 1/60)

        if touch.is_double_tap == True:
            print('DOUBLE!!!')
            #if self.fruits != []:
            #    for fruit in self.fruits:
            #        self.remove_widget(fruit)
            #        self.actors.remove(fruit)
            if self.fruits == []:
                self.add_actor('Fruit',{'flav':'blb'})
            for fruit in self.fruits:
                fruit.center = touch.pos
                #print('on touch down: '+str(fruit.center))
                self.actors.append(fruit)
                fruit.pointsDict = get_widget_bounds(fruit)
                #print('post bounds 0: ',fruit.pointsDict[0])'''
            
        return super(BlackBoard, self).on_touch_down(touch)
        
    def on_touch_move(self, touch):
        self.held = (touch.pos)
        if self.grabbed != None:
            if 'move' in self.grabbed.abilities:
                #houkou = math.copysign(1, (touch.x - self.grabbed.x))
                #movement(self.grabbed,
                #print('move')
                pass
            if self.grabbed.collide_point(*touch.pos) == False:
                self.swipe = self.grabbed.center

            self.grabbed.velocity = Vector(0,0)
            self.grabbed.pointsDict = get_widget_bounds(self.grabbed)
            self.grabbed.ghostPoints = self.grabbed.pointsDict
            collisions = get_collisions(self.actors + [self.grabbed], self.scenery)
            #print (collisions)
            if self.grabbed in collisions.keys():
                self.grabbed.pos = self.grab_pos
            self.grab_pos = self.grabbed.pos
                
        if self.right < self.size[0]:
            self.right = self.size[0]
        elif self.x > 0:
            self.x = 0
        if self.top < self.size[1]:
            self.top = self.size[1]
        elif self.y > 0:
            self.y = 0

        return super(BlackBoard, self).on_touch_move(touch)
                
    def on_touch_up(self, touch):
        if self.grabbed != None:
            for target in self.actors + self.scenery:
                if target != self.grabbed:
                    for point in self.grabbed.pointsDict.values():
                        if check_inside([point], target.ghostLines) == True:
                            pass
            if 'swipe' in self.grabbed.abilities and self.grabbed.collide_point(*touch.pos) == False:
                # do swipe abilitiy, pass flan and the touch.pos
                print('swipe')
                pass
            if 'hold' in self.grabbed.abilities:
                #if it has been held long enough
                if self.grabbed.abilities['hold'] > 1:  #hold length
                    # do hold ability
                    print('hold')
                    pass
            if self.set_up == True:
                self.grabbed.do_translation = False
                
            self.grabbed.pointsDict = get_widget_bounds(self.grabbed)
            self.grabbed.ghostPoints = self.grabbed.pointsDict
            collisions = get_collisions(self.actors + [self.grabbed], self.scenery)
            if self.grabbed in collisions.keys():
                point = collisions[self.grabbed].keys()
                if point[0] > 100:
                    target = collisions[self.grabbed][point[0]][0]
                    point = point[0] - 100
                else:
                    target = self.grabbed
                    point = point[0]
                n = Vector(-(2*touch.dx), -(2*touch.dy))
                self.grabbed.pos = Vector(self.grabbed.pos) + Vector(n)
                
            self.grab_pos = self.grabbed.pos
            self.actors.append(self.grabbed)
            
        self.grabbed = None
        self.held = None
        self.touch_timer = 0.0
        Clock.unschedule(self.count_time)

        if self.right <= self.size[0] + 30 or self.x >= -30 or self.top <= self.size[1] + 30 or self.y >= -30:
            Clock.schedule_interval(self.bounce_back, 1/60)

        return super(BlackBoard, self).on_touch_up(touch)
