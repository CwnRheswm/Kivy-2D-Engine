import math
from kivy.graphics import Color, Ellipse
from kivy.vector import Vector
from _boards import line_intersect, point_on_lines
from numpy import matrix

def find_impact_points(orgnlPt, border, velocity, rotPt, rotSpd):
    newPt = Vector(orgnlPt) #+ (velocity / 2) #pass -velocity if this is the target, not the actor
    midPt = Vector((((newPt[0] - rotPt[0]) * math.cos(math.radians(rotSpd/2))
                        - ((newPt[1] - rotPt[1]) * math.sin(math.radians(rotSpd/2)))),
                       (((newPt[0] - rotPt[0]) * math.sin(math.radians(rotSpd/2)))
                        + ((newPt[1] - rotPt[1]) * math.cos(math.radians(rotSpd/2))))))
    midPt = midPt + rotPt

    q1Pt = Vector((((newPt[0] - rotPt[0]) * math.cos(math.radians(rotSpd*.25)))
                        - ((newPt[1] - rotPt[1]) * math.sin(math.radians(rotSpd*.25)))),
                       (((newPt[0] - rotPt[0]) * math.sin(math.radians(rotSpd*.25)))
                        + ((newPt[1] - rotPt[1]) * math.cos(math.radians(rotSpd*.25)))))
    q1Pt = q1Pt + rotPt

    q3Pt = Vector((((newPt[0] - rotPt[0]) * math.cos(math.radians(rotSpd*.75)))
                        - ((newPt[1] - rotPt[1]) * math.sin(math.radians(rotSpd*.75)))),
                       (((newPt[0] - rotPt[0]) * math.sin(math.radians(rotSpd*.75)))
                        + ((newPt[1] - rotPt[1]) * math.cos(math.radians(rotSpd*.75)))))
    q3Pt = q3Pt + rotPt
    print('q3pt: ', q3Pt)
    
    newPt = Vector(orgnlPt) + (velocity) #pass -velocity if this is the target, not the actor
    ghostPt = Vector((((newPt[0] - rotPt[0]) * math.cos(math.radians(rotSpd)))
                        - ((newPt[1] - rotPt[1]) * math.sin(math.radians(rotSpd)))),
                       (((newPt[0] - rotPt[0]) * math.sin(math.radians(rotSpd)))
                        + ((newPt[1] - rotPt[1]) * math.cos(math.radians(rotSpd)))))
    ghostPt = ghostPt + rotPt
    print(orgnlPt, midPt, ghostPt)

    x1,y1 = orgnlPt
    x2,y2 = midPt
    x3,y3 = ghostPt
    
    line1 = (x1,y1),(x2,y2)
    mid1 = [((x1 + x2)/2), ((y1 + y2)/2)]
    slope1 = (y2 - y1)/(x2 - x1)
    negSlope1 = -(1/slope1)
    #mid1[1] = negSlope1*mid[0] + b
    b1 = mid1[1] - (negSlope1*mid1[0])
    u1, u2 = mid1[0]-1, mid1[0]+1
    v1 = negSlope1*(u1) + b1
    v2 = negSlope1*(u2) + b1
    print('line 1 stats: ', mid1, slope1, negSlope1, b1)
    
    
    line2 = (x2,y2),(x3,y3)
    mid2 = [(x2 + x3)/2, (y2 + y3)/2]
    slope2 = (y3 - y2)/(x3 - x2)
    negSlope2 = -(1/slope2)
    b2 = mid2[1] - (negSlope2*mid2[0])
    u3, u4 = mid2[0]-1, mid2[0]+1
    v3 = negSlope2*u3 + b2
    v4 = negSlope2*u4 + b2
    print('bisecting lines: ',u1,v1,u2,v2,u3,v3,u4,v4)
    center = line_intersect([[u1,v1],[u2,v2]], [[u3,v3],[u4,v4]])
    radius = math.sqrt(((x1 - center[0]) ** 2) + ((y1 - center[1]) ** 2))

    h,k = center
    r = radius
    [p1,q1],[p2,q2] = border
    print(p1,q1,p2,q2)
    slopeHit =m= (q2 - q1)/(p2 - p1)
    bHit =b= p1 - (slopeHit*q1)

    #(x - u)^2 + (y - v)^2 = r^2
    #x^2 - 2ux + u^2 + y^2 - 2vy + v^2 - r^2 = 0
    #x**2 + ((slopeHit * x) + bHit)**2) - 2ux - 2v(slopeHit * x) + bHit) +(u^2 + v^2 - r^2) = 0      #y = (slopeHit * x) + bHit

    '''A = (slopeHit**2 + 1)
    B = 2*((slopeHit*bHit) - (slopeHit*center[1]) - center[0])
    C = ((center[1] ** 2) - (radius ** 2) + (center[0] ** 2) - (2 * bHit * center[1]) + (bHit ** 2))
    print('Coefficient Circle Terms: ',A,B,C)
    intcX1 = ((-B + (math.sqrt((B**2) - (4*A*C)))) / (2*A)) 
    intcY1 = slopeHit * intcX1 + bHit
    intcX2 = ((-B - (math.sqrt((B**2) - (4*A*C)))) / (2*A))
    intcY2 = slopeHit * intcX2 + bHit

    X1 = (((-b*m)+h+(k*m)) / ((m**2)+1)) - math.sqrt((-(b**2) - (2*b*h*m) + (2*b*k) - ((h**2) * (m**2)) + (2*h*k*m) - (k**2) + ((m**2) * (r**2)) + r**2) / ((m**2 + 1)**2))
    Y1 = b + (m*X1)
    print('X1/Y1:',X1, Y1)
    print(((4*b) + (4*h*m) - (4*(k**2)) + (m**2) + (4*(r**2)) + (2*h) + m))
    X2 = 0.5*(math.sqrt(abs((4*b) + (4*h*m) - (4*(k**2)) + (m**2) + (4*(r**2)) + (2*h) + m)))
    Y2 = 0.5*(math.sqrt(abs((4*b) - (4*(h**2)) - (4*k) + (4*(r**2)) + 1 + (2*k) - 1)))
    print('X2/Y2:',X2, Y2)
    X3 = (0.5*(2*h + m)) - (0.5 * (math.sqrt(abs(4*b + 4*h*m - 4*k + m**2 + 1))))
    Y3 = (0.5*(2*k - 1)) - (0.5 * (math.sqrt(abs(4*b - 4*(h**2) + 8*h*X3 - 4*k + 4*m*X3 - 4*(X3**2) + 1))))
    print('X3/Y3:',X3, Y3)'''

    d = Vector(p2,q2) - Vector(p1,q1)
    #d = Vector(p1,q1) - Vector(p2,q2)
    f = Vector(p1,q1) - Vector(center)

    a = float(d.dot(d))
    b = float(2 * f.dot(d))
    c = float(f.dot(f) - r*r)

    discriminant = b*b-4*a*c
    print('discriminant: ', discriminant)
    discriminant = math.sqrt(discriminant)
    print('square discriminant: ', discriminant)

    t1 = (-b - discriminant)/(2*a)
    t2 = (-b + discriminant)/(2*a)
    print('the ts: ', t1, t2)
    pt1 = Vector(((p2 - p1) * t1) + p1, ((q2 - q1) * t1) + q1)
    pt2 = Vector(((p2 - p1) * t2) + p1, ((q2 - q1) * t2) + q1)

    #This parabola doesn't fit the trajectory, just the three points
    trajCoefMatr = matrix([[orgnlPt[0]**2, orgnlPt[0], 1],
                           [midPt[0]**2,   midPt[0],   1],
                           [ghostPt[0]**2, ghostPt[0], 1]])
    trajY = matrix([[orgnlPt[1]],
                    [midPt[1]],
                    [ghostPt[1]]])
    print('matrices: ', trajCoefMatr, trajY)
    print('inverse: ', trajCoefMatr.I)
    print('inverse:2', trajCoefMatr.getI())
    trajSolution = (trajCoefMatr.I) * trajY
    trajCoef = trajSolution.tolist()

    a = trajCoef[0][0]
    b = trajCoef[1][0]
    c = trajCoef[2][0]
    print('trajectory quadratic: ' + str(a) + 'x^2 + ' +str(b)+ 'x + '+str(c))
    
    '''for x in range(0,800):
        y = (a*(x**2)) + (b*x) + c
        with self.canvas:
            Color(0,0,1,1)
            Ellipse(size=(2,2), pos=(x-1, y-1))'''
    
    hitMid = [((border[0][0] + border[1][0])/2), ((border[0][1] + border[1][1])/2)]
    print('Hit Points: ' + str(border[0]) +', '+str(border[1])+', '+str(hitMid))
    hitCoefMatr = matrix([[border[0][0]**2, border[0][0], 1],
                          [border[1][0]**2, border[1][0], 1],
                          [hitMid[0]**2, hitMid[0], 1]])
    hitY = matrix([[border[0][1]],
                   [border[1][1]],
                   [hitMid[1]]])
    hitSolution = (hitCoefMatr.I) * hitY
    
    hitCoef = hitSolution.tolist()

    A = hitCoef[0][0]
    B = hitCoef[1][0]
    C = hitCoef[2][0]
    print('Hit Quadratic: ' + str(A) + 'x^2 + ' +str(B)+ 'x + '+str(C))

    d = A-a
    e = B-b
    f = C-c

    d = a-A
    e = b-B
    f = c-C

    
    x1 = ((-e) + (math.sqrt((e**2) - (4 * d * f)) / (2 * d)))
    x2 = ((-e) - (math.sqrt((e**2) - (4 * d * f)) / (2 * d)))
    y1 = (a * (x1 ** 2)) + (b * x1) + c
    y2 = (A * (x2 ** 2)) + (B * x2) + C

    y1 = ((-e) + (math.sqrt((e**2) - (4 * d * f)) / (2 * d)))
    y2 = ((-e) - (math.sqrt((e**2) - (4 * d * f)) / (2 * d)))
    x1 = (a * (y1 ** 2)) + (b * y1) + c
    x2 = (A * (y2 ** 2)) + (B * y2) + C

    impPoints = [Vector(x1,y1), Vector(x2,y2)]
    print('impact points: ', impPoints)
    #derivative of orgnlPt on the curve defined by orgnlPt, midPt, newPt
    #curve = y = ax**2 + bx + c
    #derivative = dy/dx = (2*a)*x + b
    #ds = sqrt(1+(dy/dx)**2
    #x = orgnlPt[0] <-> x = x1(x2)
    #NO ARC LENGTHS, FUCKING IMPOSSIBLE
    #S(length of arc) = integrate.quad(sqrt(1+(((2*a)*{orgnlPt[0]/x1/x2}) + b)**2), orgnlPt[0], {x1/x2})

    '''
    Okay so now we have:
    x1, y1 = first point of intersection between the two lines
    x2, y2 = second point of intersection between the two lines
    orgnlPt = the point on the intersecting curve outside of the target widget
    ghostPt = the point on the intersecting curve inside of the target widget
    midPt = the point on the intersecting curve that is one/half the next steps velocity and rotation

    1. From this we can get the line in between orgnlPt and ghostPt,
    2. We can find the distance between the mid point of (orgnlPt, ghostPt) ogMid and midPt on the curve
        2a. midDist = Vector(sMid) - Vector(midPt)
    3. We can use this distance to drawn a line from x1,y1 through (orgnlPt, ghostPt) and
       x2,y2 through (orgnlPt, ghostPt)
        3a. ptOne = x1,y1 - Vector(dist), ptTwo = x2,y2 - Vector(dist)
    4. This should leave us with one (or two, but likely one) point one the line (orgnlPt, ghostPt)
    5. We can compute the porpotional distance between orgnlPt and ptOne/ptTwo with respect to
       the distance between orgnlPt and ghostPt
    6. this porportional distance should match the amount of movement needed by the widget/point
       in order to "hit" the target
    '''

    sLine = Vector(orgnlPt, ghostPt)
    sMid = [(sLine[0][0] + sLine[1][0]) /2,(sLine[0][1] + sLine[1][1]) /2] #sMid = 1,2 cMid = 5,5, midDist = 4,3
    sQuarter = [(sLine[0][0] + sMid[0]) /2, (sLine[0][1]+ sMid[1]) /2]
    midDist = [midPt[0] - sMid[0], midPt[1] - sMid[1]]

    distPt1 = Vector(pt1) - Vector(midDist)
    distPt2 = Vector(pt2) - Vector(midDist)

    sPt1 = line_intersect([orgnlPt, ghostPt], [pt1, distPt1])
    sPt2 = line_intersect([orgnlPt, ghostPt], [pt2, distPt2])
    print('distance points: ', sPt1, sPt2)

    normalDist = math.sqrt(((orgnlPt[0] - ghostPt[0]) ** 2) + ((orgnlPt[1] - ghostPt[1]) ** 2))
    travelDist = math.sqrt(((orgnlPt[0] - sPt1[0]) ** 2) + ((orgnlPt[1] - sPt1[1]) ** 2))
    print('distances: ' + str(normalDist) + ', '+str(travelDist))
    travelPerc = travelDist / normalDist
    print('travelPer: ' + str(travelPerc))
    travelPoint = Vector((((orgnlPt[0] - rotPt[0]) * math.cos(math.radians(rotSpd*travelPerc)))
                          - ((orgnlPt[1] - rotPt[1]) * math.sin(math.radians(rotSpd*travelPerc)))),
                         (((orgnlPt[0] - rotPt[0]) * math.sin(math.radians(rotSpd*travelPerc)))
                          + ((orgnlPt[1] - rotPt[1]) * math.cos(math.radians(rotSpd*travelPerc)))))
    travelPoint = travelPoint + rotPt
    print('travel Point = ' + str(travelPoint))
    
    movementPts = []
    for xy in impPoints:
        x,y = xy
        oppPoint = Vector(x - midDist[0], y - midDist[1])
        percentLine = (xy),(oppPoint)
        percentPoint = line_intersect(((xy),(oppPoint)), (sLine))
        #if point_on_lines(percentPoint, [sLine]):
        movementPts.append(percentPoint)
    print('mvPts: ' + str(movementPts))
    if len(movementPts) == 2:
        if math.sqrt(((movementPts[0][0] - orgnlPt[0]) ** 2) + ((movementPts[0][1] - orgnlPt[0]) ** 2)) < math.sqrt(((movementPts[1][0] - orgnlPt[0]) ** 2) + ((movementPts[1][1] - orgnlPt[1]) ** 2)):
            movePt = movementPts[0]
        else:
            movePt = movementPts[1]
    else:
        movePt = movementPts[0]

    segLength = math.sqrt(((ghostPt[0] - orgnlPt[0]) ** 2) + ((ghostPt[1] - orgnlPt[1]) ** 2))
    moveLength = math.sqrt(((movePt[0] - orgnlPt[0]) ** 2) + ((movePt[1] - orgnlPt[1]) ** 2))
    print(moveLength, segLength)
    moveRatio = moveLength / segLength

    return moveRatio, [orgnlPt, ghostPt, midPt, sMid, border[0], border[1], hitMid, Vector(x1,y1), Vector(x2,y2), Vector(movePt), q1Pt, q3Pt, [center,radius], [pt1, pt2], [sPt1, sPt2], travelPoint, distPt1, sQuarter, [a,b,c]]
