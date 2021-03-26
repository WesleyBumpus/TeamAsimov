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

        import random
        from deap import base
        from deap import creator
        from deap import tools

        import skfuzzy as fuzz
        import skfuzzy.control as ctrl
        import numpy

        asteroid_num = ctrl.Antecedent(numpy.arange(0, 61, 1), 'asteroid_num')
        names = ['low', 'avg', 'high']
        asteroid_num.automf(names=names)
        TR = ctrl.Consequent(numpy.arange(-91, 271, 1), 'TR')
        TR.automf(names=names)
        tr_rule0 = ctrl.Rule(antecedent=(asteroid_num['low']), consequent=TR['low'], label='tr_rule_0')
        tr_rule1 = ctrl.Rule(antecedent=(asteroid_num['avg']), consequent=TR['avg'], label='tr_rule_1')
        tr_rule2 = ctrl.Rule(antecedent=(asteroid_num['high']), consequent=TR['high'], label='tr_rule_2')
        tr_system = ctrl.ControlSystem(rules=[tr_rule0, tr_rule1, tr_rule2])
        tr_sim = ctrl.ControlSystemSimulation(tr_system)

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
        import numpy
        if len(input_data['asteroids']) > 3:
            asteroid_num = ctrl.Antecedent(numpy.arange(0, 61, 1), 'asteroid_num')
            names = ['low', 'avg', 'high']
            asteroid_num.automf(names=names)
            TR = ctrl.Consequent(numpy.arange(-91, 271, 1), 'TR')
            TR.automf(names=names)
            tr_rule0 = ctrl.Rule(antecedent=(asteroid_num['low']), consequent=TR['low'], label='tr_rule_0')
            tr_rule1 = ctrl.Rule(antecedent=(asteroid_num['avg']), consequent=TR['avg'], label='tr_rule_1')
            tr_rule2 = ctrl.Rule(antecedent=(asteroid_num['high']), consequent=TR['high'], label='tr_rule_2')
            tr_system = ctrl.ControlSystem(rules=[tr_rule0, tr_rule1, tr_rule2])
            tr_sim = ctrl.ControlSystemSimulation(tr_system)
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
            tr_sim.input['asteroid_num'] = len(input_data['asteroids'])
            tr_sim.compute()
            ship.turn_rate = tr_sim.output['TR']
        else:
            ship.shoot()
            ship.turn_rate = 130
