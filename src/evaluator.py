from fuzzy_asteroids.fuzzy_asteroids import TrainerEnvironment
from typing import Tuple, Dict, Any
from aiming import aiming_function
import skfuzzy as fuzz
import skfuzzy.control as ctrl
from fuzzy_asteroids.fuzzy_controller import ControllerBase, SpaceShip
import numpy
import math

# the goal ('fitness') function to be maximized
def evalscore(individual):
    settings = {
        "graphics_on": True,
        "sound_on": False,
        # "frequency": 60,
        "real_time_multiplier": 200,
        # "lives": 3,
        # "prints": True,
        "allow_key_presses": False
    }

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
            print('run initiated')
            individualbest = [599, 486, 157, 104, 243, 59, 522, 521, 83, 872, 191, 71, 862, 215, 439, 274, 719, 960, 700, 664,
                          74, 624, 651, 176, 547, 747, 251, 168, 474, 389, 277, 948, 656, 705, 571, 225, 434, 979, 466, 787,
                          795, 291, 235, 615]

            """
            Gene Constants
            """
            self.roe_zone = individual[0] / 1000 * 500
            # Maximum Distance for Multitasking, Default: 240
            self.fuzzy_roe=(individual[1]/1000)*self.roe_zone
            # Minimum Distance for Fuzzy application, Default: 120
            self.edgeclear=individual[2]/1000*275

            self.wack_coef = individualbest[38] / 1000 * 200
            # Controls Rate of Fire, considering distance. 10 is 1 per target, Default: 100
            self.brake_speed_power = individualbest[39] / 1000 * 500
            # Controls Speed at which the craft will not exceed. Variable by size. Default: 250, lower is faster.
            self.SAD_base = individualbest[40] / 1000 * 100
            # S&D closeness to target, base. Default: 50
            self.SAD_size_adjust = individualbest[41] / 1000 * 100
            # S&D closeness to target, varies with size. Default: 62
            self.evasive_base = individualbest[42] / 1000 * 100
            # Closeness where evasive behavior is triggered. Default: 45
            self.evasive_size_adjust = individualbest[43] / 1000 * 50
            # Closeness to where evasive behavior is triggered. Variable by size. Default: 20
            self.wack = 0
            """
            Checking the asteroid angle relative to the ship
            """

            def r_angle(opposite, hypotenuse, abovebelow, leftright):
                import math
                if abovebelow > 0:
                    angle = -1 * (math.degrees(math.asin(opposite / hypotenuse)))
                elif abovebelow < 0 and leftright < 0:
                    angle = 180 + (math.degrees(math.asin(opposite / hypotenuse)))
                elif abovebelow < 0 and leftright > 0:
                    angle = -180 + (math.degrees(math.asin(opposite / hypotenuse)))
                else:
                    angle = 0
                return angle

            self.rangle = r_angle
            """
            Defensively shooting at an approaching asteroid, 
            I think for defensive shooting we could have it intentionally over shoot by turning too fast 
            as to simulate leading the shot
            """
            """
            Angle Normalizer if the difference is greater than 180 or less
            """

            def norm(angle):
                if angle > 0:
                    new_angle = angle
                elif angle < 0:
                    new_angle = 360 + angle
                else:
                    new_angle = 0
                return new_angle

            self.norm = norm

            """
            Function That Tells You Whether Rotating Left or Right to the asteroid is faster
            0 is left, 1 is right
            use normalized angles
            """

            def leftrightcheck(shipangle, astangle):
                diff = shipangle - astangle + self.ant_angle
                absdiff = abs(diff)
                if absdiff < 180 and diff > 0:
                    leftright = 1
                elif absdiff < 180 and diff < 0:
                    leftright = 0
                elif absdiff > 180 and diff > 0:
                    leftright = 0
                elif absdiff > 180 and diff < 0:
                    leftright = 1
                else:
                    leftright = 0
                    print('problem in left right checker')
                return leftright

            self.leftright = leftrightcheck

            """
            Asteroid Selecting Fuzzy System
            For simplicity of code (Not necessarily Compactness I'm going to code one fuzzy system for each size class)
            Finds Favorability 
            """
            # For Size 1
            f_orientation_size1 = ctrl.Antecedent(numpy.arange(-91, 271, 1), 'f_orientation_size1')
            f_orientation_size1['In Sights'] = fuzz.trimf(f_orientation_size1.universe, [-15, 0, 15])
            f_orientation_size1['Close'] = fuzz.trimf(f_orientation_size1.universe, [15, 45, 75])
            f_orientation_size1['Far'] = fuzz.trimf(f_orientation_size1.universe, [75, 180, 285])

            # shortest_distance < 50 + (12 * clast_size)
            names=['Imminent','Close','Far']
            f_hypotenuse_size1 = ctrl.Antecedent(numpy.arange(0,self.roe_zone+1,1), 'f_hypotenuse_size1')
            f_hypotenuse_size1.automf(names=names)
            """"
            f_hypotenuse_size1['Imminent'] = fuzz.trimf(f_hypotenuse_size1.universe, [-80, 0, 80])
            f_hypotenuse_size1['Close'] = fuzz.trimf(f_hypotenuse_size1.universe, [80, 140, 200])
            f_hypotenuse_size1['Far'] = fuzz.trimf(f_hypotenuse_size1.universe, [140, 200, 260])
            """
            # Target_F
            Target_F1 = ctrl.Consequent(numpy.arange(-26, 126, 1), 'Target_F1')
            Target_F1['Very Low'] = fuzz.trimf(Target_F1.universe, [-25, 0, 25])
            Target_F1['Low'] = fuzz.trimf(Target_F1.universe, [0, 25, 50])
            Target_F1['Medium'] = fuzz.trimf(Target_F1.universe, [25, 50, 75])
            Target_F1['High'] = fuzz.trimf(Target_F1.universe, [50, 75, 100])
            Target_F1['Very High'] = fuzz.trimf(Target_F1.universe, [75, 100, 125])

            Target_F1_rule1 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Imminent'] & f_orientation_size1['In Sights']),
                                        consequent=Target_F1['Very High'], label='Target_F1_rule1')

            Target_F1_rule2 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Close'] & f_orientation_size1['In Sights']),
                                        consequent=Target_F1['High'], label='Target_F1_rule2')

            Target_F1_rule3 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Far'] & f_orientation_size1['In Sights']),
                                        consequent=Target_F1['Medium'], label='Target_F1_rule3')

            Target_F1_rule4 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Imminent'] & f_orientation_size1['Close']),
                                        consequent=Target_F1['Very High'], label='Target_F1_rule4')

            Target_F1_rule5 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Close'] & f_orientation_size1['Close']),
                                        consequent=Target_F1['High'], label='Target_F1_rule5')

            Target_F1_rule6 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Far'] & f_orientation_size1['Close']),
                                        consequent=Target_F1['Medium'], label='Target_F1_rule6')

            Target_F1_rule7 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Imminent'] & f_orientation_size1['Far']),
                                        consequent=Target_F1['Very High'], label='Target_F1_rule7')

            Target_F1_rule8 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Close'] & f_orientation_size1['Far']),
                                        consequent=Target_F1['High'], label='Target_F1_rule8')

            Target_F1_rule9 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Far'] & f_orientation_size1['Far']),
                                        consequent=Target_F1['Medium'], label='Target_F1_rule9')

            Target_F1_system = ctrl.ControlSystem(rules=[Target_F1_rule1, Target_F1_rule2, Target_F1_rule3, Target_F1_rule4,
                                                         Target_F1_rule5, Target_F1_rule6, Target_F1_rule7, Target_F1_rule8,
                                                         Target_F1_rule9])
            self.Target_F1_sim = ctrl.ControlSystemSimulation(Target_F1_system)
            """
            Target_F1_sim.input['f_orientation_size1'] = 45
            Target_F1_sim.input['f_hypotenuse_size1'] = 100
            Target_F1_sim.compute()
            Favorability = Target_F1_sim.output['Target_F1']
            """
            # For Size 2
            f_orientation_size2 = ctrl.Antecedent(numpy.arange(-91, 271, 1), 'f_orientation_size2')
            f_orientation_size2['In Sights'] = fuzz.trimf(f_orientation_size2.universe, [-15, 0, 15])
            f_orientation_size2['Close'] = fuzz.trimf(f_orientation_size2.universe, [15, 45, 75])
            f_orientation_size2['Far'] = fuzz.trimf(f_orientation_size2.universe, [75, 180, 285])
            # shortest_distance < 50 + (12 * clast_size)
            f_hypotenuse_size2 = ctrl.Antecedent(numpy.arange(0, self.roe_zone + 1, 1), 'f_hypotenuse_size2')
            f_hypotenuse_size2.automf(names=names)
            """
            f_hypotenuse_size2['Imminent'] = fuzz.trimf(f_hypotenuse_size2.universe, [-80, 0, 80])
            f_hypotenuse_size2['Close'] = fuzz.trimf(f_hypotenuse_size2.universe, [80, 140, 200])
            f_hypotenuse_size2['Far'] = fuzz.trimf(f_hypotenuse_size2.universe, [140, 200, 260])
            """
            # Target_F
            Target_F2 = ctrl.Consequent(numpy.arange(-26, 126, 1), 'Target_F2')
            Target_F2['Very Low'] = fuzz.trimf(Target_F2.universe, [-25, 0, 25])
            Target_F2['Low'] = fuzz.trimf(Target_F2.universe, [0, 25, 50])
            Target_F2['Medium'] = fuzz.trimf(Target_F2.universe, [25, 50, 75])
            Target_F2['High'] = fuzz.trimf(Target_F2.universe, [50, 75, 100])
            Target_F2['Very High'] = fuzz.trimf(Target_F2.universe, [75, 100, 125])

            Target_F2_rule1 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Imminent'] & f_orientation_size2['In Sights']),
                                        consequent=Target_F2['Very High'], label='Target_F2_rule1')

            Target_F2_rule2 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Close'] & f_orientation_size2['In Sights']),
                                        consequent=Target_F2['High'], label='Target_F2_rule2')

            Target_F2_rule3 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Far'] & f_orientation_size2['In Sights']),
                                        consequent=Target_F2['Medium'], label='Target_F2_rule3')

            Target_F2_rule4 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Imminent'] & f_orientation_size2['Close']),
                                        consequent=Target_F2['Very High'], label='Target_F2_rule4')

            Target_F2_rule5 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Close'] & f_orientation_size2['Close']),
                                        consequent=Target_F2['High'], label='Target_F2_rule5')

            Target_F2_rule6 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Far'] & f_orientation_size2['Close']),
                                        consequent=Target_F2['Medium'], label='Target_F2_rule6')

            Target_F2_rule7 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Imminent'] & f_orientation_size2['Far']),
                                        consequent=Target_F2['Very High'], label='Target_F2_rule7')

            Target_F2_rule8 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Close'] & f_orientation_size2['Far']),
                                        consequent=Target_F2['High'], label='Target_F2_rule8')

            Target_F2_rule9 = ctrl.Rule(antecedent=(f_hypotenuse_size2['Far'] & f_orientation_size2['Far']),
                                        consequent=Target_F2['Medium'], label='Target_F2_rule9')

            Target_F2_system = ctrl.ControlSystem(rules=[Target_F2_rule1, Target_F2_rule2, Target_F2_rule3, Target_F2_rule4,
                                                         Target_F2_rule5, Target_F2_rule6, Target_F2_rule7, Target_F2_rule8,
                                                         Target_F2_rule9])
            self.Target_F2_sim = ctrl.ControlSystemSimulation(Target_F2_system)

            # For Size 3
            f_orientation_size3 = ctrl.Antecedent(numpy.arange(-91, 271, 1), 'f_orientation_size3')
            f_orientation_size3['In Sights'] = fuzz.trimf(f_orientation_size3.universe, [-15, 0, 15])
            f_orientation_size3['Close'] = fuzz.trimf(f_orientation_size3.universe, [15, 45, 75])
            f_orientation_size3['Far'] = fuzz.trimf(f_orientation_size3.universe, [75, 180, 285])
            # shortest_distance < 50 + (12 * clast_size) We may wanna change the hypotenuse membership functions
            f_hypotenuse_size3 = ctrl.Antecedent(numpy.arange(0, self.roe_zone + 1, 1), 'f_hypotenuse_size3')
            f_hypotenuse_size3.automf(names=names)
            """
            f_hypotenuse_size3['Imminent'] = fuzz.trimf(f_hypotenuse_size3.universe, [-80, 0, 80])
            f_hypotenuse_size3['Close'] = fuzz.trimf(f_hypotenuse_size3.universe, [80, 140, 200])
            f_hypotenuse_size3['Far'] = fuzz.trimf(f_hypotenuse_size3.universe, [140, 200, 260])
            """
            # Target_F
            Target_F3 = ctrl.Consequent(numpy.arange(-26, 126, 1), 'Target_F3')
            Target_F3['Very Low'] = fuzz.trimf(Target_F3.universe, [-25, 0, 25])
            Target_F3['Low'] = fuzz.trimf(Target_F3.universe, [0, 25, 50])
            Target_F3['Medium'] = fuzz.trimf(Target_F3.universe, [25, 50, 75])
            Target_F3['High'] = fuzz.trimf(Target_F3.universe, [50, 75, 100])
            Target_F3['Very High'] = fuzz.trimf(Target_F3.universe, [75, 100, 125])

            Target_F3_rule1 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Imminent'] & f_orientation_size3['In Sights']),
                                        consequent=Target_F3['Very High'], label='Target_F3_rule1')

            Target_F3_rule2 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Close'] & f_orientation_size3['In Sights']),
                                        consequent=Target_F3['High'], label='Target_F3_rule2')

            Target_F3_rule3 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Far'] & f_orientation_size3['In Sights']),
                                        consequent=Target_F3['Medium'], label='Target_F3_rule3')

            Target_F3_rule4 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Imminent'] & f_orientation_size3['Close']),
                                        consequent=Target_F3['Very High'], label='Target_F3_rule4')

            Target_F3_rule5 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Close'] & f_orientation_size3['Close']),
                                        consequent=Target_F3['High'], label='Target_F3_rule5')

            Target_F3_rule6 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Far'] & f_orientation_size3['Close']),
                                        consequent=Target_F3['Medium'], label='Target_F3_rule6')

            Target_F3_rule7 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Imminent'] & f_orientation_size3['Far']),
                                        consequent=Target_F3['Very High'], label='Target_F3_rule7')

            Target_F3_rule8 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Close'] & f_orientation_size3['Far']),
                                        consequent=Target_F3['High'], label='Target_F3_rule8')

            Target_F3_rule9 = ctrl.Rule(antecedent=(f_hypotenuse_size3['Far'] & f_orientation_size3['Far']),
                                        consequent=Target_F3['Medium'], label='Target_F3_rule9')

            Target_F3_system = ctrl.ControlSystem(rules=[Target_F3_rule1, Target_F3_rule2, Target_F3_rule3, Target_F3_rule4,
                                                         Target_F3_rule5, Target_F3_rule6, Target_F3_rule7, Target_F3_rule8,
                                                         Target_F3_rule9])
            self.Target_F3_sim = ctrl.ControlSystemSimulation(Target_F3_system)

            # For Size 4
            f_orientation_size4 = ctrl.Antecedent(numpy.arange(-91, 271, 1), 'f_orientation_size4')
            f_orientation_size4['In Sights'] = fuzz.trimf(f_orientation_size4.universe, [-15, 0, 15])
            f_orientation_size4['Close'] = fuzz.trimf(f_orientation_size4.universe, [15, 45, 75])
            f_orientation_size4['Far'] = fuzz.trimf(f_orientation_size4.universe, [75, 180, 285])
            # shortest_distance < 50 + (12 * clast_size) We may wanna change the hypotenuse membership functions
            f_hypotenuse_size4 = ctrl.Antecedent(numpy.arange(0, self.roe_zone + 1, 1), 'f_hypotenuse_size4')
            f_hypotenuse_size4.automf(names=names)
            """
            f_hypotenuse_size4['Imminent'] = fuzz.trimf(f_hypotenuse_size4.universe, [-80, 0, 80])
            f_hypotenuse_size4['Close'] = fuzz.trimf(f_hypotenuse_size4.universe, [80, 140, 200])
            f_hypotenuse_size4['Far'] = fuzz.trimf(f_hypotenuse_size4.universe, [140, 200, 260])
            """
            # Target_F
            Target_F4 = ctrl.Consequent(numpy.arange(-26, 126, 1), 'Target_F4')
            Target_F4['Very Low'] = fuzz.trimf(Target_F4.universe, [-25, 0, 25])
            Target_F4['Low'] = fuzz.trimf(Target_F4.universe, [0, 25, 50])
            Target_F4['Medium'] = fuzz.trimf(Target_F4.universe, [25, 50, 75])
            Target_F4['High'] = fuzz.trimf(Target_F4.universe, [50, 75, 100])
            Target_F4['Very High'] = fuzz.trimf(Target_F4.universe, [75, 100, 125])

            Target_F4_rule1 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Imminent'] & f_orientation_size4['In Sights']),
                                        consequent=Target_F4['Very High'], label='Target_F4_rule1')

            Target_F4_rule2 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Close'] & f_orientation_size4['In Sights']),
                                        consequent=Target_F4['High'], label='Target_F4_rule2')

            Target_F4_rule3 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Far'] & f_orientation_size4['In Sights']),
                                        consequent=Target_F4['Very Low'], label='Target_F4_rule3')

            Target_F4_rule4 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Imminent'] & f_orientation_size4['Close']),
                                        consequent=Target_F4['High'], label='Target_F4_rule4')

            Target_F4_rule5 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Close'] & f_orientation_size4['Close']),
                                        consequent=Target_F4['Medium'], label='Target_F4_rule5')

            Target_F4_rule6 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Far'] & f_orientation_size4['Close']),
                                        consequent=Target_F4['Very Low'], label='Target_F4_rule6')

            Target_F4_rule7 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Imminent'] & f_orientation_size4['Far']),
                                        consequent=Target_F4['High'], label='Target_F4_rule7')

            Target_F4_rule8 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Close'] & f_orientation_size4['Far']),
                                        consequent=Target_F4['Low'], label='Target_F4_rule8')

            Target_F4_rule9 = ctrl.Rule(antecedent=(f_hypotenuse_size4['Far'] & f_orientation_size4['Far']),
                                        consequent=Target_F4['Very Low'], label='Target_F4_rule9')

            Target_F4_system = ctrl.ControlSystem(rules=[Target_F4_rule1, Target_F4_rule2, Target_F4_rule3, Target_F4_rule4,
                                                         Target_F4_rule5, Target_F4_rule6, Target_F4_rule7, Target_F4_rule8,
                                                         Target_F4_rule9])
            self.Target_F4_sim = ctrl.ControlSystemSimulation(Target_F4_system)

        def actions(self, ship: SpaceShip, input_data: Dict[str, Tuple]) -> None:

            """
                    Compute control actions of the ship. Perform all command actions via the ``ship``
                    argument. This class acts as an intermediary between the controller and the environment.
                    The environment looks for this function when calculating control actions for the Ship sprite.
                    :param ship: Object to use when controlling the SpaceShip
                    :param input_data: Input data which describes the current state of the environment
                    """
            roe_zone = self.roe_zone  # Max distance at which the autotargeting system will engage
            roe_size = 1  # Max asteroid size the autotargeting system will engage

            astnum = len(input_data['asteroids'])
            if astnum > 0:
                distance = numpy.zeros(astnum)
                for p in range(0, astnum):
                    distance[p] = 1000
                shortest_distance = 1000
                closest_asteroid = 0
                astnumo = astnum - 1
                closest_asteroids = [astnumo, astnumo, astnumo, astnumo, astnumo]
                total_velocity = abs((ship.velocity[0] ** 2 + ship.velocity[1] ** 2) ** 0.5)
                if total_velocity > 0:
                    if ship.velocity[1] > 0:
                        travel_angle = -1 * math.degrees(math.asin(ship.velocity[0] / total_velocity))
                    elif ship.velocity[0] > 0:
                        travel_angle = -180 + math.degrees(math.asin(ship.velocity[0] / total_velocity))
                    elif ship.velocity[0] < 0:
                        travel_angle = 180 + math.degrees(math.asin(ship.velocity[0] / total_velocity))
                    else:
                        travel_angle = 0

                sidefromcenter = 400 - ship.center_x
                above_center = 300 - ship.center_y
                distancefromcenter = ((ship.center_x - 400) ** 2 + (ship.center_y - 300) ** 2) ** 0.5
                if distancefromcenter > 0:
                    anglefromcenter = self.rangle(sidefromcenter, distancefromcenter, above_center, sidefromcenter)
                else:
                    anglefromcenter = 0
                """
                angle_from_center=self.rangle(sidefromcenter, distancefromcenter, above_center, sidefromcenter)
                """
                """Below it goes through the asteroids, 
                records their distance, 
                and sets the shortest distance and closest asteroid"""
                inrange_distance = numpy.zeros(astnum)
                inrange_asteroid = numpy.zeros(astnum)
                inrange_size = numpy.zeros(astnum)
                astrange = 0

                ab2 = numpy.zeros(200)
                lr2 = numpy.zeros(200)
                op2 = numpy.zeros(200)
                hyp2 = numpy.zeros(200)
                s_rangle_inrange = numpy.zeros(200)

                orientation2 = numpy.ones(200) * 100

                # Distance Finding Every Asteroids
                for n in range(0, astnum):
                    distance[n] = (((input_data['asteroids'][n]['position'][0]) - ship.center_x) ** 2 + (
                            (input_data['asteroids'][n]['position'][1]) - ship.center_y) ** 2) ** 0.5
                    if distance[n] < shortest_distance:
                        shortest_distance = distance[n]
                        closest_asteroid = n

                    # Distance-based multitasking
                    if distance[n] < roe_zone and input_data['asteroids'][n][
                        'size'] <= roe_size:  # Variables defined above
                        inrange_distance[astrange] = distance[n]
                        inrange_asteroid[astrange] = n
                        inrange_size[astrange] = input_data['asteroids'][n]['size']

                        astrange += 1

                # Orientation Calculator
                Favorability = numpy.zeros(astrange)
                bloop = 0
                inrange_asteroid = numpy.int64(
                    inrange_asteroid)  # Converts numpy float to integer (could be streamlined)
                for m in range(0, astrange):
                    ab2[m] = input_data['asteroids'][inrange_asteroid[m]]['position'][1] - ship.center_y
                    lr2[m] = input_data['asteroids'][inrange_asteroid[m]]['position'][0] - ship.center_x
                    op2[m] = input_data['asteroids'][inrange_asteroid[m]]['position'][0] - ship.center_x
                    hyp2[m] = inrange_distance[m]
                    s_rangle_inrange[m] = self.rangle(op2[m], hyp2[m], ab2[m], lr2[m])
                    normal_astangle_mult = self.norm(s_rangle_inrange[m])
                    vx_mult = input_data['asteroids'][closest_asteroid]['velocity'][0]
                    vy_mult = input_data['asteroids'][closest_asteroid]['velocity'][1]

                    ant_angle2 = aiming_function(vx_mult, vy_mult, normal_astangle_mult)
                    Target_orientation = abs(ship.angle - s_rangle_inrange[m] + ant_angle2)
                    orientation2[m] = abs(ship.angle - s_rangle_inrange[
                        m] + ant_angle2)  # Orientation 2 is the relative angles of all ROE-free asteroids
                    if inrange_size[m] == 4:
                        self.Target_F4_sim.input['f_orientation_size4'] = orientation2[m]
                        self.Target_F4_sim.input['f_hypotenuse_size4'] = inrange_distance[m]
                        self.Target_F4_sim.compute()
                        Favorability[m] = self.Target_F4_sim.output['Target_F4']
                    elif inrange_size[m] == 3:
                        self.Target_F3_sim.input['f_orientation_size3'] = orientation2[m]
                        self.Target_F3_sim.input['f_hypotenuse_size3'] = inrange_distance[m]
                        self.Target_F3_sim.compute()
                        Favorability[m] = self.Target_F3_sim.output['Target_F3']
                    elif inrange_size[m] == 2:
                        self.Target_F2_sim.input['f_orientation_size2'] = orientation2[m]
                        self.Target_F2_sim.input['f_hypotenuse_size2'] = inrange_distance[m]
                        self.Target_F2_sim.compute()
                        Favorability[m] = self.Target_F2_sim.output['Target_F2']
                    elif inrange_size[m] == 1:
                        self.Target_F1_sim.input['f_orientation_size1'] = orientation2[m]
                        self.Target_F1_sim.input['f_hypotenuse_size1'] = inrange_distance[m]
                        self.Target_F1_sim.compute()
                        Favorability[m] = self.Target_F1_sim.output['Target_F1']
                    if m == 0:
                        if Favorability[m] > 0:
                            Target = m
                            bloop = bloop + 1
                    elif Favorability[m] == numpy.max(Favorability[m]):
                        Target = m
                        bloop = bloop + 1

                abovebelow = input_data['asteroids'][closest_asteroid]['position'][1] - ship.center_y
                leftright = input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x
                opposite = (input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x)
                hypotenuse = shortest_distance
                s_rangle = self.rangle(opposite, hypotenuse, abovebelow, leftright)
                orientation = abs(ship.angle - s_rangle)
                if bloop > 0:
                    if inrange_size[Target] < 4 and shortest_distance > self.fuzzy_roe:
                        Target_orientation = orientation2[Target]
                        Target_angle = s_rangle_inrange[Target]
                        Target_Distance = inrange_distance[Target]
                        # Target_size = inrange_size[Target]
                        # Target_Favorability = Favorability[m]

                    else:
                        Target_orientation = orientation
                        Target_angle = s_rangle
                        Target_Distance = shortest_distance
                        # Target_size = input_data['asteroids'][closest_asteroid]['size']
                        # Target_Favorability = 0
                elif bloop == 0:
                    Target_orientation = orientation
                    Target_angle = s_rangle
                    Target_Distance = shortest_distance
                    # Target_size = input_data['asteroids'][closest_asteroid]['size']
                    # Target_Favorability = 0

                """
                s_rangle is the angle relative to the ship necessary for the ship to point at the closest asteroid
                """
                """ Positive if above, negative if below"""
                """ negative if left, positive if right"""

                normal_shipangle = self.norm(ship.angle)
                normal_astangle = self.norm(s_rangle)
                normal_cangle = self.norm(anglefromcenter)
                normal_target_angle = self.norm(Target_angle)
                diff = ship.angle - s_rangle
                clast_size = input_data['asteroids'][closest_asteroid]['size']
                dodge_counter = 0
                if Target_orientation == orientation:
                    vx_mult = input_data['asteroids'][closest_asteroid]['velocity'][0]
                    vy_mult = input_data['asteroids'][closest_asteroid]['velocity'][1]

                    self.ant_angle = aiming_function(vx_mult, vy_mult, normal_astangle)
                    Target_orientation = abs(ship.angle - s_rangle + self.ant_angle)
                    leftright_target = self.leftright(normal_shipangle, normal_target_angle)
                else:
                    vx_mult = input_data['asteroids'][inrange_asteroid[Target]]['velocity'][0]
                    vy_mult = input_data['asteroids'][inrange_asteroid[Target]]['velocity'][1]
                    Target_s_rangle = s_rangle_inrange[Target]
                    Target_normal_astangle = self.norm(Target_s_rangle)
                    self.ant_angle = aiming_function(vx_mult, vy_mult, Target_normal_astangle)
                    Target_orientation = abs(ship.angle - Target_s_rangle + self.ant_angle)
                    leftright_target = self.leftright(normal_shipangle, normal_target_angle)
                vx_mult = input_data['asteroids'][closest_asteroid]['velocity'][0]
                vy_mult = input_data['asteroids'][closest_asteroid]['velocity'][1]
                self.ant_angle = aiming_function(vx_mult, vy_mult, normal_astangle)
                leftright_dodge = self.leftright(normal_shipangle, normal_astangle)
                """
                This is the master if function in which it determines which behavior mode to fall into 
                """

                if ship.respawn_time_left > 0 and shortest_distance < 45 + (5 * clast_size):  # Respawn Behavior
                    if orientation > 160:
                        ship.thrust = ship.thrust_range[1]
                    elif orientation <= 160:
                        ship.thrust = 0
                        ship.turn_rate = 180

                else:

                    if total_velocity > 1 + (shortest_distance / self.brake_speed_power):  # Braking Speed Determinant

                        """
                        Braking Manuever- For if the ship is going to fast. Probably best for when there's a lot of 
                        asteroids and you do you don't want it to slignshot past on into another
                        """

                        t_orientation = abs(ship.angle - travel_angle)
                        if travel_angle == 0:
                            pass
                        elif t_orientation > 60:
                            ship.thrust = ship.thrust_range[1]
                        elif t_orientation < 60:
                            ship.thrust = ship.thrust_range[0]
                        else:
                            print('something wonky afoot')

                    elif shortest_distance < self.evasive_base + (self.evasive_size_adjust * clast_size):
                        """Evasive Manuevers, I think we could expand this to considering the closest three 
                            asteroids and fuzzily deciding which direction to flee in
                            for cases where an asteroid is perpindicularly approaching it needs to be able to distinguish left and right anf
                            behave accordingly """
                        dodge_counter = 1
                        if orientation > 90:
                            ship.thrust = ship.thrust_range[1]
                        elif orientation > 90 and orientation < 90:
                            ship.thrust = 0
                        else:
                            ship.thrust = ship.thrust_range[0]

                        if leftright_dodge == 0 or leftright_dodge == 1:
                            if leftright_dodge == 0 and orientation > 1:
                                ship.turn_rate = 180
                            elif leftright_dodge == 0 and orientation <= 1:
                                ship.turn_rate = 90
                            elif leftright_dodge == 1 and orientation > 1:
                                ship.turn_rate = -180
                            else:
                                ship.turn_rate = -90

                    elif ship.center_x > 800-self.edgeclear or ship.center_x < self.edgeclear or ship.center_y > 600-self.edgeclear or ship.center_y < self.edgeclear:
                        turn = self.leftright(normal_shipangle, normal_cangle)
                        center_orientation = abs(ship.angle - anglefromcenter)
                        if center_orientation < 180:
                            ship.thrust = ship.thrust_range[1]
                        elif turn == 0:
                            ship.turn_rate = 180
                        else:
                            ship.turn_rate = -180

                        """
                        # Search and Destroy
                        elif shortest_distance > 50 + (62 * clast_size):
                        ship.thrust = ship.thrust_range[1]
                        """
                    # Search and Destroy Also Aiming for Target, will probs give it aiming for dodging
                    elif shortest_distance > self.SAD_base + (self.SAD_size_adjust * clast_size) and dodge_counter == 0:
                        ship.thrust = ship.thrust_range[1]

                    if leftright_target == 0 or leftright_target == 1:
                        if leftright_target == 0 and Target_orientation > 3:
                            ship.turn_rate = 180
                        elif leftright_target == 0 and Target_orientation <= 3:
                            ship.turn_rate = 90
                        elif leftright_target == 1 and Target_orientation > 3:
                            ship.turn_rate = -180
                        else:
                            ship.turn_rate = -90

                    """
                    Shooting Mechanism
                    """
                    self.wack += self.wack_coef  # wack increases until it reaches a fire threshold

                    for l in range(0, len(orientation2)):  # runs this once for every asteroid in the ROE zone.
                        if dodge_counter == 0:
                            if orientation < 2 * clast_size or orientation2[l] < 2:

                                if self.wack > Target_Distance:
                                    self.wack = 0
                                    ship.shoot()
                        else:
                            if Target_orientation < 2 * clast_size or orientation2[l] < 2:

                                if self.wack > Target_Distance:
                                    self.wack = 0
                                    ship.shoot()
    fitness=0
    for b in range(0, 3):
        game = TrainerEnvironment(settings=settings)
        score = game.run(controller=FuzzyController())
        if score.deaths == 0:
            fitness += 24
        else:
            fitness += 18 / score.deaths - 5


    def truncate(n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier
    fitness=int(fitness)
    return fitness,

