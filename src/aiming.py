import math

def aiming_function(vx, vy, normal_astangle):

    """Lester's Accuracy House of Horrors"""

    vectang = math.degrees(math.atan2(vy,vx))

    # print(vectang2, vectang, vectang2-vectang)

    sidea = math.sqrt(vx ** 2 + vy ** 2)
    sideb = 800

    # Find angle B
    tsangle = normal_astangle - 90  # This is the ship relative to the asteroid, don't change this if you're looking at it backwards.
    if tsangle <= 0:
        tsangle += 360

    orientation_ast = (tsangle - vectang)  # Vectang: asteroid travel angle, Trangle: True asteroid angle to ship

    if orientation_ast >= 180:
        orientation_ast = -360 + orientation_ast  # (-1*orientation_ast)+180 #orientation_ast - 360
    elif orientation_ast <= -180:
        orientation_ast = 360 + orientation_ast

    ant_angle = -70 * math.degrees(math.asin(math.sin(math.radians(orientation_ast)) * sidea / sideb))

    """This next line of code can be used to disable anticipatory aiming"""
    #self.ant_angle = 0

    #print(f"Asteroid Travel Angle            {vectang}")
    #print(f"Asteroid to Ship Angle (tsangle) {tsangle}")
    #print(f"Orientation of Asteroid          {orientation_ast}")
    #print(f"Anticipatory Angle               {self.ant_angle}")

    return ant_angle