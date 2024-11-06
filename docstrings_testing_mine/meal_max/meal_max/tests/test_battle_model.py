import unittest
from unittest.mock import patch, MagicMock
from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel
from meal_max.utils.random_utils import get_random

class TestBattleModel(unittest.TestCase):
    
    @patch('meal_max.models.battle_model.get_random')
    @patch('meal_max.models.kitchen_model.update_meal_stats')
    def test_battle(self, mock_update_stats, mock_get_random):
        """Test if battle between two meals updates statistics correctly."""

        # Mock the meals
        meal_1 = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MED")
        meal_2 = Meal(id=2, meal="Burger", cuisine="American", price=8.99, difficulty="LOW")

        # Initialize BattleModel
        battle_model = BattleModel()
        battle_model.combatants = [meal_1, meal_2]

        # Mock random number (simulating battle outcome)
        mock_get_random.return_value = 0.4

        # Mock update meal stats
        mock_update_stats.return_value = None

        # Run the battle
        result = battle_model.battle()

        # Check the result (the expected winner based on mocked random number and scores)
        self.assertEqual(result, "Spaghetti")

        # Check if update_meal_stats was called for both meals
        mock_update_stats.assert_any_call(1, 'win')
        mock_update_stats.assert_any_call(2, 'loss')

    @patch('meal_max.models.battle_model.get_random')
    def test_battle_insufficient_combatants(self, mock_get_random):
        """Test if battle raises an error when not enough combatants are present."""
        
        # Initialize BattleModel with only one combatant
        battle_model = BattleModel()
        meal_1 = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MED")
        battle_model.combatants = [meal_1]

        # Try to start the battle, expecting an error
        with self.assertRaises(ValueError):
            battle_model.battle()

    def test_clear_combatants(self):
        """Test if combatants list is cleared correctly."""
        
        # Initialize BattleModel with some combatants
        battle_model = BattleModel()
        meal_1 = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MED")
        meal_2 = Meal(id=2, meal="Burger", cuisine="American", price=8.99, difficulty="LOW")
        battle_model.combatants = [meal_1, meal_2]

        # Clear the combatants
        battle_model.clear_combatants()

        # Assert that the combatants list is empty
        self.assertEqual(len(battle_model.combatants), 0)

    def test_get_battle_score(self):
        """Test if battle score is calculated correctly."""
        
        # Initialize BattleModel
        battle_model = BattleModel()
        meal = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MED")

        # Get the battle score
        score = battle_model.get_battle_score(meal)

        # Calculate the expected score manually:
        # Score = (price * length of cuisine) - difficulty modifier
        expected_score = (10.99 * len("Italian")) - 2  # difficulty "MED" corresponds to a modifier of 2

        self.assertEqual(score, expected_score)

    def test_get_combatants(self):
        """Test if the combatants list is retrieved correctly."""
        
        # Initialize BattleModel with combatants
        battle_model = BattleModel()
        meal_1 = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MED")
        meal_2 = Meal(id=2, meal="Burger", cuisine="American", price=8.99, difficulty="LOW")
        battle_model.combatants = [meal_1, meal_2]

        # Get the current combatants
        combatants = battle_model.get_combatants()

        # Assert that the combatants list is returned correctly
        self.assertEqual(combatants, [meal_1, meal_2])

    def test_prep_combatant(self):
        """Test if combatant is added to the list properly."""
        
        # Initialize BattleModel
        battle_model = BattleModel()

        # Create a new combatant
        meal = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MED")

        # Prepare the combatant
        battle_model.prep_combatant(meal)

        # Assert the combatant is added to the list
        self.assertEqual(len(battle_model.combatants), 1)
        self.assertEqual(battle_model.combatants[0], meal)

    def test_prep_combatant_full_list(self):
        """Test if an error is raised when trying to add a combatant to a full list."""
        
        # Initialize BattleModel with 2 combatants already in place
        battle_model = BattleModel()
        meal_1 = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MED")
        meal_2 = Meal(id=2, meal="Burger", cuisine="American", price=8.99, difficulty="LOW")
        battle_model.combatants = [meal_1, meal_2]

        # Try to prep a third combatant, expecting an error
        meal_3 = Meal(id=3, meal="Tacos", cuisine="Mexican", price=7.99, difficulty="LOW")
        with self.assertRaises(ValueError):
            battle_model.prep_combatant(meal_3)

if __name__ == "__main__":
    unittest.main()
