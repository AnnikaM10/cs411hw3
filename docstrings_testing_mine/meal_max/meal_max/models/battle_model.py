import logging
from typing import List

from meal_max.models.kitchen_model import Meal, update_meal_stats
from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class BattleModel:

    def __init__(self):
        self.combatants: List[Meal] = []

    def battle(self) -> str:
        """
        Conducts a battle between two meals, determining a winner based on their battle scores.

        The battle process includes the following steps:
        1. Validates that there are exactly two combatants.
        2. Logs the start of the battle and the combatants involved.
        3. Calculates battle scores for both combatants based on their attributes.
        4. Computes the difference (delta) between the two scores and normalizes it.
        5. Generates a random number to determine the winner based on the normalized delta.
        6. Logs the winner and updates the combatants' statistics (wins and losses).
        7. Removes the losing combatant from the list of combatants.

        Returns:
            str: The name of the winning meal.

        Raises:
            ValueError: If there are not exactly two combatants available for the battle.
        """

        logger.info("Two meals enter, one meal leaves!")

        if len(self.combatants) < 2:
            logger.error("Not enough combatants to start a battle.")
            raise ValueError("Two combatants must be prepped for a battle.")

        combatant_1 = self.combatants[0]
        combatant_2 = self.combatants[1]

        # Log the start of the battle
        logger.info("Battle started between %s and %s", combatant_1.meal, combatant_2.meal)

        # Get battle scores for both combatants
        score_1 = self.get_battle_score(combatant_1)
        score_2 = self.get_battle_score(combatant_2)

        # Log the scores for both combatants
        logger.info("Score for %s: %.3f", combatant_1.meal, score_1)
        logger.info("Score for %s: %.3f", combatant_2.meal, score_2)

        # Compute the delta and normalize between 0 and 1
        delta = abs(score_1 - score_2) / 100

        # Log the delta and normalized delta
        logger.info("Delta between scores: %.3f", delta)

        # Get random number from random.org
        random_number = get_random()

        # Log the random number
        logger.info("Random number from random.org: %.3f", random_number)

        # Determine the winner based on the normalized delta
        if delta > random_number:
            winner = combatant_1
            loser = combatant_2
        else:
            winner = combatant_2
            loser = combatant_1

        # Log the winner
        logger.info("The winner is: %s", winner.meal)

        # Update stats for both combatants
        update_meal_stats(winner.id, 'win')
        update_meal_stats(loser.id, 'loss')

        # Remove the losing combatant from combatants
        self.combatants.remove(loser)

        return winner.meal

    def clear_combatants(self):
        """
        Clears the list of combatants for future battles.

        This method removes all combatants from the internal list, preparing
        the instance for a fresh set of combatants in subsequent battles.
        """

        logger.info("Clearing the combatants list.")
        self.combatants.clear()

    def get_battle_score(self, combatant: Meal) -> float:
        """
        Calculates the battle score for a given meal combatant.

        The battle score is determined using the following formula:
        (price of the meal * number of ingredients in the cuisine) 
        minus a difficulty modifier based on the meal's difficulty level.

        Parameters:
            combatant (Meal): The meal combatant for whom the score is to be calculated.

        Returns:
            float: The calculated battle score for the specified combatant.
        """

        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}

        # Log the calculation process
        logger.info("Calculating battle score for %s: price=%.3f, cuisine=%s, difficulty=%s",
                    combatant.meal, combatant.price, combatant.cuisine, combatant.difficulty)

        # Calculate score
        score = (combatant.price * len(combatant.cuisine)) - difficulty_modifier[combatant.difficulty]

        # Log the calculated score
        logger.info("Battle score for %s: %.3f", combatant.meal, score)

        return score

    def get_combatants(self) -> List[Meal]:
        """
        Retrieves the current list of combatants.

        This method returns the list of meal combatants that are available for battles.

        Returns:
            List[Meal]: A list of Meal objects representing the current combatants.

        """

        logger.info("Retrieving current list of combatants.")
        return self.combatants

    def prep_combatant(self, combatant_data: Meal):
        """
        Prepares and adds a combatant to the list of available combatants for battles.

        This method checks if there are already two combatants in the list. If so,
        it raises an error and prevents the addition of a new combatant. If there is
        space, the provided combatant is added to the list.

        Parameters:
            combatant_data (Meal): The meal combatant to be added.

        Raises:
            ValueError: If the combatants list already contains two combatants.

        """

        if len(self.combatants) >= 2:
            logger.error("Attempted to add combatant '%s' but combatants list is full", combatant_data.meal)
            raise ValueError("Combatant list is full, cannot add more combatants.")

        # Log the addition of the combatant
        logger.info("Adding combatant '%s' to combatants list", combatant_data.meal)

        self.combatants.append(combatant_data)

        # Log the current state of combatants
        logger.info("Current combatants list: %s", [combatant.meal for combatant in self.combatants])
