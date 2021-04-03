from fuzzy_asteroids.fuzzy_asteroids import AsteroidGame, FuzzyAsteroidGame

from src.sample_controller import FuzzyController


if __name__ == "__main__":
    # Available settings
    settings = {
        "graphics_on": True,
        "sound_on": False,
        # "frequency": 60,
        "real_time_multiplier": 2000,
        # "lives": 3,
        # "prints": True,
        "allow_key_presses": True
    }

    # Whether the users controller should be run
    run_with_controller = 1

    # Run with FuzzyController
    if run_with_controller:
        # Instantiate the environment
        game = FuzzyAsteroidGame(settings=settings)
        score = game.run(controller=FuzzyController())
        print(score.asteroids_hit)

    else:
        # Run the Asteroids game with no
        game = AsteroidGame(settings=settings)
        game.run()
