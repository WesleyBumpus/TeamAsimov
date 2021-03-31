import skfuzzy as fuzz
import skfuzzy.control as ctrl
import numpy

# For Size 1
f_orientation_size1 = ctrl.Antecedent(numpy.arange(-91, 271, 1), 'f_orientation_size1')
f_orientation_size1['In Sights'] = fuzz.trimf(f_orientation_size1.universe, [-15, 0, 15])
f_orientation_size1['Close'] = fuzz.trimf(f_orientation_size1.universe, [15, 45, 75])
f_orientation_size1['Far'] = fuzz.trimf(f_orientation_size1.universe, [75, 180, 285])
# shortest_distance < 50 + (12 * clast_size)
f_hypotenuse_size1 = ctrl.Antecedent(numpy.arange(-81, 261, 1), 'f_hypotenuse_size1')
f_hypotenuse_size1['Imminent'] = fuzz.trimf(f_hypotenuse_size1.universe, [-80, 0, 80])
f_hypotenuse_size1['Close'] = fuzz.trimf(f_hypotenuse_size1.universe, [80, 140, 200])
f_hypotenuse_size1['Far'] = fuzz.trimf(f_hypotenuse_size1.universe, [140, 200, 260])
# Target_F
Target_F1 = ctrl.Consequent(numpy.arange(-26, 126, 1), 'Target_f')
Target_F1['Very Low'] = fuzz.trimf(Target_F1.universe, [-25, 0, 25])
Target_F1['Low'] = fuzz.trimf(Target_F1.universe, [0, 25, 50])
Target_F1['Medium'] = fuzz.trimf(Target_F1.universe, [25, 50, 75])
Target_F1['High'] = fuzz.trimf(Target_F1.universe, [50, 75, 100])
Target_F1['Very High'] = fuzz.trimf(Target_F1.universe, [75, 100, 125])

Target_F1_rule1 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Imminent'] & f_orientation_size1['In Sights']),
                            consequent=Target_F1['Very High'], label='Target_F1_rule1')

Target_F1_rule2 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Close'] & f_orientation_size1['In Sights']),
                            consequent=Target_F1['Very High'], label='Target_F1_rule2')

Target_F1_rule3 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Far'] & f_orientation_size1['In Sights']),
                            consequent=Target_F1['Very High'], label='Target_F1_rule3')

Target_F1_rule4 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Imminent'] & f_orientation_size1['Close']),
                            consequent=Target_F1['Very High'], label='Target_F1_rule4')

Target_F1_rule5 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Close'] & f_orientation_size1['Close']),
                            consequent=Target_F1['Very High'], label='Target_F1_rule5')

Target_F1_rule6 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Far'] & f_orientation_size1['Close']),
                            consequent=Target_F1['High'], label='Target_F1_rule6')

Target_F1_rule7 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Imminent'] & f_orientation_size1['Far']),
                            consequent=Target_F1['Very High'], label='Target_F1_rule7')

Target_F1_rule8 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Close'] & f_orientation_size1['Far']),
                            consequent=Target_F1['High'], label='Target_F1_rule8')

Target_F1_rule9 = ctrl.Rule(antecedent=(f_hypotenuse_size1['Far'] & f_orientation_size1['Far']),
                            consequent=Target_F1['Medium'], label='Target_F1_rule9')

Target_F1_system = ctrl.ControlSystem(rules=[Target_F1_rule1, Target_F1_rule2, Target_F1_rule3, Target_F1_rule4,
                                             Target_F1_rule5, Target_F1_rule6, Target_F1_rule7, Target_F1_rule8,
                                             Target_F1_rule9])
Target_F1_sim = ctrl.ControlSystemSimulation(Target_F1_system)

Target_F1_sim.input['f_orientation_size1'] = 45
Target_F1_sim.input['f_hypotenuse_size1'] = 100
Target_F1_sim.compute()
Favorability=Target_F1_sim.output['Target_f']
print(Crisp)