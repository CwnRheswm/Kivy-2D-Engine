# -*- coding: utf-8 -*-
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
    widget.cog = cog

    return pointsDict
    
def check_stability(actor, gravity)#(points, impactPt, impactLn, stability, fall):
    rotDir = 0
    velocity = Vector(0,0)

    impacts = actor.impacts
    push, fall = gravity
    
    #find maximum and minimum x coords of impacted points
    min_x = str()
    max_x = None
    for num in impacts.keys():
        if num != 'rotPt':
            if impacts[num]['pt'][0] < min_x:
                min_x = impacts[num]['pt'][0]
                left = num
            if impacts[num]['pt'][0] > max_x:
                max_x = impacts[num]['pt'][0]
                right = num
    '''
    for point in points.values():
        #print('point coord: '+str(point))
        if point[0] > max_x:
            max_x = point[0]
            #print('max_x: ',max_x)
        elif point[0] < min_x:
            min_x = point[0]
            #print('min_x: ',min_x)
    '''
    #check point or points to see if it should rotate in a particular direction and on a particular point
    #should work on one point or two or three or more
    if cog[0] > max_x:
        rotDir = -1
        actor.impacts['rotPt'] = impacts[right]['pt']
        if left != right:
            impacts.pop(left)
    elif cog[0] < min_x:
        rotDir = 1
        actor.impacts['rotPt'] = impacts[left]['pt']
        if right != left:
            impacts.pop(right)
    '''
    center = (min_x + max_x) / 2
    
    if center < min(Vector(impactPt))[0]: #min([impactPt])[0]:
        rotDir = 1
        #impactPt = min(impactPt)
        impactPt = [min(Vector(impactPt))]
    elif center > max(Vector(impactPt))[0]:
        rotDir = -1
        #impactPt = max(impactPt)
        impactPt = [max(Vector(impactPt))]
    '''
    line = None
    targets = []
    for num in impacts.keys():
        for target in impacts[num]:
            targets.append(target)
            #line.append(impacts[num][target]['ln'])
    #if all(x == line[0] for x in line):
    #    line = line[0]
    if all(x == targets[0] for x in targets): #if all targets are the same, i.e. only one target
        for num in impacts.keys():
            if type(num) == int:
                if impacts[num][targets[0]]['ln'] in targets[0].lines:
                    line = impacts[num][targets[0]]['ln']
    else:
        #find a differnce between a case where an Actor is resting on two different lines
        #1. the Actor is sloped towards a line it is against, thus it should remain
        #2. the Actor is sloped away from a line it is against, thus it should slide
        #Look at the lower of the set of points, if it is...
        min_y = str()
        #leaning = False
        for num in impacts.keys():
            if type(num) == int:
                if impacts[num]['pt'] < min_y:
                    min_y = impacts[num]['pt']
                    bottom = num
                    
                #if point_on_line([impact[num]['pt']], line):
                 #   leaning = line
        for target in targets:
            if target in impacts[bottom].keys():
                if impacts[bottom][target]['ln'] in actor.lines:
                    line = impacts[bottom][target]['ln']

    if line != None and len(line) == 1:
        dX = line[0][0] - line[1][0]
        dY = line[1][0] - line[1][1]
        if dX == 0:
            slope = 0
        else:
            slope = dY / dX

        if abs(slope) > math.tan(math.radians(actor.stability[0])):
            actor.velocity = Vector(actor.velocity) + Vector((fall+(-push)) * slope, (fall+(-push)))
        else:
            actor.velocity = Vector(0,0)

        if abs(slope) > math.tan(math.radians(actor.stability[1])):
            actor.rotDir = -(math.copysign(1, slope))

            bottom = str()
            for num in impacts.keys():
                if impacts[num]['pt'] < bottom:
                    bottom = impacts[num]['pt']
            actor.impacts['rotPt'] = impacts[bottom]['pt']
        '''
        if leaning == True:
            if bottom < 100:
                #point is on another line, thus it is not against a target
                print('POTENTIALLY UNSTABLE')
                
            else:
                #point is on the Actor, and it is resting against a target
                #STABLE
        
    
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
        '''
    
    return velocity, impactPt, rotDir 

def bounce(actor, bounceList):
    bounceThreshold = 0.01 * 30
    rotDir = 0

    velocities = []
    for i in bounceList:
        num, target = bounceList[i]
        
        friction = actor.impacts[num][target]['f']
        elastic = actor.impacts[num][target]['e']
        bounce = actor.bounce
        v = actor.velocity

        [x,y],[p,q] = actor.impacts[num][target]['ln']
    
        n = Vector((q-y), -abs(p-x)).normalize()

        u = (v.dot(n) / n.dot(n)) * n
        w = v - u

        new_v = (friction * w) - ([elastic * bounce * u[0], elastic * bounce * u[1]])
        velocities.append(new_v)
    '''
    if len(velocityList) == 1:
        if new_v[1] < bounceThreshold:
            actor.velocity = Vector(0,0)
        else:
            actor.velocity = velocityList[0]
            actor.impacts.pop(num) #remove 'pt', 'ln', 'f' & 'e' from that num
            if velocityList[0][0] < 0:
                rotDir = 1
            elif velocityList[0][0] > 0:
                rotDir = -1

    else: #get average velocity
    '''
    x = 0
    y = 0
    for i in range(len(velocities)):
        x += velocities[i][0]
        y += velocities[i][1]
        
    x = x / len(velocities)
    y = y / len(velocities)

    velocity = Vector(x,y)

    if velocity[1] < bounceThreshold:
        actor.velocity = Vector(0,0)
        for i in bounceList:
            num, target = bounceList[i]
            actor.impacts[num][target]['e'] = []
    else:
        actor.velocity = velocity
        for i in bounceList: #CONTINUE
            num, target = bounceList[i]
            actor.impacts[num].pop(target)
            if actor.impacts[num].keys() == []:
                actor.impacts.pop(num)
            
        if velocity[0] < 0:
            actor.rotDir = 1
        elif velocity[0] > 0:
            actor.rotDir = -1
        
    return #new_v, rotPt, impactLn, rotDir, [friction, None]
    
def gravity(actors, gravity):
    '''
    '''
    terminalV = 3.3
    terminalH = 1
    push = gravity[0]
    fall = gravity[1]
    
    for actor in actors:
        #CONTINUE FROM HERE
        #print('GRAVITY CHECK: Velocity: '+str(actor.velocity)+' Impacts: '+str(actor.impactPt)+', '+str(actor.impactLn)+', '+str(actor.impact)+' coG: '+str(actor.cog))
        if actor.impacts.keys() != []:
            velocity, imp
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
        #if actor.impactPt != [[]]:
        if 'rotPt' in actor.impacts.keys():
            h,k = actor.impacts['rotPt']
        else:
            h,k = actor.cog
        
        ghostPoints = {}
        for point in actor.pointsDict.keys():
            x,y = actor.pointsDict[point]
            new_point = Vector(((((x + u) - (h + u)) * math.cos(math.radians(rad * direction))) - (((y + v) - (k + v)) * math.sin(math.radians(rad * direction)))),
                               ((((x + u) - (h + u)) * math.sin(math.radians(rad * direction))) + (((y + v) - (k + v)) * math.cos(math.radians(rad * direction)))))
            new_point = Vector(new_point) + Vector(h + u, k + v)
            ghostPoints[point] = new_point
            
        actor.ghostPoints = ghostPoints

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
        lines = []
        for i in piece.ghostPoints.keys():
            if i == len(piece.ghostPoints.keys()) - 1:
                j = 0
            else:
                j = i+1

            lines.append([ghostPoints[i], ghostPoints[j]])
        piece.lines = lines
        #lines = list of each point pair to define the lines of each widget, in order to test against it
            
    #run each Actor against the lines list
    for actor in actors:
        for target in actors + scenery:
            if actor != target: #check to make sure you aren't running the target against itself
                
                for point in actor.ghostPoints.keys():  #run each point in the actor against each target's lines
                    if check_inside([actor.ghostPoints[point]], target.lines):
                        #if pre_collided(actor, point, target) == False: #if the target collided with it last timestep, ignore it, おもいだして： negate velocity for objects that should stand still
                        if actor in collisions.keys():
                            if point in collisions[actor].keys():
                                collisions[actor][point].append(target)
                            else:
                                collisions[actor][point] = [target]
                        else:
                            collisions[actor] = {}
                            collisions[actor][point] = [target]
                
                for point in target.ghostPoints.keys(): #run each point in the target against the actors lines
                    if check_inside([target.ghostPoints[point]], actor.lines):
                        #if pre_collided(actor, point, target) == False:
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
        if abs(crossproduct) > 10: #0.001:
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
    line1 = [body,ghost]
    for line2 in target.lines:
        cross = line_intersect(line1, line2)
        if cross != False:
            if point_on_lines(cross, [line1,line2]):
                lines.append(line2)
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
            if ( (((y1-y2) * (p-x1)) + ((x2-x1) * (q-y1))) ) <= 0: #if the new point is now "inside" the line
                m,n = mn
                ab = line_intersect([[m,n],[p,q]], line)
                if ab != False:
                    a,b = ab
                    if point_on_lines(ab, [line]):
                        percent = (math.sqrt(((a-m) ** 2) + ((b-n) ** 2))) / (math.sqrt(((p-m) ** 2) + ((q-n) ** 2)))
                        percentMovement = ((i - 1) + percent) /steps
                        if percentMovment not in movements.keys():
                            movements[percentMovement] = {'pt': [ab]
                                                          'ln': [line]}
                        elif percentMovement in movements.keys(): #in case there are two points or lines for the same percent of movement
                            #movements[percentMovement]['pt'].append(ab)
                            movements[percentMovement]['ln'].append(line)
                    break
            mn = pq

    first_impact = 1
    for key in movements.keys():
        if key > first_impact:
            movements.pop(key)
        else:
            first_impact = key
        #should leave a movements dictionary with only the lowest percentMovement dict, which has any lines this point would impact at that percent of movement
        #movements = {%: {'pt': [ab], 'ln': [[A],[B]]} }
    pt = movements[first_impact]['pt']
    ln = movements[first_impact]['ln']
    movements = {'%': first_impact,
                 'pt': pt,
                 'ln': ln}
    
    return movements
        
def get_future_pos(actors, scenery):

    get_ghosts(actors)
    collisions = get_collisions(actors, scenery) #collisions{ actors {points: [targets]} }
    impacts = {}
    print('1 collide: ',collisions)
    for actor in actors:
        if actor in collisions.keys(): #for each actor that collided with another widget,  if any of the actor's ghostPoints are inside any target
            impact = collisions[actor] #assign each actor to impact, for convenience
            
            #find the percent of movement in order to reach a collision
            for num in impact.keys(): #for each point in collision[actor].keys
                impact[num] = {}
                u,v = actor.velocity
                if 'rotPt' in actor.impacts.keys():
                    h,k = actor.impacts['rotPt']
                else:
                    h,k  = actor.cog
                '''
                if piece.impacts[num]['pt'] == [[]]:
                    h,k = actor.cog[0]
                else:
                    h,k = actor.impacts[num]['pt'] #actor.impactPt[0] #FIX impactPt
                '''
                for target in impact[num].values:
                    friction = target.friction
                    elastic = target.elastic

                    if num < 100:
                        ghost = actor.ghostPoints[num] #the point inside the target, after v/r
                        body = actor.pointsDict[num] #the point outside the target, before v/r
                        lines = target.lines
                    else:
                        radian = -(actor.rotSpd * actor.rotDir)
                        
                        x,y = body = target.pointsDict[(num - 100)]
                        ghost = Vector(((((x+u) - (h+u)) * math.cos(math.radians(radian)))
                                         - (((y+v) - (k+v)) * math.sin(math.radians(radian)))),
                                        (((x+u) - (h+u)) * math.sin(math.radians(radian)))
                                        + (((y+v) - (k+v)) * math.cos(math.radians(radian))))
                        ghost = ghost + (h+u, y+v)
                        lines = actor.lines

                    if check_inside([body], lines) == False: #if the point isn't already inside the lines
                        #impact[num] = target
                        targetLine = check_border(body, ghost, target) # = [[line1],[line2]]
                        movePercent = find_percent_move(body, [h,k], [u,v], radian, targetLine) # = {'%' %, 'pt': [a,b], 'ln': [[lineA],[lineB]] }#TSUZUKU
                        #for key in targetPerc.keys():
                        movePercent['f'] = friction
                        movePercent['e'] = elastic
                    else:
                        print('else movePercent, a.k.a. Should Never Happen')
                        movePercent = {'%': -1,  'pt': [body], 'ln': actor.impacts[num][target]['ln'], 'f': friction, 'e': []}#FIX the line & point, keep eye on % = 1

                    impact[num][target] = movePercent

            #impact = {num: {target: {movePercent} } } 
            first_impact = 1
            impacts[actor] = {}
            for num in impact.keys(): #for each point that impact something given a full movement
                for target in impact[num].keys(): #for each target with which the point may interact given a full movement
                    if impact[num][target]['%'] < first_impact and impact[num][target]['%'] > 0:
                        first_impact = impact[num][target]['%']
                for target in impact[num].keys():
                    if impact[num][target]['%'] == first_impact:
                        if num in impact[actor].keys():
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f':  impact[num][target]['f'],
                                                           'e':  impact[num][target]['e']}
                            #impacts[actor][num]['target'].append(target)
                            #impacts[actor][num]['ln'].append(impact[num][target]['ln'])
                            #impacts[actor][num]['f'].append(impact[num][target]['f'])
                            #impacts[actor][num]['e'].append(impact[num][target]['e'])
                        else:
                            impacts[actor][num] = {}
                            impacts[actor][num]['pt'] = impact[num][target]['pt']
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f':  impact[num][target]['f'],
                                                           'e':  impact[num][target]['e']}
                            #impacts[actor][num] = {'target':[target], #'%':  impact[num][target]['%'],
                            #                       'pt': impact[num][target]['pt'],
                            #                       'ln': [impact[num][target]['ln']],
                            #                       'f':  [impact[num][target]['f']],
                            #                       'e':  [impact[num][target]['e']]}
                            impacts[actor]['%'] = impact[num][target]['%']
                        
                    elif impact[num][target]['%'] == -1:
                        if num in impact[actor].keys():
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f':  impact[num][target]['f'],
                                                           'e':  impact[num][target]['e']}
                            #impacts[actor][num]['target'].append(target)
                            #impacts[actor][num]['ln'].append(impact[num][target]['ln'])
                            #impacts[actor][num]['f'].append(impact[num][target]['f'])
                            #impacts[actor][num]['e'].append(impact[num][target]['e'])
                        else:
                            impacts[actor][num] = {}
                            impacts[actor][num]['pt'] = impact[num][target]['pt']
                            impacts[actor][num][target] = {'ln': impact[num][target]['ln'],
                                                           'f': impact[num][target]['f'],
                                                           'e': impact[num][target]['e']}
                            #impacts[actor][num] = {'target':[target], #'%':  impact[num][target]['%'],
                            #                       'pt': impact[num][target]['pt'],
                            #                       'ln': [impact[num][target]['ln']],
                            #                       'f':  [impact[num][target]['f']],
                            #                       'e':  [impact[num][target]['e']]}
        
        if actor not in collisions.keys():
            impacts[actor] = {}
            if 'rotPt' in actor.impacts.keys():
                impacts[actor]['rotPt'] = actor.impacts['rotPt']
            impacts[actor]['%'] = 1
            
    #at this point I should have a dictionary with a key for EVERY actor and an associated value
    #of how much of the projected movement the actor can take before it's initial collision,
    #between 0, no movement, and 1, full movement
    #print('impacts: ', impacts)
    return impacts
        

def move_actors(impacts):
    for actor in impacts.keys():
        if 'rotPt' in actor.impacts.keys():   #actor.impactPt != [[]]:
            rotPt = actor.impacts['rotPt']
        else:
            rotPt = actor.cog
        actor.velocity = Vector(actor.velocity) * impacts[actor]['%']
        actor.pos = Vector(actor.pos) + (actor.velocity)
        r = Matrix().rotate(actor.rotDir * math.radians(-(actor.rotSpd * impacts[actor]['%'])), 0, 0, 1)
        #print(r)
        actor.apply_transform(r, post_multiply = True, anchor = actor.to_local(*((Vector(rotPt) + Vector(actor.velocity))) ) )

        actor.pointsDict = get_widget_bounds(actor)
        #if actor.impactLn != [[]]:
        #if actor.impactPt == []:
        #    actor.impactPt = []#[impacts[actor][0]]
        #else:
        #print(impacts)
        #print(actor.impactPt, impacts[actor][0][0], impacts[actor][0][0] in actor.impactPt)
        bounceList = []
        actor.impacts = {}
        for num in actor.pointsDict.keys():
            if num in impacts[actor].keys():
                if num in actor.impacts.keys():
                    actor.impacts[num][impacts[actor][num]['target']] = {'ln': impacts[actor][num]['ln'],
                                                                         'f': impacts[actor][num]['f'],
                                                                         'e': impacts[actor][num]['e']}
                    #actor.impacts[num]['target'].append(impacts[actor]['target'])
                    #actor.impacts[num]['pt'] = impacts[actor]['pt']
                    #actor.impacts[num]['ln'].append(impacts[actor]['ln'])
                    #actor.impacts[num]['f'].append(impacts[actor]['f'])
                    #actor.impacts[num]['e'].append(impacts[actor]['e'])
                else:
                    actor.impacts[num] = {impacts[actor][num]['target']: {'ln': impacts[actor][num]['ln'],
                                                                          'f': impacts[actor][num]['f'],
                                                                          'e': impacts[actor][num]['e']}}
                    actor.impacts[num]['pt'] = impacts[actor][num]
                    #actor.impacts[num] = impacts[actor][num]
            for target in range(len(actor.impacts[num].keys())):
                if actor.impacts[num][target]['e'] != []:
                    bounceList.append([num, target])
        
        if 'rotPt' in impacts[actor].keys():
            actor.impacts['rotPt'] = impacts[actor]['rotPt']

        '''
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
        '''

        #determine bounce
        if bounceList != []:
            bounce(actor, bounceList) #bounce will also pop any targets and nums that are empty, if all nums are empty, pop 'rotPt'
        actor.impacts.pop('%')
        if actor.impacts.keys() == ['rotPt']:
            actor.impacts.pop('rotPt')
        #if actor.impact[1] != None:
        #    actor.velocity, actor.impactPt, actor.impactLn, actor.rotDir, actor.impact = bounce(actor)
        
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
        impacts = get_future_pos(actors,scenery)    # compiles a dictionary of the future percents of velocity/rotation for every actor that changes position, accounts for stunted movement due to collisions
        move_actors(impacts)
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
