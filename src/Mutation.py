import random
def mutSet(individual):
    """Mutation that pops or add an element."""
    for n in range (0,len(individual)):
        if random.random() < 0.2:    # We cannot pop from an empty set
                individual[n]=random.random()
        else:
            pass
    return individual,