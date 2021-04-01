from fuzzy_asteroids.fuzzy_asteroids import TrainerEnvironment

from src.sample_controller import FuzzyController
from sample_score import SampleScore
from deap import base
from deap import creator
from deap import tools
import pandas as pd

if __name__ == "__main__":
    # Available settings
    settings = {
        "graphics_on": False,
        "sound_on": False,
        # "frequency": 60,
        "real_time_multiplier": 200,
        # "lives": 3,
        # "prints": True,
        "allow_key_presses": False
    }

    # To use the controller within the context of a training solution
    # It is important to not create a new instance of the environment everytime
    game = TrainerEnvironment(settings=settings)
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    for i in range(1000):
        # Call run() on an instance of the TrainerEnvironment
        # This function automatically manages cleanup
        score = game.run(controller=FuzzyController(), score=SampleScore())

        print(f"Generation {i}: {str(score)}")