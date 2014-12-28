def reduce_impact_lines(lines):
    
def get_impacts(actor, ghost, target):

    #checks to see if any Actor() point will be inside the target, or if
    #any target point will be inside the Actor() given it's next velocity step
    for num, point in ghost.pointsDict.items():
        if check_inside(target, [point]):
            ghPts[num] = point
    for num, point in target.pointsDict.items():
        point = Vector(point) - Vector(actor.velocity)
        if check_inside(actor, [point]):
            trPts[num] = point

    points = {}
    lines = {}
    '''Case 1: intersecting each other
    Case 2: ghost intersects target
    Case 3: target intersects ghost
    Case 4: two points in the '''

    for num,redPt in ghPts.items():
        for p in target.pointsDict.keys():
            q = p + 1
            if q == len(target.pointsDict):
                q = 0
            orangePt = line_intersect([actor.pointsDict[num], ghost.pointsDict[num]], [target.pointsDict[p], target.pointsDict[q]])
            if point_on_lines(orangePt, [target.pointsDict[p], target.pointsDict[q]]):
                points[redPt] = orangePt
                lines[redPt] = [target.pointsDict[p], target.pointsDict[q]]
    for num,redPt in trPts.items():
        for p in actor.pointsDict.keys():
            q = p + 1
            if q == len(target.pointsDict):
                q = 0
            orangePt = line_intersect([target.pointsDict[num], target.pointsDict[num] - Vector(actor.velocity)], [actor.pointsDict[p], actor.pointsDict[q]])
            if point_on_lines(orangePt, [actor.pointsDict[p], actor.pointsDict[q]]):
                points[redPt] = orangePt
                lines[redPt] = [actor.pointsDict[p], actor.pointsDict[q]]

    distDict = {}
    for x,y in points.items():
        distDict[x] = math.sqrt(((y[0] - x[0]) ** 2) + ((y[1] - x[1]) ** 2))
    minDist = min(distDict.values())
    for redPt,dist in distDict.items():
        if dist = minDist:
            impPt = points[redPt]

            if actor.rotDir == 0:
                deltaX = math.copysign(redPt[0] - points[redPt][0], actor.velocity[0])
                deltaY = math.copysign(redPt[1] - points[redPt][1], actor.velocity[1])
                impDist = Vector(deltaX, deltaY)

                ghost.pos = Vector(actor.pos) + impDist

            else:
                pass
    '''For rotation:
    #When the ghost rotates through a line, catch the target line
    #Actor Point = x,y; Ghost Point = x+u, y+v; Target Line = [[a,b][c,d]]
    #Find the distance of the line from poImp to either the end of the falling line
    #segment (when the ghost hits the target) or to the next poImp (when the target
    #hits the ghost)'''

    '''
    So, if the ghostPoint is inside find the length of the line segment = a:
        find the point on the target line that is a distance of a away from
        the original poImp

        l = {x = x1 + (x2-x1)*t}{y = y1 + (y2-y1)*t} end points are at t=0, t=1
        m = {u = u1 + (u2-u1)*s}{v = v1 + (v1-v1)*s} end points are at s=0, s=1
        p = a,b #known point
        q = c,d #unknown point
        d = e   #pre calculated line length

        t = (a-x1)/(x2-x1) OR (b-y1)/(y2-y1)
        
        s = (d - y*t) / x = (e - b*t) / a
        c,d = u1 + ((u2-u1)*s), v1 + ((v2-v1)*s)

        find the bounds of a new line segment, defined by the x position on the
        target line for the x on the ghostPoint and actorPoint at the end of
        its line segment
    
    If the targetPoint is inside find the line between the original poImp
    and the new poImp:
        find the slope, translate that to the appropriate rotation value
        given which line is the falling line (line 4->0 is flat when rotation is 0
        all others must be calculated)
        0 = 1000000,0,1000000,0
        346 = 4.0107, -0.2493, 4.0107, -0.2493
        320 = 1.1917, -08.390, 1.1917, -0.8390
    '''
            
            '''#find the impact lines for actor and target
            for num, point in ghost.pointsDict.items():
                if redPt == point:
                    targetLines = lines[redPt]
                    
                    zero = num -1
                    one = num
                    two = num + 1
                    if zero == -1:
                        zero = len(ghost.pointsDict) - 1
                    if two == len(ghost.pointsDict):
                        two = 0
                    ghostLines = [[ghost.pointsDict[zero], ghost.pointsDict[one]], [ghost.pointsDict[one], ghost.pointsDict[two]]]
                

            for num, point in target.pointsDict.items():
                if redPt == point:
                    zero = num - 1
                    one = num
                    two = num + 1
                    if zero == -1:
                        zero = len(target.pointsDict) - 1
                    if two == len(ghost.pointsDict):
                        two = 0
                    targetLines = [[target.pointsDict[zero], target.pointsDict[one]], [target.pointsDict[one], target.pointsDict[two]]]
                ghostLines = lines[redPt]
            impLn = [ghostLines, targetLines]
    if len(impLn[0]) > 1:
        impLn[0] = reduce_impact_lines(impLn[0])
    if len(impLn[1]) > 1:
        impLn[1] = reduce_impact_lines(impLn[1])'''

    return impPt

def get_next_pos(actors, scenery):

    bbox_collisions = collide_widget_group(

def get_slope(xy, uv):
    x,y = xy
    u,v = uv
    
    deltaX = u-x
    deltaY = v-y

    if deltaX == 0:
        return 1000000
    elif deltaY == 0:
        return 0
    else:
        return ((y-v) / (x-u))

def get_norm(xy, uv):
    x,y = xy
    u,v = uv

    deltaX = u-x
    deltaY = v-y

    return Vector(deltaY, -(abs(deltaX))).normalize()

def gravity(actors, fall):

    termVelocity = 3.3
    for actor in actors:
        if actor.impPt == []:
            if abs(actor.vDelt[1]) < 0.3:
                actor.vDelt[1] += fall[1]
            if actor.vDelt > 0:
                actor.vDelt[0] -= fall[0]
            elif actor.vDelt < 0:
                actor.vDelt[0] += fall[0]

            if actor.velocity[1] > termVelocity or actor.velocity[1] < -termVelocity:
                pass
            else:
                actor.velocity = Vector(actor.velocity) + Vector(actor.vDelt)

        else:
            #rotate
            selfSlope = get_slope(?1,?2)
            surfSlope = get_slope(?1,?2)

            check_slope_stability()
        
