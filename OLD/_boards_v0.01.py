;oimport math, os, random

from kivy.clock import Clock
from kivy.core.image import Image as Sheet
from kivy.graphics import Color, Line, Ellipse
from kivy.graphics.texture import Texture
from kivy.graphics.transformation import Matrix
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.vector import Vector

from _actors import Flan, Floor, Fruit#, Obsticle
from _open_level_file import read_level, save_level

def pos_on_plate(lstWidget, lstPlate):
    firstCenter = lstPlate[0]
    if len(lstWidget) == 1:
        increment = lstPlate[0].width / 2
    elif len(lstWidget) == 2:
        increment = lstPlate[0].width / 4
    else:
        increment = lstPlate[0].width / 6
        increment2 = lstPlate[0].width / 4
        increment3 = lstPlate[0].width / 2

    for i in range(len(lstWidget)):
        width, height = lstWidget[i].right - lstWidget[i].x, lstWidget[i].top - lstWidget[i].y
        if i <= 2:
            lstWidget[i].center = lstPlate[0].center_x + ((i-1) * (width)), lstPlate[0].top + (height/2)
        if i == 3:
            lstWidget[i].center = lstPlate[0].center_x - (width/2), lstPlate[0].top + ((height/2)*3)
        if i == 4:
            lstWidget[i].center = lstPlate[0].center_x + (width/2), lstPlate[0].top + ((height/2)*3)
        if i == 5:
            lstWidget[i].center = lstPlate[0].center_x, lstPlate[0].top + ((height/2)*5)
        #print(i,lstWidget[i].center)
        
    #print(lstWidget[1].y, lstPlate[0].top)
    
def rotate_by_slope(actor, ghost, **kwargs):
   #print('rotate by slope: ', actor.poImp, actor.impactLines)
    selfM, surfM = actor.impactLines
    
    selfSlope = round(ghost.linesDict[selfM.strip('Line') + "M"], 3)
    prevSlope = round(actor.linesDict[selfM.strip('Line') + "M"], 3)

    surfSlope = round(actor.target[0].linesDict[surfM.strip('Line') + "M"], 3)
    #if math.copysign(1, abs(prevSlope) - abs(surfSlope)) != math.copysign(1, abs(selfSlope) - abs(surfSlope)) and prevSlope != surfSlope:
    if 'target' in kwargs.keys():
        print('new target')
        poImp, linesDict = get_intersection(actor, ghost, kwargs['target'])
        if poImp != None:   #if it hits the new target
            actor.poImp = [actor.poImp, poImp]
            #print('target in kwargs.keys()')
            return True
    if near(prevSlope, surfSlope) == True:
        ghost.pos, ghost.rotation = actor.pos, actor.rotation
        print('near',prevSlope, surfSlope)
        return True
    '''if near(selfSlope, surfSlope) == True:
       #print('near(selfSlope, surfSlope)')
        #ghost.pos, ghost.rotation = actor.pos, actor.rotation
        return True'''
    if (prevSlope < surfSlope and selfSlope < surfSlope) or (prevSlope > surfSlope and selfSlope > surfSlope) or prevSlope == 0:# or near(selfSlope,surfSlope) == True or near(prevSlope,surfSlope) == False:
        print('slopes: ')#,prevSlope,selfSlope,surfSlope, actor.rotation, ghost.rotation)
        pass
        #ghost.pos, ghost.rotation = actor.pos, actor.rotation
        #ghost.pointsDict, ghost.linesDict = get_widget_bound(ghost)
        #selfSlope = round(ghost.linesDict[selfM.strip('Line') + "M"], 3)    
    if (prevSlope < surfSlope and selfSlope > surfSlope) or (prevSlope > surfSlope and selfSlope < surfSlope):
        print('ending slope')
        ghost.pos = (Vector(actor.pos) + Vector(ghost.pos)) /2
        ghost.rotation = (actor.rotation + ghost.rotation) /2
        ghost.pointsDict, ghost.linesDict = get_widget_bound(ghost)
        '''selfSlope = round(ghost.linesDict[selfM.strip('Line') + "M"], 3)
        while near(selfSlope, surfSlope) == False:
            #while math.copysign(1, prevSlope - surfSlope) == math.copysign(1, selfSlope - surfSlope) and selfSlope != 1000000:
            #prevSlope = selfSlope
            r = Matrix().rotate(actor.rotDirect * math.radians(-0.01), 0, 0, 1)
            ghost.apply_transform(r, post_multiply = True, anchor = actor.to_local(*actor.poImp))
            ghost.pointsDict, ghost.linesDict = get_widget_bound(ghost)
            selfSlope = round(ghost.linesDict[selfM.strip('Line') + "M"], 3)'''
        ##needs to check for a NEW widget intersection that is NOT the current target
        '''if 'target' in kwargs.keys():
            print('new target')
            poImp, linesDict = get_intersection(actor, ghost, kwargs['target'])
            if poImp != None:   #if it hits the new target
                actor.poImp = [actor.poImp, poImp]
               #print('target in kwargs.keys()')
                return True'''
        #print('(prevSlope < surfSlope and selfSlope > surfSlope) or (prevSlope > surfSlope and selfSlope < surfSlope)')
        return True
    else:
        return
    
def bounce(actor, velocity, target, poImp, impactLines):
    #print('bouncing', velocity)
    friction = target.friction
    elastic = target.elastic
    bounce = actor.bounce
    
    v = velocity
    #print('border: ',impactLines[1])
    for border in target.linesDict.keys():
        if impactLines[1] == border:
            n = target.linesDict[str(border).strip('Line') + 'Norm']
           #print(border, target.linesDict[border], n)
            break
    #print(n, target.linesDict[str(border)])
    q = v.dot((n))
    u = (v.dot(n) / n.dot(n)) * n
    w = v - u
    #print('Q: ' + str(q) + ' U: ' +str(u)+ ' W: ' +str(w))
    velocity = (friction * w) - ([elastic * bounce * u[0], elastic * bounce * u[1]])
    #velocity = (w) - ([u[0], u[1]])
    #print('to bounce', velocity, actor.y, target.top)
    #if (abs(velocity[0]) < 1 and abs(velocity[1]) < 1) or 'finish' in target.alt:
    #print('bounce check: ', velocity)
    if (abs(velocity[1])) < 1:
        velocity = Vector(0,0)
        #vDelt
        #actor.falling = False
        #actor.impactLines = impactLines
        #actor.sloped = True
        actor.target = []
        #print('stop falling: ', velocity)
    else:
        #actor.impactLines = []
        impactLines = []
        #print('up and down: ', actor, actor.impactLines)
        
    #actor.velocity = velocity
    #print('bounce check: ',actor.center_x, poImp)
    #if actor.center_x == poImp[0]:
    #   #print('CENTER')
    if actor.center_x > poImp[0]:
        #print('bounce right')
        rotDirect = 1
    elif actor.center_x < poImp[0]:
        #print('bounce left')
        rotDirect = -1
    else:
        #print('CENTER')
        rotDirect = 0
    #print(velocity)
    #print('bounce return: ', rotDirect, impactLines)
    return velocity, rotDirect, impactLines
    
def near(a, b, rtol = math.e + 5, atol = math.e + 8):
    #(a, b, rtol = math.e - 5, atol = math.e - 8):
    # test if two floats are sufficiently near each other
    #print('near: ',a, b, atol, rtol,abs(a - b), abs(atol + rtol * abs(b)))
    return abs(a - b) < .01#abs(atol + rtol * abs(b))

def line_intersect(line1, line2):
    '''
    Descrip:
        tests if two lines intersect, or are collinear
    Returns:
        None if lines are parallel, but non-collinear
        point(x,y) of intersection given two lines.
        point(x,y) arbitrary if the lines are collinear
    Parameters:
        line1 and line2: lines given as 2 points
    '''
    #print(line1)
    [x1,y1], [x2,y2] = line1
    [u1,v1], [u2,v2] = line2

    (a,b), (c,d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    e, f = u1-x1, v1-y1
    denom = float(a*d - b*c)
    if near(denom, 0):
        return False
    else:
        t = (e*d - b*f) /denom
        #s = (a*f - e*c) /denom

        px = x1 + t * (x2-x1)
        py = y1 + t * (y2-y1)
        return (px,py)
    
def get_lines(widg):
    widgLines = {}
    for i in widg.linesDict.keys():
        if "Line" in i:
            widgLines[i] = widg.linesDict[i]

    return widgLines

def widget_intersect(ghostLines, targetLines):
    '''
    Descrip:
        Checks to see if an Actor()'s lines intersects with a target widget's lines
    Returns:
        cross = a dictionary of lines on the ghost and the lines on the target that line intersects
    Parameters:
        ghostLines: dictionary of a ghost's lines
        targetLines: dictionary of a target widget's lines
    Calls:
        line_intersect():
    '''
    cross = {}
    for line1 in ghostLines.keys():
        for line2 in targetLines.keys():
            if line_intersect(ghostLines[line1], targetLines[line2]):
                if line1 in cross.keys():
                    cross[line1].append(line2)
                else:
                    cross[line1] = [line2]
    return cross

def check_inside(target, points):
    #print('check_inside: ', target, points)

    for point in points:
        x,y = point
        for i in target.linesDict.keys():
            if 'Line' in i:
                [x1,y1],[x2,y2] = target.linesDict[i]
                if (((y1-y2) * (x-x1)) + ((x2-x1) * (y-y1))) <= 0:
                    continue
                else:
                    #print('outside')
                    return False
    #print('inside')
    return True

def check_border(targetLine, ghostPoints, actorPoints):
    [x1,y1],[x2,y2] = targetLine
    for i in range(len(ghostPoints)):
        dX,dY = ghostPoints[i]
        x,y = actorPoints[i]
        if math.copysign(1, ((y1-y2) * (x-x1)) + ((x2-x1) * (y-y1))) != math.copysign(1, ((y1-y2) * (dX - x1)) + ((x2-x1) * (dY-y1))):
            border = True
        else:
            border = False
    #print('border: ',border, targetLine, ghostPoints, actorPoints)
    return border        

def point_on_lines(point, lines):
    #print (lines)
    for line in lines:
        #print(line)
        a, b, c = line[0], line[1], point

        for i in range(0,2):
            a[i] = round(a[i], 1)
            b[i] = round(b[i], 1)
            c[i] = round(c[i], 1)
        print('pol, abc: ',a,b,c)
        crossproduct = (round(((c[1] - a[1]) * (b[0] - a[0])),1)) - (round(((c[0] - a[0]) * (b[1] - a[1])),1))
        #if abs(crossproduct) > 0.001:
        if abs(crossproduct) > 10:
            print('crossproduct False')
            return False

        dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1]) * (b[1] - a[1])
        if dotproduct < 0:
            print('dotproduct False')
            return False

        squaredLength = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])
        if dotproduct > squaredLength:
            print('squaredLength False')
            return False
        '''
        [aX,aY], [bX,bY], [cX,cY] = line[0], line[1], point
        crossProduct = (cY - aY) * (bX - aX) - (cX - aX) * (bY - aY)
        if abs(crossProduct) > 0.001:
            return False

        dotProduct = (cX - aX) * (bX - aX) + (cY - aY) *(bY - aY)
        if dotProduct < 0:
            return False

        squaredLength = (bX - aX) * (bX - aX) + (bY - aY) * (bY - aY)
        if dotProduct > squaredLength:
            return False'''
    #print('poL: ',point,lines)
    return True

    

def get_intersection(actor, ghost, target):
    '''
    Descrip:
        determines the point of impact between two intersecting widgets
    Returns:
        px,py: point of first impact
        line1: line on ghost that impacted first
        line2: first line on target to be hit
    Calls:
        *get_lines():
        *get_widget_bound():
        *line_intersect():
    '''
    ghostLines = get_lines(ghost)
    targetLines = get_lines(target)
    '''DOES NOT HAVE A CASE WHERE THE SLOPES ARE THE SAME AND THEY INTERSECT, E.G. A FLAT
    FLAN LANDS ON A FLAT SURFACE, THE BOTTOM LINE, I.E. 3LINE, DOES NOT INTERSECT THE TOP LINE
    I.E. 1LINE'''
    cross = widget_intersect(ghostLines, targetLines) #dictionary of all lines on the ghost and which lines it will intersect given full movement on the target

    v = ghost.velocity
    
    mv = max(abs(v[0]), abs(v[1]))

    if mv != 0:
        deltaX  = abs(v[0]) / mv
        deltaY = abs(v[1]) / mv
    else:
        deltaX = 0
        deltaY = 0

    if deltaX != 0:
        xRng = int(mv/deltaX)
    else:
        xRng = 1
    if deltaY != 0:
        yRng = int(mv/deltaY)
    else:
        yRng = 1

    poImp = None
    impactLines = []
    pos = ghost.pos
    rot = ghost.rotation
    velo = ghost.velocity
    '''
    #print('iL: ', impactLines)
    #ghost.pos = ghost.x + deltaX, ghost.y + deltaY
    iPts = []
    iLns = []
    '''
    ghPts = {}
    trPts = {}
    for num, point in ghost.pointsDict.items():
        if check_inside(target, [point]):
            for j in target.pointsDict.keys():
                k = j + 1
                if k == len(target.pointsDict):
                    k = 0
                if k == -1:
                    k == len(target.pointsDict) - 1
                if line_intersect([point, actor.pointsDict[num]], [target.pointsDict[j], target.pointsDict[k]]):
                    border = [target.pointsDict[j], target.pointsDict[k]]
            ghPts[num] = border

    for num, point in target.pointsDict.items():
        if check_inside(ghost, [point]):
            for j in actor.pointsDict.keys():
                k = j + 1
                if k == len(target.pointsDict):
                    k = 0
                if k == -1:
                    k == len(target.pointsDict) -1
                if line_intersect([point, Vector(point) - Vector(actor.velocity)], [actor.pointsDict[j], actor.pointsDict[k]]):
                    border = [actor.pointsDict[j], actor.pointsDict[k]]
            trPts[num] = border
    '''for point in target.pointsDict():
        if check_inside(target, [point]):
            trPts[num] = (point)
    '''

    for each in ghPts.keys(): #and/or each in trPts.keys():
        ghPt = ghost.pointsDict[each]
        acPt = actor.pointsDict[each]
        newPt = Vector(acPt) + (Vector(actor.velocity) /2)
        midPt = Vector((((newPt[0] - actor.poImp[0]) * math.cos(math.radians(actor.rotSpd/2)))
                        - ((newPt[1] - actor.poImp[1]) * math.sin(math.radians(actor.rotSpd/2))))
                       (((newPt[0] - actor.poImp[0]) * math.sin(math.radians(actor.rotSpd/2)))
                        + ((newPt[1] - actor.poImp[1]) * math.cos(math.radians(actor.rotSpd/2)))))
        #find quadratic
        #acPt[1] = a*(acPt[0]**2) + b*(acPt[0]) + 1
        #ghPt[1] = a*(ghPt[0]**2) + b*(ghPt[0]) + 1
        #mdPt[1] = a*(mdPt[0]**2) + b*(mdPt[0]) + 1
        '''
        |acPt[0]**2  acPt[0]  1| |a|    |acPt[1]|
        |ghPt[0]**2  ghPt[0]  1| |b|  = |ghPt[1]|
        |mdPt[0]**2  mdPt[0]  1| |c|    |mdPt[1]|
        '''
        trajCoefMatr = matrix([[acPt[0]**2, acPt[0], 1],
                               [ghPt[0]**2, ghPt[0], 1],
                               [mdPt[0]**2, mdPt[0], 1]])
        trajY = matrix([[acPt[1]],
                        [ghPt[1]],
                        [mdPt[1]]])

        trajSolution = (trajCoefMatr.I) * trajY
        trajCoef = trajSolution.tolist()
        '''
        y = d[0][0]*(x**2) + d[1][0]*(x) + d[2][0]
        '''
        a = trajCoef[0][0]
        b = trajCoef[1][0]
        c = trajCoef[2][0]
        
        border = ghPts[each]
        borderMid = [((ghPts[each][0][0] + ghPts[each][1][0]) / 2), ((ghPts[each][0][1] + ghPts[each][1][1]) / 2)]
        bordCoefMatr = matrix([[(border[0][0]**2), border[0][0], 1],
                               [(border[1][0]**2), border[1][0], 1],
                               [ borderMid[0]**2,  borderMid[0], 1]])
        bordY = matrix([[border[0][1]],
                        [border[1][1]],
                        [borderMid[1]]])
        bordSolution = (bordCoefMatr.I) * bordY
        bordCoef = bordSolution.tolist()

        A = bordCoef[0][0]
        B = bordCoef[1][0]
        C = trajCoef[2][0]
        
        d = A-a
        e = B-b
        f = C-c

        x1 = (-e + math.sqrt((e**2) - (4 * d * f))) / (2 * d)
        x2 = (-e - math.sqrt((e**2) - (4 * d * f))) / (2 * d)
        y1 = (a * (x1 ** 2)) + (b * x1) + c
        y2 = (A * (x2 ** 2)) + (B * x2) + C

        #find the closest point to the actor point
        if math.sqrt(((x1 - acPt[0]) ** 2) + ((y1 - acPt[1]) ** 2)) < math.sqrt(((x2 - acPt[0]) ** 2) + ((y2 - acPt[1]) ** 2)):
            ptImpacts.append(x1,y1)
        else:
            ptImpacts.append(x2,y2)

    impacts = {}
    #Case 1: Corner of ghost and Corner of target
    #Case 2: Corner of ghost
    #Case 3: Corner of target
    #Case 4: Two points of a ghost

    #if len(ghPts) == 1 or len(trPts) == 1:
    for each in range(ghPts):
        for j in targetLines.keys():
        #    if check_border(target.linesDict[j], 
            point = line_intersect([ghost.pointsDict[ghPts.keys()], actor.pointsDict[ghPts.keys()]], target.linesDict[j])
            if point_on_lines(point, [target.linesDict[j]]):
                impacts[trPts.values()] = point
    for each in range(trPts):
        for i in ghostLines.keys():
            point = line_intersect([target.pointsDict[trPts.keys()], Vector(target.pointsDict[trPts.keys]) + -(Vector(ghost.velocity))], [actor.linesDict[i]])
            if point_on_lines(point, [actor.linesDict[i]]):
                impacts[ghPts.values()] = point

    #find minimum in impacts.values(), this is the distance the actor should move
    #find the fraction this represents of how much the ghost moved, apply that "magnifier" to the velocity NEVERMIND, NOT WORTH IT
    distDict = {}
    for x,y in impacts.items():
        distDict[x,y] = math.sqrt(((y[0] - x[0]) ** 2) + ((y[1] - x[1]) ** 2))

    minDist = min(distDict.values())
    for a,b in distDict.items():
        if b == minDist:
            deltaX = math.copysign(a[0][0] - a[1][0], actor.velocity[0])
            deltaY = math.copysign(a[0][1] - a[1][1], actor.velocity[1])
            
    if actor.poImp == []:
        ghost.pos = actor.pos + Vector(deltaX, deltaY)
    else:
        pass
    '''

    #
    
    for i in ghostLines.keys():
        for j in targetLines.keys():
            line1 = ghostLines[i]
            line2 = targetLines[j]
            if ghost.linesDict[str(i).strip('Line') + 'M']  == target.linesDict[str(j).strip('Line') + 'M']:
                if check_border(target.linesDict[j], ghost.linesDict[i], actor.linesDict[i]):
                   #print('Flat Slope')
                    #poImp = line_intersect((((Vector(ghost.linesDict[i][0]) + Vector(ghost.linesDict[i][1]))/2),((Vector(actor.linesDict[i][0]) + Vector(actor.linesDict[i][1]))/2)),target.linesDict[j])
                    #impactLines = [i,j]
                    iLns.append([line_intersect((((Vector(ghost.linesDict[i][0]) + Vector(ghost.linesDict[i][1]))/2),((Vector(actor.linesDict[i][0]) + Vector(actor.linesDict[i][1]))/2)),target.linesDict[j]), i, j])
            else:
                point = line_intersect(line1, line2)
                if point != False:
                    #print('prestruck')
                    #problem with point_on_line...
                    #if i == '3Line' and j == '1Line':
                        #print('targetLineDict: ',targetLines.keys(), targetLi)
                        #print('Line Check: ',point, ghost.linesDict[i], target.linesDict[j])
                        #with target.canvas:
                        #    Color(0,1,1,1)
                        #    Ellipse(size=(20,20), pos = (target.to_local(*Vector(point) - (10,10))))
                    if point_on_lines(point, [ghost.linesDict[i], target.linesDict[j]]):
                        #print('Struck')
                        #poImp = point
                        #impactLines = [i,j]
                        iPts.append([point, i, j])
                        print('ghost/targetLines: ', i, j)
    if iLns != []:
        while check_border(target.linesDict[iLns[0][2]], ghost.linesDict[iLns[0][1]], actor.linesDict[iLns[0][1]]):
            ghost.pos = Vector(ghost.pos) + (-(Vector(velo) / 10))
            ghost.pointsDict, ghost.linesDict = get_widget_bound(ghost)
            poImp = iLns[0][0]
            impactLines = [iLns[0][1], iLns[0][2]]
    elif iPts != []:
        #In this case an Actor() has hit a Target, There is at least one point of impact
        #thus iPts != [], there should usually only be one or two
        #Grab the Lines which the poImps are on, this should be either 1 or 2 for the Actor
        #and either 1 or 2 for the target
        #find the most extreme point on the Ghost() in the direction of the velocity between
        #the poImps for each line.
        #Find that point on the Actor(), this is the RED, then find the corresponding point
        #on the Target, this is the ORANGE. Find the distance between each RED and ORANGE
        #pair, and move the Ghost() the shortest distance of the two
        '''

    '''iPts = ([(x,y), '#Line', '#Line'], ...)'''
        #if len(iPts) == 2:
        #    for point in iPts:
        #        ghostCord = point[0], point[0] - (ghost.velocity) #Line between poImp
        #        actorPOImp = point[0] - (ghost.velocity) #The position of the impact points on the actor
    '''
        impacts = {}
        for pt in actor.pointsDict.keys():
            if point_on_lines(actor.pointsDict[pt], [actor.linesDict[iPts[0][1]], actor.linesDict[iPts[1][1]]]):
                for i in range(len(iPts)):
                    orange = line_intersect(target.linesDict[iPts[i][2]], [actor.pointsDict[pt], Vector(actor.pointsDict[pt]) + Vector(ghost.velocity)])
                    #print('orange: ', target.linesDict[iPts[i][2]])
                    if point_on_lines(orange, [target.linesDict[iPts[i][2]]]):
                        #print ('POL: ' + str(type(pt)) +' '+str(type(actor.pointsDict[pt])) + ' '+str(type(orange)))
                        impacts[tuple(actor.pointsDict[pt])] = orange # actor.pointsDict[pt] = RED
                ''''''#actorPOImp = pt
                #newImp.append(pt, [actor.linesDict[iPts[0][1]], actor.linesDict[iPts[1][1]]])
                if 'actor' in newImp.keys():
                    newImp{'actor'} = [newImp{actor}, [pt, actor.linesDict[iPts[0][1]], actor.linesDict[iPts[1][1]]]]
                else:
                    newImp{'actor'} =  [pt, actor.linesDict[iPts[0][1]], actor.linesDict[iPts[1][1]]]''''''
        for pt in target.pointsDict.keys():
            if point_on_lines(target.pointsDict[pt], [target.linesDict[iPts[0][2]], target.linesDict[iPts[1][2]]]):
                for i in range(len(iPts)):
                    orange = line_intersect(actor.linesDict[iPts[i][1]], [target.pointsDict[pt], Vector(target.pointsDict[pt]) - Vector(ghost.velocity)])
                    if point_on_lines(orange, [actor.linesDict[iPts[i][1]]]):
                        impacts[tuple(target.pointsDict[pt])] = orange # target.pointsDict[pt] = RED
                ''''''#targetPOImp = pt
                #newImp.append(pt, [target.linesDict[iPts[0][2]], target.linesDict[iPts[1][2]]])
                if 'target' in newImp.keys():
                    newImp{'target'} = [newImp{'target'}, [pt, target.linesDict[iPts[0][1]], target.linesDict[iPts[1][1]]]]
                else:
                    newImp{'target'} =  [pt, target.linesDict[iPts[0][1]], target.linesDict[iPts[1][1]]]''''''
        #Still need to find the fourth case, impact point on two lines - one line, but the two
        #lines do not share a point
        if impacts = {}:
            
        #Here we should have an impacts{} with a redPoint = orangePoint relation
        #Next we find the distance between each red/orange pair and use the lowest one
        #sqrt( ( (x2 - x1)^2) + ( (y2- y1)^2) )

        distDict = {}
        for a,b in impacts.items():
            distDict[a,b] = math.sqrt(((b[0] - a[0]) ** 2) + ((b[1] - a[1]) ** 2))

        distList = []
        for i in distDict.values():
            distList.append(i)

        minDist = min(distDict.values())
        for a,b in distDict.items():
            if b == minDist:
                moveToFrom = a
                print('moveToFrom: ' + str(a))
    '''                    
    '''     impacts={}

            
            #elif len(newImp) == 2:
            for i,j in newImp.items():
                if 'actor' in i:
                    for a in range(1,3):
                        orange = line_intersect(j[a], [j[0], Vector(j[0]) + Vector(ghost.velocity)])
                        if point_on_lines(orange, j[a]):
                            impacts{j[0]} = orange #j[0] = RED, orange = ORANGE
                if 'target' in i:
                    for a in range(1,3):
                        orange = line_intersect(j[a], [j[0], Vector(j[0]) + Vector(ghost.velocity)])
                        if point_on_lines(orange, j[a]):
                            impacts{j[0]} = orange #j[0] = RED, orange = ORANGE
                
                    
                for j in range(0,2):
                    if point_on_lines(newImp[0], newImp[j]):
                        #on the Actor()
                    for i in range(len(newPOImp)):
                        orange = line_intersect(target.linesDict(iPts[i][2]), [newPOImp[0], Vector(newPOImp[0]) + Vector(ghost.velocity)])
                        if point_on_lines(orange, target.linesDict(iPts[i][2])):
                            impacts{newPOImp} = orange
                        else:
                            pass

            #Here we should have an impacts{} with a redPoint = orgPoint relation
            #Next we find the distance between each red/orange pair and use the lowest one
                
            if iPts[0][1] == iPts[1][1]:
                #One line on the Actor() hitting two lines on the Target, find the extreme
                #point on the target between the two poImps
                redPt = 
            if iPts[0][2] == iPts[1][2]:
                pass
            else:
                impactSegment = 
        
        #First thing is to back the ghost out of the target
        while line_intersect(iPts[0][1], iPts[0][2]) or line_intersect(iPts[1][1], iPts[1][2]):
            ghost.pos = Vector(ghost.pos) + (-(Vector(velo) / 10))
            ghost.pointsDict, ghost.linesDict = get_wiget_bound(ghost)
            #if 
            
        #find the point of impact, find the appropriate impactLines on each widget
        after finding the poImp
    '''
        
                       
    #if ghost.pos == pos:
    for y in range(yRng):
        for x in range(xRng):
            ghost.pos = (ghost.x + (deltaX * x), ghost.y + (deltaY * y))
            if ghost.deltaRot != 0:
                if actor.poImp != None:
                    rotPoint = actor.poImp
                else:
                    rotPoint = ghost.center
                #print('rotation incrementation: ',actor.rotDirect)
                #r = Matrix().rotate(-(actor.rotDirect) * math.radians(-(actor.rotSpd * (x/xRng))), 0, 0,1)
                #ghost.apply_transform(r, post_multiply = True, anchor = ghost.to_local(*rotPoint))
            ghost.pointsDict, ghost.linesDict = get_widget_bound(ghost)
            pos, rot = ghost.pos, ghost.rotation
            
            #for i in cross.keys():
            #    for j in cross[i]:
            for i in ghostLines.keys():
                for j in targetLines.keys():
                    line1 = ghostLines[i]
                    line2 = targetLines[j]
                    #print('Lines: ',i, ghost.linesDict[str(i).strip('Line') + 'M'], j, target.linesDict[str(j).strip('Line') + 'M'])
                    if ghost.linesDict[str(i).strip('Line') + 'M']  == target.linesDict[str(j).strip('Line') + 'M']:
                       #print('if')
                        #if ghost.linesDict[str(i).strip('Line') + 'M'] >= (target.linesDict[str(j).strip('Line')+'M'] -0.1) or ghost.linesDict[str(i).strip('Line') + 'M'] <= (target.linesDict[str(j).strip('Line')+'M'] +0.1):
                        #print (ghost.linesDict[str(i).strip('Line') + 'M'], target.linesDict[str(j).strip('Line')+'M'])
                        #if check_inside(target, ghost.linesDict[str(i)]) and check_border(target.linesDict[j], ghost.linesDict[i], actor.linesDict[i]):
                        if check_border(target.linesDict[j], ghost.linesDict[i], actor.linesDict[i]):
                            impactLines = [i,j]
                            poImp = line_intersect((((Vector(ghost.linesDict[i][0]) + Vector(ghost.linesDict[i][1]))/2),((Vector(actor.linesDict[i][0]) + Vector(actor.linesDict[i][1]))/2)),target.linesDict[j])
                            ghost.pos = poImp
                            ghost.velocity = Vector(math.copysign(abs(ghost.velocity[0]) - (x/xRng), ghost.velocity[0]),
                                                    math.copysign(abs(ghost.velocity[1]) - (y/yRng), ghost.velocity[1]))
                           #print('Same Slope Capture')
                            return poImp, impactLines
                    else:
                       #print('else')
                        point = line_intersect(line1, line2)
                        #print(i,j,point)
                        if point != False:
                            #print(i, j, point_on_lines(point, [line1, line2]))
                            if point_on_lines(point, [ghost.linesDict[i], target.linesDict[j]]):
                                #print (ghost.linesDict[str(i).strip('Line') + 'M'], target.linesDict[str(j).strip('Line')+'M'])
                               #print('Capture Point')
                                #if point:
                                poImp = point
                                impactLines = [i,j]
                                #deltaX = x/xRng
                                #deltaY = y/yRng
                                #print(deltaX, deltaY)
                                #ghost.velocity = Vector(ghost.velocity) - (x/xRng, y/yRng)
                                ghost.velocity = Vector(math.copysign(abs(ghost.velocity[0]) - (x/xRng), ghost.velocity[0]),
                                                        math.copysign(abs(ghost.velocity[1]) - (y/yRng), ghost.velocity[1]))
                                #velo[0] = math.copysign(abs(ghost.velocity[0]) - (x/xRng), ghost.velocity[0])
                                #velo[1] = math.copysign(abs(ghost.velocity[1]) - (y/yRng), ghost.velocity[1])
                                #print(ghost.velocity)
                                #return point, [i,j]
                        else:
                            pass
                    #print(i, line1, j, line2)
    
    #print('Velo: ', velo)
   #print('striking @ ', ghost.x, ghost.center_x, poImp, impactLines)
    ghost.velocity = velo
    ghost.pos = pos
    ghost.rotation = rot
    #print('posvelo ',pos, velo)
    #print('get_intersection: ',impactLines)
    
    return poImp, impactLines
    #return None, None

def collide_widget_group(lstWidg, lstTarg):
    '''
    Descrip:
        Runs collide_widget against two lists of widgets
    Returns:
        dict{collision} of collsion[widget] = collided widget
    Parameters:
        lstWidg: moving widgets to test collision
        lstTarg: widgets to test collision against
    '''
    collision = {}
    for widg in lstWidg:
        for target in lstTarg:
            if widg != target:
                if widg.collide_widget(target):
                    if widg in collision.keys():
                        collision[widg].append(target)# = [collision[widg], target] #allows for multiple collisions from one widget
                    else:
                        collision[widg] = [target]
    #print('collision: ',collision)
    return collision

def get_widget_bound(widget):
    '''
    Descrip:
        computes the boundaries of a circular widget
    Returns:
        pointsDict: a dictionary of eight points around the edge of the
            circle and the center of the circle
    Parameters:
        widget: the circular widget
    '''
    #places the widget at the origin, with rotation of 0
    center = widget.center
    rotation = widget.rotation

    widget.center = (0,0)
    widget.rotation = 0

    pointsDict = {}
    linesDict = {}
    
    if 'circ' in widget.shape:
        points = widget.shape['circ']
        cut_in = 0
        rads = 360 / points
    elif 'rect' in widget.shape:
        points = 4
        cut_in = widget.shape['rect'] * 0.45
        
    #calculate the basic points around the shape (not adjusted for pos or rotation
    for p in range(points):
        if 'circ' in widget.shape.keys():
            a = math.cos(math.radians(360 - (p * rads)))
            b = math.sin(math.radians(360 - (p * rads)))

            x, y = ((Vector(center) + (Vector(a,b) * (Vector(widget.size) /2)))) 
        if 'rect' in widget.shape.keys():
            if p == 0:
                x,y = Vector(widget.x, widget.y)
            elif p == 1:
                x,y = Vector((widget.x + cut_in), widget.top)
            elif p == 2:
                x,y = Vector((widget.right - cut_in), widget.top)
            elif p == 3:
                x,y = Vector(widget.right, widget.y)
        
        pointsDict[p] = [x,y]

    #resets the center and rotation to the true pos/rotation
    widget.rotation = rotation
    widget.center = center
    
    for point in pointsDict.keys():
        x, y = pointsDict[point]
        #rotates the points in accordance with the true rotation of the widget
        #xV = (((x - {point.x of rotation}) *math.cos(math.radians({degrees of rotation})))
        #      - ((y - {point.y of rotation}) * math.cos(math.radians({degrees of rotation}))))
        xPrime = ((x * math.cos(math.radians(rotation))) + (y * -math.sin(math.radians(rotation))))
        yPrime = ((x * math.sin(math.radians(rotation))) + (y * math.cos(math.radians(rotation))))
        #if rotation != 0:
        #   #print ('y: ',int(rotation), point, y)

        #moves the points accordingly
        xPrime, yPrime = Vector(xPrime, yPrime) + Vector(center)
        #replaces the point in the dictionary with the new modified point
        pointsDict[point] = Vector(xPrime, yPrime)
        
    for point in pointsDict.keys():
        #find lines
        if point + 1 in pointsDict.keys():
            q = point + 1
        else:
            q = 0
        
        x,y = pointsDict[point]
        u,v = pointsDict[q]

        linesDict[str(point) + 'Line'] = Vector((x,y),(u,v))
        #linesDict[str(q) + 'Line'] = Vector((x,y),(u,v))

        #find delta between points on line
        deltaX, deltaY = u - x, v - y

        #find normal
        linesDict[str(point) + 'Norm'] = Vector(deltaY, -abs(deltaX)).normalize()
        #linesDict[str(q) + 'Norm'] = Vector(-deltaY, deltaX).normalize()

        #find slope
        if deltaX == 0:
            slope = 1000000
        elif deltaY == 0:
            slope = 0
        else:
            slope = ((y - v) / (x - u))
        #linesDict[str(q) + "M"] = slope
        linesDict[str(point) + "M"] = slope

        #find Y-intercept
        b = y - slope * x
        #linesDict[str(q) + "B"] = b
        linesDict[str(point) + "B"] = b

    with widget.canvas:
        for line in linesDict.keys():
            if 'Line' in line:
                points = linesDict[line]
                localPt = []
                for i in range(len(points)):
                    localPt.append(widget.to_local(*points[i]))
                Color(0,1,0,1)
                Line(points = (localPt[0][0], localPt[0][1], localPt[1][0], localPt[1][1]))
        for point in pointsDict.keys():
            if point == 0:
                Color(0,0,1,1)
                #print('which: ',pointsDict[point], widget.pos)
            elif point == 1:
                Color(0,1,1,1)
            elif point == 2:
                Color(0,1,0,1)
            else:
                Color(1,1,0,1)
            #Color(1 - ((point+1) / 4.0),0,0 + ((point+1) / 4.0),1)
            #Ellipse(size = (20,20), pos=(widget.to_local(*pointsDict[point] - (10,10))))
        Color(0,0.5,0.5,1)
        Ellipse(size = (10,10),     pos=(widget.to_local(*Vector(widget.pos) -(5 ,5 ))))
    
    return pointsDict, linesDict

def scatter_ghost(target):
    '''
    Descrip:
        copies a target Scatter() with specific attributes
    Returns:
        ghost: a Scatter() widget that has many attributes of the target widget copied    
    Parameters:
        target: a target widget to copy
    '''
    ghost = Scatter()
    ghost.size = target.size
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
    
    try:
        ghost.cut_in = target.cut_in
    except:
        ghost.cut_in = 0
    try:
        ghost.poRefl = target.poRefl
    except:
        ghost.poRefl = None
    #print('ghosting: ',target.pos, ghost.pos)
    return ghost

def get_ghosts(actors):
    '''
    Calls:
        *scatter_ghost() to create a scatter clone of the passed widget
        *get_widget_bound() to get the line dictionary (Y-intercept, Slope, Normalize Slope, Line Points)
        #rotate_by_slope() checks if the ghost rotates through another widget
    Assigns:
        new ghost positions, rotations to check collisions/intersects against
    Returns:
        futures{[actor] = [ghost]} associate an actor (e.g. Flan 1) with a ghost (e.g. Flan 1 Ghost)
        statics{[actor] = [actor]} associate an actor with itself
    '''    
    futures = {}
    for actor in actors:
        if actor.poImp != None or actor.velocity != Vector(0,0):
            ghost = scatter_ghost(actor)
            ghost.pos = (Vector(*ghost.pos) + Vector(actor.velocity))   #get new ghost position
            #print('get_ghosts: poImp: ', actor.poImp, actor.rotDirect)
            if actor.poImp == None:
               #print('is pushed')
                if Vector(ghost.velocity)[0] < 0:
                   #print('to the left', ghost.velocity[0])
                    actor.rotDirect = 1
                elif Vector(ghost.velocity)[0] > 0 :
                   #print('to the right')
                    actor.rotDirect = -1
                else:
                    print('straight')
                    actor.rotDirect = 0
                rotSpd = Vector(ghost.velocity)[1] / 5
                poI = ghost.center
            else:
                #print('is rotating')
                if actor.rotBound != []:
                    #print('rot Bounded')
                    if ghost.rotation < actor.rotBound[0] or ghost.rotation > actor.rotBound[1]:
                        actor.rotDirect = -actor.rotDirect #used for rotating obsticles that rotate back and forth
                rotSpd = actor.rotSpd
                poI = actor.poImp
            #print('general rotation: ', actor.rotDirect)
            r = Matrix().rotate(actor.rotDirect * math.radians(-(rotSpd)), 0, 0, 1)
            #print('rotating ghosts: ', actor.poImp)
            #NOT GETTING A ROTDIRECT!!!
           #print('ghost pre rot: ', ghost.rotation, actor.rotDirect)
            ghost.apply_transform(r, post_multiply = True, anchor = ghost.to_local(*poI))
           #print('ghost post rot: ', ghost.rotation, actor.rotation)

            ghost.pointsDict, ghost.linesDict = get_widget_bound(ghost)
            futures[actor] = ghost
            #print('ghost',actor.pos, ghost.pos)
        else:
            futures[actor] = actor
            #print('actor',actor.pos)

    return futures

def get_future_pos(actors, scenery):
    '''
    Descrip:
        modifies the position and rotation of ghosts from futures if neccessary
        and assings the new positions to the Actor()s
    Returns:
        move = {[actor] = [ghost/actor]} used to pass new pos, rotation, and other attributes to a moving actor
    Parameters:
        self: ...
        actors: list of all potential moving widgets, i.e. flans, fruits, and obsticles (moving floors are obsticles)
    Calls:
        *get_ghosts() to get the "ghosts" (i.e. the widget if it moved) of the next step
        *collide_widget_group() to determine if any of ghosts' widgets will collide with any other widget
        *get_intersection() to determine if colliding widget actors (images) intersect
    Assigns:
        a target to each actor that intersects another actor
    '''
    futures = get_ghosts(actors)    #dictionary of moving actors and static actors
    bbox_collisions = collide_widget_group(futures.values(), futures.values() + scenery)#self.floors]) #dictionary of actor widgets that collided with another widget
    move = {}
    for actor in futures.keys():
        ghost = futures[actor]
            
        if ghost not in bbox_collisions.keys():     #ghost did not collide
            #print('ghost did not collide')
            pos = ghost.pos
            rotation = ghost.rotation
            velocity = ghost.velocity
            rotDir = actor.rotDirect
            poImp = None
            impactLines = []
            
        elif ghost in bbox_collisions.keys():
            #print('ghost collided')
            new_hit = None
            for collision in bbox_collisions[ghost]:       # for each widget that collided
                target = collision
                if target not in actor.target:
                    actor.target.append(target)
                    new_hit = target
                #else:
                #    new_hit = target

            ghost.deltaRot = ghost.rotation - actor.rotation
            
            if actor.impactLines != []: #if there IS an impactLine, i.e. has already collided with something
               #print('rotation check: ', actor.poImp)
                if len(actor.target) == 1:
                    stop = rotate_by_slope(actor, ghost)
                    #    stop = True
                    #else:
                    #    stop = False
                else:
                    #c = rotate_by_slope(actor, ghost, 'target' = new_hit)
                    stop = rotate_by_slope(actor, ghost, target = new_hit)
                    #    stop = True
                    #else:
                    #    stop = False
                        
                if stop == True:
                    #print('stopped')
                    poImp = None #actor.poImp
                    #impactLines = actor.impactLines
                else:
                    #print('ongoing')'''
                    poImp = actor.poImp
                impactLines = actor.impactLines
                pos = ghost.pos
               #print(actor.rotation, ghost.rotation)
                rotation = ghost.rotation
                velocity = Vector(0,0)
                #print('velocity is reset: ', velocity)
                rotDir = actor.rotDirect
            else: #had not intersect, but may now
               #print('free ghost  ', ghost.pos)
                pos = ghost.pos
                rotation = ghost.rotation
                velocity = ghost.velocity
                rotDir = actor.rotDirect
                #print(pos, velocity)
                poImp = None
                impactLines = []
                for target in actor.target:
                    t_pI, t_iL = get_intersection(actor, ghost, target)
                    #print('t_iL 1: ',t_iL)
                    if t_pI != None and t_iL != None:
                       #print('t_iL 2: ',t_iL)
                        poImp = t_pI
                        impactLines = t_iL
                        #pos, rotation, velocity = ghost.pos, ghost.rotation, ghost.velocity
                if impactLines != []:
                   #print('to bounce')
                    velocity, rotDir, impactLines = bounce(actor, ghost.velocity, target, poImp, impactLines) #set new velocity, rotation
                    #print('!= [] :', impactLines)
        #print('actor to poImp: ',actor.poImp)
        move[actor] = [pos, rotation, velocity, rotDir, poImp, impactLines]
       #print('get_futures: actor move dictionary: ',move[actor])#[0], move[actor][5])
        #print(move[actor])
        #if move[actor][5] != []:
        #   #print(jfkla)
        
    return move

def check_slope_stability(actor, surfSlope, stability):
    if surfSlope < stability[0]:    #stand
        #print('stand')
        actor.velocity = Vector(0,0)
        actor.vDelt = [0, 0]
    if surfSlope > stability[0]:    #slide
       #print('slide')
        actor.vDelt = Vector(actor.vDelt) + Vector((actor.vDelt[1]/slope), vDelt[1])
        actor.velocity = Vector(actor.velocity) + Vector(vDelt)
    if surfSlope > stability[1]:    #rotate
       #print('rotate')
        actor.rotDirect = math.copysign(1, surfSlope)

def check_overhang(actor, surfPoints):
    max_x = max(surfPoints[0][0],surfPoints[1][0])
    min_x = min(surfPoints[0][0],surfPoints[1][0])
    
    if actor.center_x < min_x:
       #print('left hanging')
        actor.poImp = min_x
        actor.rotDirect = 1
    elif actor.center_x > max_x:
       #print('right hanging')
        actor.poImp = max_x
        actor.rotDirect = -1
    else:
        pass
    

def gravity(actors, fall): #, move):
    '''
    Parameters:
        self, actor widget
    Sets:
        modifies widge.velocity attributes
    '''
    #print('grav',fall)
    terminalV = 3.3
    for actor in actors:
        if actor.impactLines != []:
            #print('Impacted: ',actor, actor.impactLines)
            if actor.impactLines == 'attached':
                pass
            else:
                stability = actor.stability
                selfSlope = actor.linesDict[str(actor.impactLines[0]).strip('Line') + "M"]
                surfSlope = actor.linesDict[str(actor.impactLines[1]).strip('Line') + "M"] #remember to calculate slopes on move() & up()

                check_slope_stability(actor, surfSlope, actor.stability)

                if len(actor.target) == 1:
                    point0 = str(actor.impactLines[1]).strip('Line')
                    point1 = int(str(actor.impactLines[1]).strip('Line')) + 1
                    if point1 not in actor.target[0].pointsDict.keys():
                        point1 = 0
                    surfPoints = (actor.target[0].pointsDict[int(point0)], actor.target[0].pointsDict[int(point1)])

                    check_overhang(actor, surfPoints)
        else:
            if abs(actor.vDelt[1]) < 0.3:
                actor.vDelt[1] += fall[1]
            #actor.vDelt = Vector(actor.vDelt) + Vector(fall) #self.push, self.gravity)
            #if abs(actor.vDelt[0]) > 0.1:
            #    actor.vDelt[0] = math.copysign(0.99, actor.vDelt[0])
            #if abs(actor.vDelt[1]) > 0.1:
            #    actor.vDelt[1] = math.copysign(0.99, actor.vDelt[1])
            #print('vDelt: ',abs(actor.vDelt[1]))
            
            actor.velocity = Vector(actor.velocity) + Vector(actor.vDelt)
            #print('gravity velocity: ', actor.velocity)
            #if actor.velocity[0]) > terminalV:
            #    actor.velocity[0] = math.copysign(terminalV, actor.velocity[0])
            if actor.velocity[1] > terminalV or actor.velocity[1] < -terminalV:
                actor.velocity[1] = math.copysign(terminalV, actor.velocity[1])
        
            
def move_actors(move):
    
    for actor in move.keys():
       #print('move: ',move[actor])
        [pos, rotation, velocity, rotDir, poImp, impactLines] = move[actor]
        actor.pos = pos
        actor.rotation = rotation
        actor.velocity = velocity
        actor.rotDirect = rotDir 
        actor.poImp = poImp
        actor.impactLines = impactLines
        actor.pointsDict, actor.linesDict = get_widget_bound(actor)
        
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
            #if 'alt' in value.keys():
                #if 'plate' in value['alt']:
                #    self.plates.append(actor)
                    #print(actor.top)
                #elif 'start' in value['alt']:
                #    self.start.append(actor)
                #elif 'finish' in value['alt']:
                #    self.finish.append(actor)
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
        #lvlfile = os.path.join('Levels',filename + '.txt')
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
        #print(self.lstFlan,self.lstFloor)
        # widget tracking lists
        self.flans, self.fruits, self.floors, self.plates, self.start, self.finish, self.obsticles = [], [], [], [], [], [], []
        #self.actors, self.floors = [self.flans + self.fruits + self.obsticles], []
        #print(self.lstFloor.items())
        for key, value in self.lstFloor.items():
            self.add_actor(key, value)
            
        for key, value in self.lstObsticles.items():
            self.add_actor(key, value)
        
        for key, value in self.lstFlan.items():                
            self.add_actor(key, value)

        #pos_on_plate(self.flans, self.plates)

        #remember to make init lines/points-Dict
        for widget in (self.flans + self.floors + self.plates + self.start + self.finish + self.obsticles):
            widget.pointsDict, widget.linesDict = get_widget_bound(widget)

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
               #print('pre roll call: ', actor.rotDirect)
        scenery = []
        for scene in self.floors:
            scenery.append(scene)
        #for actor in self.fruits:
        #    actors.append(actor)
        #for actor in self.obsticles:
        #    actors.append(actor)

        gravity(actors, [self.push, self.gravity]) # if any Actor() is falling or sliding, modifies their velocity and vDelt
        move = get_future_pos(actors,scenery)    # compiles a dictionary of the future position/rotation for every actor that changes position, accounts for stunted movement due to collisions
        move_actors(move)

        for actor in move.keys():
           #print('post roll call: ', actor.rotDirect)
            if move[actor][4] != None:
                with self.canvas:
                    Color(1,1,1,1)
                    Ellipse(size = (20,20), pos = (Vector(move[actor][4]) - (10,10)))

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
        
        #if touch.is_double_tap:
        
        #    #print(' - distance is', touch.double_tap_distance)
        #    touch.double_tap_time = 0.0
 
        self.held = touch.pos
        for child in self.children:
            if child in self.flans:
                if child.collide_point(*touch.pos):
                    self.grabbed = child
                    Clock.schedule_interval(self.count_time, 1/60)
                    '''print(' - interval is', touch.double_tap_time, touch.time_start, touch.)
                    if touch.is_double_tap:# and touch.double_tap_time < 0.75 and touch.double_tap_time > 0.0:
                        #print(' - interval is', touch.double_tap_time)
                        if 'double' in self.grabbed.abilities: #abilites keys(): what is the ability attribute?
                            #do double-tap ability
                            #print('double')'''

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
                self.grabbed.velocity = Vector(0,0)
        self.grabbed = None
        self.held = None
        self.touch_timer = 0.0
        Clock.unschedule(self.count_time)

        if self.right <= self.size[0] + 30 or self.x >= -30 or self.top <= self.size[1] + 30 or self.y >= -30:
            Clock.schedule_interval(self.bounce_back, 1/60)

        return super(BlackBoard, self).on_touch_up(touch)
        
class WhiteBoard(BlackBoard):
    def __init__(self):
        BlackBoard.__init__(self)
