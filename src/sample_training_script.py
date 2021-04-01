from fuzzy_asteroids.fuzzy_asteroids import TrainerEnvironment
import random
from deap import base
from deap import creator
from deap import tools
import pandas as pd
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import numpy
from src.sample_controller import FuzzyController
from sample_score import SampleScore

if __name__ == "__main__":
    # Available settings
    settings = {
        # "frequency": 60,
        # "lives": 3,
        # "prints": False,
    }

    # To use the controller within the context of a training solution
    # It is important to not create a new instance of the environment everytime
    game = TrainerEnvironment(settings=settings)
    """
    Created on Sat Feb 13 22:18:12 2021

    @author: Team Asimov
    """
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    # Attribute generator
    #                      define 'attr_bool' to be an attribute ('gene')
    #                      which corresponds to integers sampled uniformly
    #                      from the range [0,1] (i.e. 0 or 1 with equal
    #                      probability)
    toolbox.register("attr_output", random.random())

    # Structure initializers
    #                         define 'individual' to be an individual
    #                         consisting of 100 'attr_bool' elements ('genes')
    toolbox.register("individual", tools.initRepeat, creator.Individual,
                     toolbox.attr_output, 9)

    # define the population to be a list of individuals
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)


    # the goal ('fitness') function to be maximized
    def evalTip(individual):

        # Defines a fuzzy inference system for "Tip"

        temp = ctrl.Antecedent(numpy.arange(0, 11, 1), 'temp')
        taste = ctrl.Antecedent(numpy.arange(0, 11, 1), 'price')
        price = ctrl.Antecedent(numpy.arange(0, 11, 1), 'taste')
        quality = ctrl.Consequent(numpy.arange(-6, 16, 1), 'quality')

        names = ['low', 'avg', 'high']
        temp.automf(names=names)
        taste.automf(names=names)
        price.automf(names=names)

        quality['low'] = fuzz.trimf(quality.universe, [-5, 0, 5])
        quality['avg'] = fuzz.trimf(quality.universe, [0, 5, 10])
        quality['high'] = fuzz.trimf(quality.universe, [5, 10, 15])

        rule1 = ctrl.Rule((temp['low'] & price['low'] & taste['low']) |
                          (temp['low'] & price['avg'] & taste['low']) |
                          (temp['low'] & price['high'] & taste['low']) |
                          (temp['avg'] & price['low'] & taste['low']) |
                          (temp['high'] & price['low'] & taste['low']) |
                          (temp['avg'] & price['avg'] & taste['low']) |
                          (temp['avg'] & price['high'] & taste['low']) |
                          (temp['high'] & price['avg'] & taste['low']) |
                          (temp['low'] & price['low'] & taste['avg']) |
                          (temp['low'] & price['avg'] & taste['avg']) |
                          (temp['avg'] & price['low'] & taste['avg']),
                          quality['low'])

        rule2 = ctrl.Rule((temp['high'] & price['high'] & taste['low']) |
                          (temp['avg'] & price['avg'] & taste['avg']) |
                          (temp['low'] & price['high'] & taste['avg']) |
                          (temp['high'] & price['low'] & taste['avg']) |
                          (temp['low'] & price['low'] & taste['high']) |
                          (temp['low'] & price['avg'] & taste['high']) |
                          (temp['low'] & price['high'] & taste['high']) |
                          (temp['avg'] & price['low'] & taste['high']) |
                          (temp['high'] & price['low'] & taste['high']),
                          quality['avg'])

        rule3 = ctrl.Rule((temp['avg'] & price['high'] & taste['avg']) |
                          (temp['high'] & price['avg'] & taste['avg']) |
                          (temp['high'] & price['high'] & taste['avg']) |
                          (temp['avg'] & price['avg'] & taste['high']) |
                          (temp['avg'] & price['high'] & taste['high']) |
                          (temp['high'] & price['avg'] & taste['high']) |
                          (temp['high'] & price['high'] & taste['high']),
                          quality['high'])

        quality_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        quality = ctrl.ControlSystemSimulation(quality_ctrl)

        """
        Service Calculation
        """

        # Create fuzzy variables (two inputs, one output)
        attentiveness = ctrl.Antecedent(numpy.arange(0, 11, 1), 'attentiveness')
        speed = ctrl.Antecedent(numpy.arange(0, 11, 1), 'speed')
        friendliness = ctrl.Antecedent(numpy.arange(0, 11, 1), 'friendliness')
        service_q = ctrl.Consequent(numpy.arange(-6, 16, 1), 'service')

        # Use automf to define three membership function names
        # Names: Bad, Neutral, Good
        names = ['bad', 'neutral', 'good']
        attentiveness.automf(names=names)
        speed.automf(names=names)
        friendliness.automf(names=names)

        service_q['bad'] = fuzz.trimf(service_q.universe, [-5, 0, 5])
        service_q['neutral'] = fuzz.trimf(service_q.universe, [0, 5, 10])
        service_q['good'] = fuzz.trimf(service_q.universe, [5, 10, 15])

        # Define rules Bad, Neutral, Good:
        s_rule0 = ctrl.Rule(antecedent=((attentiveness['bad'] & speed['bad']) & friendliness['bad'] |
                                        (attentiveness['bad'] & speed['neutral']) & friendliness['bad'] |
                                        (attentiveness['bad'] & speed['good']) & friendliness['bad'] |
                                        (attentiveness['neutral'] & speed['bad']) & friendliness['bad'] |
                                        (attentiveness['good'] & speed['bad']) & friendliness['bad'] |
                                        (attentiveness['neutral'] & speed['neutral']) & friendliness['bad'] |
                                        (attentiveness['neutral'] & speed['good']) & friendliness['bad'] |
                                        (attentiveness['good'] & speed['neutral']) & friendliness['bad'] |
                                        (attentiveness['bad'] & speed['bad']) & friendliness['neutral'] |
                                        (attentiveness['bad'] & speed['neutral']) & friendliness['neutral'] |
                                        (attentiveness['neutral'] & speed['bad']) & friendliness['neutral']),
                            consequent=service_q['bad'], label='s_rule b')

        s_rule1 = ctrl.Rule(antecedent=((attentiveness['neutral'] & speed['neutral']) & friendliness['neutral'] |
                                        (attentiveness['good'] & speed['good']) & friendliness['bad'] |
                                        (attentiveness['bad'] & speed['good']) & friendliness['neutral'] |
                                        (attentiveness['good'] & speed['bad']) & friendliness['neutral'] |
                                        (attentiveness['bad'] & speed['bad']) & friendliness['good'] |
                                        (attentiveness['bad'] & speed['neutral']) & friendliness['good'] |
                                        (attentiveness['bad'] & speed['good']) & friendliness['good'] |
                                        (attentiveness['neutral'] & speed['bad']) & friendliness['good'] |
                                        (attentiveness['good'] & speed['bad']) & friendliness['good']),
                            consequent=service_q['neutral'], label='s_rule n')

        s_rule2 = ctrl.Rule(antecedent=((attentiveness['neutral'] & speed['good']) & friendliness['neutral'] |
                                        (attentiveness['good'] & speed['neutral']) & friendliness['neutral'] |
                                        (attentiveness['good'] & speed['good']) & friendliness['neutral'] |
                                        (attentiveness['neutral'] & speed['neutral']) & friendliness['good'] |
                                        (attentiveness['neutral'] & speed['good']) & friendliness['good'] |
                                        (attentiveness['good'] & speed['neutral']) & friendliness['good'] |
                                        (attentiveness['good'] & speed['good']) & friendliness['good']),
                            consequent=service_q['good'], label='s_rule g')

        # Add rules to control system
        system = ctrl.ControlSystem(rules=[s_rule0, s_rule1, s_rule2])

        s_sim = ctrl.ControlSystemSimulation(system)

        # print(round(calc_service))

        # Create fuzzy variables (three inputs, one output)
        food = ctrl.Antecedent(numpy.arange(0, 11, 1), 'food')
        service = ctrl.Antecedent(numpy.arange(0, 11, 1), 'service')
        tip = ctrl.Consequent(numpy.arange(-6, 16, 1), 'tip')

        # Use automf to define three membership function names
        # Names: Bad, Neutral, Good
        names = ['bad', 'neutral', 'good']
        service.automf(names=names)
        food.automf(names=names)

        tip['low'] = fuzz.trimf(tip.universe, [-5, 0, 5])
        tip['medium'] = fuzz.trimf(tip.universe, [0, 5, 10])
        tip['high'] = fuzz.trimf(tip.universe, [5, 10, 15])

        def truncate(n, decimals=0):
            multiplier = 10 ** decimals
            return int(n * multiplier) / multiplier

        diff_total = 0
        # Define rules Bad, Neutral, Good:
        for x in range(0, 208):
            """
            Based on the information from the chromosomes, 
            the rules of the inference system are changed
            """
            """ Rule 1 """
            if individual[0] == 1:
                t_rule0 = ctrl.Rule(antecedent=(food['bad'] & service['bad']), consequent=tip['low'], label='t_rule_0')
            if individual[0] == 2:
                t_rule0 = ctrl.Rule(antecedent=(food['bad'] & service['bad']), consequent=tip['medium'],
                                    label='t_rule_0')
            if individual[0] == 3:
                t_rule0 = ctrl.Rule(antecedent=(food['bad'] & service['bad']), consequent=tip['high'], label='t_rule_0')

            """ Rule 2 """
            if individual[1] == 1:
                t_rule1 = ctrl.Rule(antecedent=(food['bad'] & service['neutral']), consequent=tip['low'],
                                    label='t_rule_1')
            if individual[1] == 2:
                t_rule1 = ctrl.Rule(antecedent=(food['bad'] & service['neutral']), consequent=tip['medium'],
                                    label='t_rule_1')
            if individual[1] == 3:
                t_rule1 = ctrl.Rule(antecedent=(food['bad'] & service['neutral']), consequent=tip['high'],
                                    label='t_rule_1')

            """ Rule 3 """
            if individual[2] == 1:
                t_rule2 = ctrl.Rule(antecedent=(food['neutral'] & service['bad']), consequent=tip['low'],
                                    label='t_rule_2')
            if individual[2] == 2:
                t_rule2 = ctrl.Rule(antecedent=(food['neutral'] & service['bad']), consequent=tip['medium'],
                                    label='t_rule_2')
            if individual[2] == 3:
                t_rule2 = ctrl.Rule(antecedent=(food['neutral'] & service['bad']), consequent=tip['high'],
                                    label='t_rule_2')

            """ Rule 4 """
            if individual[3] == 1:
                t_rule3 = ctrl.Rule(antecedent=(food['neutral'] & service['neutral']), consequent=tip['low'],
                                    label='t_rule_3')
            if individual[3] == 2:
                t_rule3 = ctrl.Rule(antecedent=(food['neutral'] & service['neutral']), consequent=tip['medium'],
                                    label='t_rule_3')
            if individual[3] == 3:
                t_rule3 = ctrl.Rule(antecedent=(food['neutral'] & service['neutral']), consequent=tip['high'],
                                    label='t_rule_3')

            """ Rule 5 """
            if individual[4] == 1:
                t_rule4 = ctrl.Rule(antecedent=(food['good'] & service['bad']), consequent=tip['low'], label='t_rule_4')
            if individual[4] == 2:
                t_rule4 = ctrl.Rule(antecedent=(food['good'] & service['bad']), consequent=tip['medium'],
                                    label='t_rule_4')
            if individual[4] == 3:
                t_rule4 = ctrl.Rule(antecedent=(food['good'] & service['bad']), consequent=tip['high'],
                                    label='t_rule_4')

            """ Rule 6 """
            if individual[5] == 1:
                t_rule5 = ctrl.Rule(antecedent=(food['bad'] & service['good']), consequent=tip['low'], label='t_rule_5')
            if individual[5] == 2:
                t_rule5 = ctrl.Rule(antecedent=(food['bad'] & service['good']), consequent=tip['medium'],
                                    label='t_rule_5')
            if individual[5] == 3:
                t_rule5 = ctrl.Rule(antecedent=(food['bad'] & service['good']), consequent=tip['high'],
                                    label='t_rule_5')

            """ Rule 7 """
            if individual[6] == 1:
                t_rule6 = ctrl.Rule(antecedent=(food['neutral'] & service['good']), consequent=tip['low'],
                                    label='t_rule_6')
            if individual[6] == 2:
                t_rule6 = ctrl.Rule(antecedent=(food['neutral'] & service['good']), consequent=tip['medium'],
                                    label='t_rule_6')
            if individual[6] == 3:
                t_rule6 = ctrl.Rule(antecedent=(food['neutral'] & service['good']), consequent=tip['high'],
                                    label='t_rule_6')

            """ Rule 8 """
            if individual[7] == 1:
                t_rule7 = ctrl.Rule(antecedent=(food['good'] & service['neutral']), consequent=tip['low'],
                                    label='t_rule_7')
            if individual[7] == 2:
                t_rule7 = ctrl.Rule(antecedent=(food['good'] & service['neutral']), consequent=tip['medium'],
                                    label='t_rule_7')
            if individual[7] == 3:
                t_rule7 = ctrl.Rule(antecedent=(food['good'] & service['neutral']), consequent=tip['high'],
                                    label='t_rule_7')

            """ Rule 9 """
            if individual[8] == 1:
                t_rule8 = ctrl.Rule(antecedent=(food['good'] & service['good']), consequent=tip['low'],
                                    label='t_rule_8')
            if individual[8] == 2:
                t_rule8 = ctrl.Rule(antecedent=(food['good'] & service['good']), consequent=tip['medium'],
                                    label='t_rule_8')
            if individual[8] == 3:
                t_rule8 = ctrl.Rule(antecedent=(food['good'] & service['good']), consequent=tip['high'],
                                    label='t_rule_8')

            """
            t_rule0 = ctrl.Rule(antecedent=(food['bad'] & service['bad']),consequent=tip['low'], label='t_rule_0')
            t_rule1 = ctrl.Rule(antecedent=(food['bad'] & service['neutral']),consequent=tip['low'], label='t_rule_1')
            t_rule2 = ctrl.Rule(antecedent=(food['neutral'] & service['bad']),consequent=tip['low'], label='t_rule_2')
            t_rule3 = ctrl.Rule(antecedent=(food['neutral'] & service['neutral']),consequent=tip['medium'], label='t_rule_3')
            t_rule4 = ctrl.Rule(antecedent=(food['good'] & service['bad']),consequent=tip['medium'], label='t_rule_4')
            t_rule5 = ctrl.Rule(antecedent=(food['bad'] & service['good']),consequent=tip['medium'], label='t_rule_5')
            t_rule6 = ctrl.Rule(antecedent=(food['neutral'] & service['good']),consequent=tip['high'], label='t_rule_6')
            t_rule7 = ctrl.Rule(antecedent=(food['good'] & service['neutral']),consequent=tip['high'], label='t_rule_7')
            t_rule8 = ctrl.Rule(antecedent=(food['good'] & service['good']),consequent=tip['high'], label='t_rule_8')
            """

            # Add rules to control system
            t_system = ctrl.ControlSystem(
                rules=[t_rule0, t_rule1, t_rule2, t_rule3, t_rule4, t_rule5, t_rule6, t_rule7, t_rule8])

            t_sim = ctrl.ControlSystemSimulation(t_system)
            """
            Inputs
            """
            quality.input['taste'] = data['food flavor'][x] * 10
            if data['food flavor'][x] < 0:
                quality.input['taste'] = 0
            if data['food flavor'][x] > 1:
                quality.input['taste'] = 10

            quality.input['temp'] = data['food temperature'][x] * 10
            if data['food temperature'][x] < 0:
                quality.input['temp'] = 0
            if data['food temperature'][x] > 1:
                quality.input['temp'] = 10

            quality.input['price'] = data['portion size'][x] * 10
            if data['portion size'][x] < 0:
                quality.input['price'] = 0
            if data['portion size'][x] > 1:
                quality.input['price'] = 10

            quality.compute()
            food_crisp = quality.output['quality']

            s_sim.input['attentiveness'] = data['attentiveness'][x] * 10
            if data['attentiveness'][x] < 0:
                s_sim.input['attentiveness'] = 0
            if data['attentiveness'][x] > 1:
                s_sim.input['attentiveness'] = 10

            s_sim.input['friendliness'] = data['friendliness'][x] * 10
            if data['friendliness'][x] < 0:
                s_sim.input['friendliness'] = 0
            if data['friendliness'][x] > 1:
                s_sim.input['friendliness'] = 10

            s_sim.input['speed'] = data['speed of service'][x] * 10
            if data['speed of service'][x] < 0:
                s_sim.input['speed'] = 0
            if data['speed of service'][x] > 1:
                s_sim.input['speed'] = 10

            s_sim.compute()
            service_crisp = s_sim.output['service']

            t_sim.input['food'] = food_crisp
            t_sim.input['service'] = service_crisp

            t_sim.compute()
            crisp = t_sim.output['tip']
            new_crisp = (crisp / 10) * 25

            final_crisp = truncate(new_crisp, 4)
            diff = (final_crisp - data['tip'][x]) * (final_crisp - data['tip'][x])
            if data['tip'][x] < 0:
                diff = (final_crisp - 0) * (final_crisp - 0)
            if data['tip'][x] > 25:
                diff = (final_crisp - 25) * (final_crisp - 25)
            diff_total = diff_total + diff
        print('one eval cycle done')
        return 100 / diff_total,


    # ----------
    # Operator registration
    # ----------
    # register the goal / fitness function
    toolbox.register("evaluate", evalTip)

    # register the crossover operator
    toolbox.register("mate", tools.cxTwoPoint)

    # register a mutation operator with a probability to
    # flip each attribute/gene of 0.05
    toolbox.register("mutate", tools.mutUniformInt, up=3, low=1, indpb=0.2)

    # operator for selecting individuals for breeding the next
    # generation: each individual of the current generation
    # is replaced by the 'fittest' (best) of three individuals
    # drawn randomly from the current generation.
    toolbox.register("select", tools.selRoulette)

    # ----------
    """
    The Genetic Algorithm Itself
    """


    def main():
        random.seed(42)

        # create an initial population of 300 individuals (where
        # each individual is a list of integers)
        pop = toolbox.population(n=20)
        hof_overall = tools.selBest(pop, 1)[0]

        # CXPB  is the probability with which two individuals
        #       are crossed
        #
        # MUTPB is the probability for mutating an individual
        CXPB, MUTPB = 0.5, 0.2

        print("Start of evolution")

        # Evaluate the entire population
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(pop))

        # Extracting all the fitnesses of
        fits = [ind.fitness.values[0] for ind in pop]

        # Variable keeping track of the number of generations
        g = 0

        # Begin the evolution
        while g < 10:
            # A new generation
            g = g + 1
            print("-- Generation %i --" % g)

            # Select the next generation individuals
            offspring = toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = list(map(toolbox.clone, offspring))

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):

                # cross two individuals with probability CXPB
                if random.random() < CXPB:
                    toolbox.mate(child1, child2)

                    # fitness values of the children
                    # must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:

                # mutate an individual with probability MUTPB
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            print("  Evaluated %i individuals" % len(invalid_ind))

            # The population is entirely replaced by the offspring
            pop[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in pop]

            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean ** 2) ** 0.5

            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)
            hof_app = tools.selBest(pop, 1)[0]
            if hof_app.fitness.values > hof_overall.fitness.values:
                hof_overall = hof_app

        print("-- End of (successful) evolution --")

        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual of the last generation is %s, %s" % (best_ind, best_ind.fitness.values))
        print("Best individual overall is %s, %s" % (hof_overall, hof_overall.fitness.values))
        print("Part of the Best individual is %s" % (hof_overall[7]))


    for i in range(1000):
        # Call run() on an instance of the TrainerEnvironment
        # This function automatically manages cleanup
        score = game.run(controller=FuzzyController(), score=SampleScore())

        print(f"Generation {i}: {str(score)}")
