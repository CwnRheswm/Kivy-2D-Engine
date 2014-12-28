import math, os, random

from kivy.clock import Clock
from kivy.core.image import Image as Sheet
from kivy.graphics import Color, Line, Ellipse
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.vector import Vector

from _actors import Flan, Floor, Fruit
from _open_level_file import read_level, save_level

'''
Changelog:
  Need to:
      change impact to a dictionary that holds impactPt: impactLn, friction, elastic
      when an Actor hits a target populate impact with the impact stats
      if the Actor bounces, remove the impact record relating to the bounce post bounce calculation
      
'''

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
            a = math.cos(math.radians(360 - (p * rads)))
            b = math.sin(math.radians(360 - (p * rads)))

            x, y = ((Vector(center) + (Vector(a,b) * (Vector(widget.size) / 2))))
        pointsDict[p] = [x,y]

    elif 'rect' in widget.shape:
        points = 4
        cut_in = widget.shape['rect'] * widget.scaling
        for p in range(points):
            if p == 0:
                x,y = Vector(widget.x, widget.y)
            elif p == 1:
                x,y = Vector((widget.x + cut_in), widget.top)
            elif p == 2:
                x,y = Vector((widget.right - cut_in), widget.top)
            elif p == 3:
                x,y = Vector(widget.right, widget.y)
            pointsDict[p] = [x,y]

    widget.rotation = rotation
    widget.center = center

    cog = [0,0]
    for point in pointsDict.keys():
        x, y = pointsDict[point]
        
        xPrime = ((x * math.cos(math.radians(rotation))) + (y * -math.sin(math.radians(rotation))))
        yPrime = ((x * math.sin(math.radians(rotation))) + (y * math.cos(math.radians(rotation))))

        xPrime, yPrime = Vector(xPrime, yPrime) + Vector(center)
        
        pointsDict[point] = Vector(xPrime, yPrime)
        cog[0] += xPrime
        cog[1] += yPrime

    cog[0] = cog[0] / (len(pointsDict.keys()))
    cog[1] = cog[1] / (len(pointsDict.keys()))
    
    #if widget.impactPt == widget.cog or widget.impactPt == None:
    #    widget.impactPt = [cog]
    widget.cog = [cog]

    return pointsDict
    
def check_stability(points, impactPt, impactLn, stability, fall):
    rotDir = 0
    velocity = Vector(0,0)
    
    min_x = points[0][0]
    max_x = points[0][0]
    for point in points.values():
        #print('point coord: '+str(point))
        if point[0] > max_x:
            max_x = point[0]
            #print('max_x: ',max_x)
        elif point[0] < min_x:
            min_x = point[0]
            #print('min_x: ',min_x)
    
    center = (min_x + max_x) / 2
    
    if center < min(Vector(impactPt))[0]: #min([impactPt])[0]:
        rotDir = 1
        #impactPt = min(impactPt)
        impactPt = [min(Vector(impactPt))]
    elif center > max(Vector(impactPt))[0]:
        rotDir = -1
        #impactPt = max(impactPt)
        impactPt = [max(Vector(impactPt))]
    print('check stability: ', impactPt, len(impactPt))
    if len(impactPt) == 1:
        #rotating off of one point to the left or right
        if center == impactPt[0]:
            rotDir = random.choice(1,-1)
    	if impactLn != [[]]:
            print('surfSlope: '+str(impactLn))
            line = impactLn

            dX = line[0][0] - line[1][0]
            #dY = line[0][1] - line[1][1]
            if dX == 0:
                surfSlope = 1000000
            else:
                surfSlope = (line[0][1] - line[1][1]) / (line[0][0] - line[1][0])        

            if abs(surfSlope) > math.tan(math.radians(stability[0])):
                #slide on one point
                velocity = Vector(fall * surfSlope, fall)
        print('length 1 velocity: ',velocity)
    
    elif len(impactPt) == 2:
        dX = impactPt[0][0] - impactPt[1][0]
        #dY = impactPt[0][1] - impactPt[1][1]
        
        if dX == 0:
            selfSlope = 0
        else:
            selfSlope = (impactPt[0][1] - impactPt[1][1]) / (impactPt[0][0] - impactPt[1][0])
            
        if abs(selfSlope) > math.tan(math.radians(stability[0])):
            #slide on two points
            velocity = Vector(fall * selfSlope, fall)
        if abs(selfSlope) > math.tan(math.radians(stability[1])):
            #rotate off of a slope
            rotDir = math.copysign(1, selfSlope)
            if impactPt[0][1] < impactPt[1][1]:
                impactPt = [impactPt[0]]
            else:
                impactPt = [impactPt[1]]
        print('length 2 velocity: ',velocity)
    
    return velocity, impactPt, rotDir 

def bounce(actor):
    bounceThreshold = 0.01 * 30
    rotDir = 0

    friction = actor.impact[0]
    elastic = actor.impact[1]
    bounce = actor.bounce
    v = actor.velocity

    if actor.impactLn == []:
        return
    
    [x,y],[p,q] = actor.impactLn
    
    n = Vector((q-y), -abs(p-x)).normalize()

    u = (v.dot(n) / n.dot(n)) * n
    w = v - u

    new_v = (friction * w) - ([elastic * bounce * u[0], elastic * bounce * u[1]])

    if new_v[1] < bounceThreshold:
        new_v = Vector(0,0)
        rotPt = actor.impactPt
        impactLn = actor.impactLn
        #print('new_v: ', impactLn)
        friction = actor.impact[0]
    else:
        impactLn = []
        #print('new_v else: ', impactLn)
        rotPt = [[]]
        friction = None
        if new_v[0] < 0:
            rotDir = 1
        elif new_v[0] > 0:
            rotDir = -1
        
    return new_v, rotPt, impactLn, rotDir, [friction, None]
    
def gravity(actors, gravity):
    '''
    '''
    terminalV = 3.3
    terminalH = 1
    push = gravity[0]
    fall = gravity[1]
    
    for actor in actors:
        #print('GRAVITY CHECK: Velocity: '+str(actor.velocity)+' Impacts: '+str(actor.impactPt)+', '+str(actor.impactLn)+', '+str(actor.impact)+' coG: '+str(actor.cog))
        if actor.impact[1] == None and actor.impactPt != [[]]:#actor.cog:
            velocity, impactPt, rotDir = check_stability(actor.pointsDict, actor.impactPt, actor.impactLn, actor.stability, fall) # should set velocity based on surface slope, either 0,0 if it can remain as is, or velocity defined by slope if it is sliding down the slope

            actor.rotDir = rotDir
            actor.impactPt = impactPt
            actor.velocity = Vector(actor.velocity) + Vector(velocity)
            if actor.velocity[1] > terminalV/2:
                actor.velocity[0] = actor.velocity[0] * ((terminalV/2) / actor.velocity[1])
                actor.velocity[1] = terminalV/2
                
        else:
            actor.velocity = Vector(actor.velocity) + Vector(push, fall)
            if abs(actor.velocity[1]) > terminalV:
                actor.velocity[1] = math.copysign(terminalV, actor.velocity[1])
            if abs(actor.velocity[0]) > terminalH:
                actor.velocity[0] = math.copysign(terminalH, actor.velocity[0])

def get_ghosts(actors):
    for actor in actors:
        u,v = actor.velocity
        rad = actor.rotSpd
        direction = actor.rotDir
        print('get_ghosts: '+str(rad)+' '+str(direction))
        if actor.impactPt != [[]]:
            h,k = actor.impactPt[0]
        else:
            h,k = actor.cog[0]
        
        ghostPoints = {}
        for point in actor.pointsDict.keys():
            x,y = actor.pointsDict[point]
            new_point = Vector(((((x + u) - (h + u)) * math.cos(math.radians(rad * direction))) - (((y + v) - (k + v)) * math.sin(math.radians(rad * direction)))),
                               ((((x + u) - (h + u)) * math.sin(math.radians(rad * direction))) + (((y + v) - (k + v)) * math.cos(math.radians(rad * direction)))))
            new_point = Vector(new_point) + Vector(h + u, k + v)
            ghostPoints[point] = new_point
            
        actor.ghostPoints = ghostPoints

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
    
    for target in actors + scenery:
        try:
            points = target.ghostPoints
        except:
            points = target.pointsDict

        lines = []
        for i in points.keys():
            if i == len(points.keys()) - 1:
                j = 0
            else:
                j = i+1

            lines.append([points[i], points[j]])
        
        for actor in actors:
            if actor != target:
                for point in actor.ghostPoints.keys():
                    if check_inside([actor.ghostPoints[point]], lines):
                        if actor in collisions.keys():
                            collisions[actor][point] = target 
                        else:
                            collisions[actor] = {}
                            collisions[actor][point] = target

        if target in actors:
            for piece in scenery:
                for point in piece.pointsDict.keys():
                    if check_inside([piece.pointsDict[point]], lines):
                        if piece in collisions.keys():
                            collisions[piece][point] = target
                            #collisions[target][point] = piece
                        else:
                            collisions[piece] = {}
                            collisions[piece][point] = target
                
    return collisions

def near(a, b, rtol = math.e + 5, atol = math.e + 8):
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
        if abs(crossproduct) > 10:
            return False

        dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1]) * (b[1] - a[1])
        if dotproduct < 0:
            return False

        squaredLength = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])
        if dotproduct > squaredLength:
            return False
    return True

def check_border(body, ghost, target):
    lines = []
    try:
        points = target.ghostPoints
    except:
        points = target.pointsDict

    line1 = [body,ghost]
    for i in points.keys():
        if i == len(points.keys()) - 1:
            j = 0
        else:
            j = i+1

        line2 = [points[i], points[j]]
        cross = line_intersect(line1, line2)
        if cross != False:
            if point_on_lines(cross, [line1]):
                lines.append(line2)
    #print('border lines: ', lines)
    return lines
            
def find_percent_move(point, pivot, velocity, radian, lines):
    x,y = point
    h,k = pivot
    u,v = velocity
    mn = x,y
    
    movements = {}
    for line in lines:
        steps = 100.0
        [x1,y1],[x2,y2] = line
        for i in range(0, int(steps)):
            pq = Vector(((((x + (u * (i/steps))) - (h + (u * (i/steps)))) * math.cos(math.radians(radian * (i/steps)))) - ((y + (v * (i/steps))) - (k + (v * (i/steps)))) * math.sin(math.radians(radian * (i/steps)))),
                        ((((x + (u * (i/steps))) - (h + (u * (i/steps)))) * math.sin(math.radians(radian * (i/steps)))) + ((y + (v * (i/steps))) - (k + (v * (i/steps)))) * math.cos(math.radians(radian * (i/steps)))))
            pq = Vector(pq) + Vector(h + (u * (i/steps)), k + (v * (i/steps)))
            p,q = pq[0], pq[1]
            #print('check_inside: ', ( (((y1-y2) * (p-x1)) + ((x2-x1) * (q-y1))) ), p,q)
            if ( (((y1-y2) * (p-x1)) + ((x2-x1) * (q-y1))) ) <= 0: #if the new point is now "inside" the line
                m,n = mn
                ab = line_intersect([[m,n],[p,q]], line)
                if ab != False:
                    a,b = ab
                    if point_on_lines(ab, [line]):
                        percent = (math.sqrt(((a-m) ** 2) + ((b-n) ** 2))) / (math.sqrt(((p-m) ** 2) + ((q-n) ** 2)))
                        percentMovement = ((i - 1) + percent) /steps
                        movements[percentMovement] = [[ab],line]
                        #print('break: ', i, percent, percentMovement, ab, line)
                    break
            mn = pq
    
    key_check = []
    for keys in movements.keys():
        key_check.append(keys)
    #print('key_check: ', key_check)
    if all(x == key_check[0] for x in key_check) and len(key_check) != 0:
        minimum = key_check[0]
        #print('mini:',minimum)
        impact = movements[key_check[0]]#,key_check[1]]
    else:
        minimum = min(movements.keys())
        #print('minimum:',minimum)
        impact = movements[minimum]
    #print('unhashable: ',minimum, impact)
    rD = {minimum: impact}
    return rD #{minimum: impact}
        
def get_future_pos(actors, scenery):

    get_ghosts(actors)
    collisions = get_collisions(actors, scenery) #collisions{ actor {point: target} }
    impacts = {}
    targets = []
    print('1 collide: ',collisions)
    for piece in collisions.keys(): #if any of the actor's ghostPoints are inside any target
        ghosts = collisions[piece]
        #we want to modifiy velocity and rotation here to account for collisions
        #find the percent of movement in order to reach a collision
        for num in ghosts.keys():
            if piece in actors:
                #if piece.pointsDict[num] not in piece.impactPt:
                ghost = piece.ghostPoints[num] #the point inside the target, after v/r
                body = piece.pointsDict[num] #the point outside the target, before v/r
                u,v = piece.velocity
                if piece.impactPt == [[]]:
                    h,k = piece.cog[0]
                else:
                    h,k = piece.impactPt[0]
                radian = piece.rotSpd * piece.rotDir
                friction = piece.friction
                elastic = piece.elastic

                lines = []
                if ghosts[num] in actors:
                    points = ghosts[num].ghostPoints
                else:
                    points = ghosts[num].pointsDict
                    
                for i in points.keys():
                    if i == len(points.keys()) - 1:
                        j = 0
                    else:
                        j = i+1
                    lines.append([points[i], points[j]])
                #print('inside check body',check_inside([body], lines))
                if check_inside([body], lines) == False:
                    ghosts[num] = check_border(body, ghost, ghosts[num])
                    #if piece.pointsDict[num] not in piece.impactPt and ghosts[num] not in piece.impactLn:
                    #if ghosts[num] != []:
                    #print('ghost[num] border: ',ghosts[num], piece, num, piece.pointsDict[num], piece.impactPt, ghosts[num], piece.impactLn)
                    ghosts[num] = find_percent_move(body, [h,k], [u,v], radian, ghosts[num])
                    for key in ghosts[num].keys():
                        print('ghost[num][key]: ',ghosts[num][key])
                        ghosts[num][key] = ghosts[num][key] + [friction, elastic]
                else:
                    #ghosts.pop(num)
                    print('piece impactPt: ',piece.impactPt)
                    ghosts[num] = {0: [[h,k], piece.impactLn, friction, elastic]}
                #for actors: collisions{ actor {num1: {%: #}} }
                #            collisions{ actor {num2: {%: #}} }
            
            elif piece in scenery:
                #if piece.pointsDict[num] not in piece[num].impactPt:
                target = ghosts[num]
                x,y = piece.pointsDict[num]
                u,v = ghosts[num].velocity
                if ghosts[num].impactPt == [[]]:
                    h,k = ghosts[num].cog
                else:
                    h,k = ghosts[num].impactPt[0]
                radian = -(ghosts[num].rotSpd * ghosts[num].rotDir)
                ghost = Vector(((((x + u) - (h + u)) * math.cos(math.radians(radian)))
                                - (((y + v) - (k + v)) * math.sin(math.radians(radian)))),
                               (((x + u) - (h + u) * math.sin(math.radians(radian)))
                                + (((y + v) - (k + v)) * math.cos(math.radians(radian)))))
                ghost = ghost + (h + u, y + v)
                body = [x,y]
                
                ghosts[num] = check_border(body, ghost, ghosts[num])
                if piece.pointsDict[num] not in target.impactPt and ghosts[num] not in target.impactLn:
                    ghosts[num] = find_percent_move(body, [h,k], [u,v], radian, ghosts[num])
                    for key in ghosts[num].keys():
                        ghosts[num][key] = ghosts[num][key] + [friction, elastic]
                    new_num = 100 + num
                    collisions[target][new_num] = ghosts[num]
                else:
                    ghost.pop(num)
                #for scenes: collisions{ scene {num1: {%: #}} }
                #            collisions{ scene {num2: {%: #}} }
        #collisions.pop(piece)
    print('2 collide: ',collisions)  #{actor {point {point, line, friction, elastic} } }              
    #collisions is a dictionary that equals the lowest percent of movement to impact another object for each actor
    #impacts is a dictionary that equals the impactPt, impactLn, target.friction, and target.elastic for each actor that impacts another object
    for actor in collisions.keys(): #collisions[actor1/actor2/etc.] = [(num1[%:#],num2[%:#],num101[%:#],num102[%:#])]
        first_impact = 1
        for num in collisions[actor].keys():
            for percent in collisions[actor][num].keys():
                #if percent == 0:
                #    collisions[actor][num].pop(percent)
                if percent < first_impact:
                    
                    first_impact = percent #%
                    impacts[actor] = collisions[actor][num][percent] #[(#,#), [[],[]]]
                    #print('=1 impactPt: '+str(impacts[actor]))
                    #print(impacts[actor][0])
                    #impacts[actor][0].append(['ad'])
                    #print(impacts[actor][0])
                    #print(impacts[actor][0][0])
                elif percent == first_impact:
                    #print(impacts[actor][0], impacts[actor][0][0],collisions[actor][num][percent][0])
                    #print(impacts[actor][0][0], collisions[actor][num][percent][0], collisions[actor][num][percent][0][0], collisions[actor][num][percent][0][0][0])
                    impacts[actor][0].append(collisions[actor][num][percent][0][0])# = [impacts[actor][0][0], collisions[actor][num][percent][0]]
                    #print('>1 impactPt: '+str(impacts[actor]))
        collisions[actor] = first_impact
        #print('first impact: ',collisions[actor])
        
    for actor in actors:
        if actor not in collisions.keys():
            collisions[actor] = 1
            impacts[actor] = [ [[]], [], None, None]
            
    #at this point I should have a dictionary with a key for EVERY actor and an associated value
    #of how much of the projected movement the actor can take before it's initial collision,
    #between 0, no movement, and 1, full movement
    #print('impacts: ', impacts)
    return collisions, impacts
        

def move_actors(movements, impacts):
    for actor in movements.keys():
        if actor.impactPt != [[]]:
            #print('move_check: ',actor.impactPt)
            rotPt = actor.impactPt[0]
        else: #if rotPt == [] or len(rotPt) != 1:
            rotPt = actor.cog[0]
        #print(rotPt, actor.velocity)
        #print(Vector(rotPt) + Vector(actor.velocity))
        actor.velocity = actor.velocity * movements[actor]
        actor.pos = Vector(actor.pos) + (actor.velocity)
        r = Matrix().rotate(actor.rotDir * math.radians(-(actor.rotSpd * movements[actor])), 0, 0, 1)
        #print(r)
        actor.apply_transform(r, post_multiply = True, anchor = actor.to_local(*( (Vector(rotPt) + Vector(actor.velocity)) )))

        actor.pointsDict = get_widget_bounds(actor)
        #if actor.impactLn != [[]]:
        #if actor.impactPt == []:
        #    actor.impactPt = []#[impacts[actor][0]]
        #else:
        #print(impacts)
        #print(actor.impactPt, impacts[actor][0][0], impacts[actor][0][0] in actor.impactPt)
        if actor.impactPt != impacts[actor][0]:
            print('move_actor impactPt: ', actor.impactPt, impacts[actor][0])
            if actor.impactPt == [[]]:
                actor.impactPt = impacts[actor][0]
            elif impacts[actor][0][0] in actor.impactPt:
                 pass   
            else:
                print('pre: ',actor.impactPt,impacts[actor])
                actor.impactPt.append(impacts[actor][0])# = [actor.impactPt[0], impacts[actor][0]]
                print('post: ',actor.impactPt,impacts[actor])
        #print(impacts[actor][0], actor.impactPt)
            

        #if actor.impactLn == []:
        #    actor.impactLn = [impacts[actor][1]] #[actor.impactLn, impacts[actor][1]]
        #else:
        if actor.impactLn != impacts[actor][1]:
            if actor.impactLn == []:
                actor.impactLn = impacts[actor][1]
            elif impacts[actor][1] in actor.impactLn:
                pass
            else:
                actor.impactLn.append(impacts[actor][1])# = [actor.impactLn[0], impacts[actor][1]]
        #print(actor.impactLn)            
            #print('if: ',actor.impactLn)
        actor.impact = [impacts[actor][2], impacts[actor][3]]
            #else:
            #print('impacts: ',impacts[actor][0])
            #actor.impactPt = impacts[actor][0]
            #actor.impactLn = impacts[actor][1]
            #print('else: ',actor.impactLn)
            #actor.impact = [impacts[actor][2], impacts[actor][3]]
        
        if actor.impact[1] != None:
            actor.velocity, actor.impactPt, actor.impactLn, actor.rotDir, actor.impact = bounce(actor)
        
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
        if 'Flan' in key:
            actor = Flan(value)#flav = value['flav'], pos = )
            self.flans.append(actor)
        elif 'Fruit' in key:
            actor = Fruit()
            self.fruits.append(actor)
        elif 'Floor' in key:
            actor = Floor(value)#pos = value['pos'], rot = value['rotation'], size = value['size'], mat = value['mat'])
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
        actors = []#[self.flans + self.fruits + self.obsticles] #only things that should be moving, bc. moving floors are obsticles
        for actor in self.flans + self.fruits + self.obsticles:
            if actor != self.grabbed:
                actors.append(actor)
               
        scenery = []
        for scene in self.floors:
            scenery.append(scene)
        
        gravity(actors, [self.push, self.gravity]) # if any Actor() is falling or sliding, modifies their velocity and vDelt
        movements,impacts = get_future_pos(actors,scenery)    # compiles a dictionary of the future percents of velocity/rotation for every actor that changes position, accounts for stunted movement due to collisions
        print('movements: '+str(movements))
        move_actors(movements,impacts)
        #move_actors(get_future_pos(actors,scenery))

        
    def count_time(self, dt):       #should probably be moved out of BlackBoard and placed in a common area, 
        self.prev_time = self.touch_timer
        self.touch_timer += Clock.frametime
        if self.grabbed.collide_point(*self.held):
            if self.prev_time < 11 and self.touch_timer >= 11:
                #print('11') #do poke 2
                pass
            elif self.prev_time < 5 and self.touch_timer >= 5:
                #print('5') #do poke 1
                pass
            elif self.prev_time < 0.4 and self.touch_timer >= 0.4:
                #print('0.4')
                if self.set_up == True:
                    self.grabbed.do_translation = True
                    self.grabbed.velocity = None
                    self.grabbed.impactLines = []

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
                    Clock.schedule_interval(self.count_time, 1/60)
                    
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
            if 'swipe' in self.grabbed.abilities and self.grabbed.collide_point(*touch.pos) == False:
                # do swipe abilitiy, pass flan and the touch.pos
                #print('swipe')
                pass
            if 'hold' in self.grabbed.abilities:
                #if it has been held long enough
                if self.grabbed.abilities['hold'] > 1:  #hold length
                    # do hold ability
                    #print('hold')
                    pass
            if self.set_up == True:
                self.grabbed.do_translation = False
                #self.grabbed.velocity = Vector(0,0)
                self.grabbed.impactLn = []
                self.grabbed.impactPt = [[]]
        self.grabbed = None
        self.held = None
        self.touch_timer = 0.0
        Clock.unschedule(self.count_time)

        if self.right <= self.size[0] + 30 or self.x >= -30 or self.top <= self.size[1] + 30 or self.y >= -30:
            Clock.schedule_interval(self.bounce_back, 1/60)

        return super(BlackBoard, self).on_touch_up(touch)
