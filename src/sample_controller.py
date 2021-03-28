from typing import Tuple, Dict, Any

from fuzzy_asteroids.fuzzy_controller import ControllerBase, SpaceShip


class FuzzyController(ControllerBase):
    """
    Class to be used by UC Fuzzy Challenge competitors to create a fuzzy logic controller
    for the Asteroid Smasher game.

    Note: Your fuzzy controller class can be called anything, but must inherit from the
    the ``ControllerBase`` class (imported above)

    Users must define the following:
    1. __init__()
    2. actions(self, ship: SpaceShip, input_data: Dict[str, Tuple])

    By defining these interfaces, this class will work correctly
    """

    def __init__(self):
        """
        Create your fuzzy logic controllers and other objects here
        """
        import skfuzzy.control as ctrl
        import numpy
        self.hi=30
        """
        Checking the asteroid angle relative to the ship
        """
        def r_angle(opposite, hypotenuse, abovebelow, leftright):
            import math
            if abovebelow > 0:
                s_rangle = -1 * (math.degrees(math.asin(opposite/hypotenuse)))
            elif abovebelow < 0 and leftright < 0:
                s_rangle = 180+(math.degrees(math.asin(opposite/hypotenuse)))
            elif abovebelow < 0 and leftright > 0:
                s_rangle = -180+(math.degrees(math.asin(opposite/hypotenuse)))
            return s_rangle
        self.rangle=r_angle
        """
        Defensively shooting at an approaching asteroid, 
        I think for defensive shooting we could have it intentionally over shoot by turning too fast 
        as to simulate leading the shot
        """

        """
        Chaffe Clearing Rotation Controller
        """
        asteroid_num = ctrl.Antecedent(numpy.arange(0, 61, 1), 'asteroid_num')
        names = ['low', 'avg', 'high']
        asteroid_num.automf(names=names)
        TR = ctrl.Consequent(numpy.arange(-91, 271, 1), 'TR')
        TR.automf(names=names)
        tr_rule0 = ctrl.Rule(antecedent=(asteroid_num['low']), consequent=TR['low'], label='tr_rule_0')
        tr_rule1 = ctrl.Rule(antecedent=(asteroid_num['avg']), consequent=TR['avg'], label='tr_rule_1')
        tr_rule2 = ctrl.Rule(antecedent=(asteroid_num['high']), consequent=TR['high'], label='tr_rule_2')
        tr_system = ctrl.ControlSystem(rules=[tr_rule0, tr_rule1, tr_rule2])
        self.tr_sim = ctrl.ControlSystemSimulation(tr_system)

    def actions(self, ship: SpaceShip, input_data: Dict[str, Tuple]) -> None:

        """
        Compute control actions of the ship. Perform all command actions via the ``ship``
        argument. This class acts as an intermediary between the controller and the environment.

        The environment looks for this function when calculating control actions for the Ship sprite.

        :param ship: Object to use when controlling the SpaceShip
        :param input_data: Input data which describes the current state of the environment
        """
        import fuzzy_asteroids
        import skfuzzy.control as ctrl
        import math
        import numpy
        astnum=len(input_data['asteroids'])
        distance=numpy.zeros(astnum)
        shortest_distance=1000
        closest_asteroid=0
        """Below it goes through the asteroids, 
        records their distance, 
        and sets the shortest distance and closest asteroid"""
        for n in range (0,astnum):
            distance[n]=(((input_data['asteroids'][n]['position'][0])-ship.center_x)**2+((input_data['asteroids'][n]['position'][1])-ship.center_y)**2)**0.5
            if distance[n]<shortest_distance:
                shortest_distance=distance[n]
                closest_asteroid=n
        abovebelow = input_data['asteroids'][closest_asteroid]['position'][1] - ship.center_y
        leftright = input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x
        opposite=(input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x)
        hypotenuse=shortest_distance
        s_rangle=self.rangle(opposite, hypotenuse, abovebelow, leftright)
        """
        s_rangle is the angle relative to the ship necessary for the ship to point at the closest asteroid
        """
        """ Positive if above, negative if below"""
        """ negative if left, positive if right"""
        print("---")
        print(ship.angle)
        print(s_rangle)
        orientation=abs(ship.angle-s_rangle)
        """Evasive Manuevers, I think we could expand this to considering the closest three 
        asteroids and fuzzily deciding which direction to flee in
        
        for cases where an asteroid is perpindicularly approaching it needs to be able to distinguish left and right anf
         behave accordingly """
        if shortest_distance<60:
            if orientation>100:
                ship.thrust=ship.thrust_range[1]
            elif orientation>70 and orientation<110 and shortest_distance<45:
                ship.thrust = 0
                ship.turn_rate=180
            else:
                ship.thrust = ship.thrust_range[0]
                ship.shoot()


        elif len(input_data['asteroids']) > 3:

            """
            ship.center_x
            ship.center_y
            ship.velocity
            ship.angle
            print(ship.angle)
            """
            """
            print(input_data['asteroids'][0]['position'][0])
            print(input_data['asteroids'][0]['position'][1])
            """
            """
    
            print(ship)
            ship.turn_rate = 160.0
    
            ship.thrust = ship.thrust_range[0]
            """

            ship.shoot()
            self.tr_sim.input['asteroid_num'] = len(input_data['asteroids'])
            self.tr_sim.compute()
            ship.turn_rate = self.tr_sim.output['TR']
            """We'll need to use orientation to teach it to break since velocity can be measured using r_angle"""

        else:
            ship.shoot()
            ship.turn_rate = 40

