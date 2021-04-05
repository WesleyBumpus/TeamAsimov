import math

def aiming_function(vx, vy, normal_astangle):

    """Lester's Accuracy House of Horrors"""

    vectang = math.degrees(math.atan2(vy,vx)) #calculates asteroid travel angle

    # print(vectang2, vectang, vectang2-vectang)

    sidea = math.sqrt(vx ** 2 + vy ** 2) #asteroid speed
    sideb = 800 #800 is Bullet speed

    # Find angle B
    tsangle = normal_astangle - 90  # This is the ship relative to the asteroid, don't change this if you're looking at it backwards.
    if tsangle <= 0:
        tsangle += 360

    orientation_ast = (tsangle - vectang)  # Vectang: asteroid travel angle, Trangle: True asteroid angle to ship

    if orientation_ast >= 180:
        orientation_ast = -360 + orientation_ast
    elif orientation_ast <= -180:
        orientation_ast = 360 + orientation_ast

    ant_angle = -70 * math.degrees(math.asin(math.sin(math.radians(orientation_ast)) * sidea / sideb)) # Calculates anticipatory aiming.

    """This next line of code can be used to disable anticipatory aiming"""
    #self.ant_angle = 0

    return ant_angle