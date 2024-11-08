import pytest
from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel

import os
DATABASE_PATH = os.path.abspath("db/meal_max.db")




@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    """Fixture providing a sample Meal object for testing."""
    return Meal(id=1, meal='Pizza', price=12.99, cuisine='Italian', difficulty='MED')

@pytest.fixture
def sample_meal2():
    """Fixture providing another sample Meal object for testing."""
    return Meal(id=2, meal='Burger', price=9.99, cuisine='American', difficulty='LOW')


##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the battle model."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Pizza'


def test_prep_combatant_limit(battle_model, sample_meal1, sample_meal2):
    """Test error when adding more than two combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(Meal(id=3, meal='Sushi', price=15.99, cuisine='Japanese', difficulty='HIGH'))


def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing all combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing."


##################################################
# Battle Simulation Test Cases
##################################################

def test_battle(battle_model, sample_meal1, sample_meal2, mocker):
    """Test simulating a battle and determining a winner."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    # Mock get_random and update_meal_stats to control randomness and avoid side effects
    mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.5)
    mock_update_stats = mocker.patch("meal_max.models.battle_model.update_meal_stats")

    winner = battle_model.battle()

    # Check the winner and assert that stats were updated
    assert winner in [sample_meal1.meal, sample_meal2.meal]
    assert mock_update_stats.call_count == 2
    mock_update_stats.assert_any_call(sample_meal1.id, 'win' if winner == sample_meal1.meal else 'loss')
    mock_update_stats.assert_any_call(sample_meal2.id, 'win' if winner == sample_meal2.meal else 'loss')



def test_battle_insufficient_combatants(battle_model):
    """Test error when trying to battle with less than two combatants."""
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_battle_clear_combatants(battle_model, sample_meal1, sample_meal2, mocker):
    """Test that combatants are cleared correctly after a battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    # Mock update_meal_stats to prevent real database interaction
    mocker.patch("meal_max.models.battle_model.update_meal_stats")
    battle_model.battle()

    # After the battle, only one combatant should remain
    assert len(battle_model.get_combatants()) == 1

# def test_battle_winner_selection(battle_model, sample_meal1, sample_meal2, mocker):
#     """Test that the winner is correctly selected based on battle scores."""
#     battle_model.prep_combatant(sample_meal1)
#     battle_model.prep_combatant(sample_meal2)

#     # Mock get_random to control randomness
#     mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.2)

#     # Run the battle
#     winner = battle_model.battle()

#     # Check that the winner is one of the combatants
#     assert winner in [sample_meal1.meal, sample_meal2.meal]

##################################################
# Utility Function Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test calculating the battle score for a combatant."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 2   # MED difficulty modifier
    assert score == expected_score, f"Expected score to be {expected_score}, but got {score}"


def test_get_combatants(battle_model, sample_meal1):
    """Test retrieving the list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    combatants = battle_model.get_combatants()
    assert combatants == [sample_meal1], "Expected combatants list to contain only the prepped combatant."

# def test_update_meal_stats_call_on_battle(battle_model, sample_meal1, sample_meal2, mocker):
#     """Test that update_meal_stats is called correctly during battle for winner and loser without database access."""
#     battle_model.prep_combatant(sample_meal1)
#     battle_model.prep_combatant(sample_meal2)

#     # Mock get_random to control randomness
#     mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.5)
#     # Mock update_meal_stats to bypass actual database access
#     mock_update_meal_stats = mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

#     # Run the battle
#     winner_name = battle_model.battle()

#     # Check that update_meal_stats was called with the expected arguments for each combatant
#     if winner_name == sample_meal1.meal:
#         mock_update_meal_stats.assert_any_call(sample_meal1.id, 'win')
#         mock_update_meal_stats.assert_any_call(sample_meal2.id, 'loss')
#     else:
#         mock_update_meal_stats.assert_any_call(sample_meal1.id, 'loss')
#         mock_update_meal_stats.assert_any_call(sample_meal2.id, 'win')

#     # Assert that update_meal_stats was called exactly twice (once for each combatant)
#     assert mock_update_meal_stats.call_count == 2

def test_get_battle_score_with_invalid_difficulty(battle_model, sample_meal1):
    """Test calculating battle score with an invalid difficulty."""
    sample_meal1.difficulty = "INVALID"

    with pytest.raises(KeyError):
        battle_model.get_battle_score(sample_meal1)


def test_get_combatants_empty(battle_model):
    """Test retrieving combatants from an empty list."""
    combatants = battle_model.get_combatants()
    assert combatants == [], "Combatants list should be empty."

def test_get_combatants_after_clear(battle_model, sample_meal1, sample_meal2):
    """Test retrieving combatants after clearing the list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    battle_model.clear_combatants()
    combatants = battle_model.get_combatants()
    assert combatants == [], "Combatants list should be empty after clear."