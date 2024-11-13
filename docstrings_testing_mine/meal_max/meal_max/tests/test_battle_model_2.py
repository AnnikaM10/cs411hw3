import pytest
from unittest.mock import patch
from meal_max.models import Meal, create_meal, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats, clear_meals
from meal_max.utils.sql_utils import get_db_connection


@pytest.fixture()
def meal():
    """Fixture to provide a new instance of Meal for each test."""
    return Meal(id=1, meal='Spaghetti', cuisine='Italian', price=12.99, difficulty='MED')

@pytest.fixture()
def mock_db_connection(mocker):
    """Mock database connection for tests that interact with the DB."""
    return mocker.patch('meal_max.utils.sql_utils.get_db_connection')

@pytest.fixture()
def sample_meal():
    """Fixture to provide a sample meal for creation tests."""
    return {
        "meal": "Tacos",
        "cuisine": "Mexican",
        "price": 10.99,
        "difficulty": "LOW"
    }

@pytest.fixture()
def sample_meal_with_invalid_price():
    """Fixture to provide a sample meal with invalid price."""
    return {
        "meal": "Tacos",
        "cuisine": "Mexican",
        "price": -10.99,
        "difficulty": "LOW"
    }

@pytest.fixture()
def sample_meal_with_invalid_difficulty():
    """Fixture to provide a sample meal with invalid difficulty."""
    return {
        "meal": "Tacos",
        "cuisine": "Mexican",
        "price": 10.99,
        "difficulty": "INVALID"
    }


##################################################
# Meal Creation Test Cases
##################################################

def test_create_meal(mock_db_connection, sample_meal):
    """Test the creation of a meal."""
    create_meal(**sample_meal)
    
    # Ensure the function interacts with the DB correctly
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_called_once()
    mock_db_connection.return_value.__enter__.return_value.commit.assert_called_once()

def test_create_meal_with_invalid_price(mock_db_connection, sample_meal_with_invalid_price):
    """Test creating a meal with an invalid price."""
    with pytest.raises(ValueError, match="Invalid price: -10.99. Price must be a positive number."):
        create_meal(**sample_meal_with_invalid_price)

def test_create_meal_with_invalid_difficulty(mock_db_connection, sample_meal_with_invalid_difficulty):
    """Test creating a meal with an invalid difficulty."""
    with pytest.raises(ValueError, match="Invalid difficulty level: INVALID. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(**sample_meal_with_invalid_difficulty)

def test_create_duplicate_meal(mock_db_connection, sample_meal):
    """Test creating a duplicate meal."""
    create_meal(**sample_meal)
    with pytest.raises(ValueError, match="Meal with name 'Tacos' already exists"):
        create_meal(**sample_meal)


##################################################
# Meal Deletion Test Cases
##################################################

def test_delete_meal(mock_db_connection, meal):
    """Test deleting a meal."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = [False]
    delete_meal(meal.id)
    
    # Ensure the meal was deleted in the database
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_called_with(
        "UPDATE meals SET deleted = TRUE WHERE id = ?", (meal.id,)
    )


def test_delete_non_existing_meal(mock_db_connection):
    """Test deleting a non-existing meal."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)


def test_delete_already_deleted_meal(mock_db_connection):
    """Test deleting a meal that has already been deleted."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = [True]
    with pytest.raises(ValueError, match="Meal with ID 1 has already been deleted"):
        delete_meal(1)


##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_meal_by_id(mock_db_connection, meal):
    """Test retrieving a meal by ID."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (1, 'Spaghetti', 'Italian', 12.99, 'MED', False)
    
    retrieved_meal = get_meal_by_id(meal.id)
    assert retrieved_meal.id == meal.id
    assert retrieved_meal.meal == meal.meal
    assert retrieved_meal.cuisine == meal.cuisine
    assert retrieved_meal.price == meal.price
    assert retrieved_meal.difficulty == meal.difficulty


def test_get_meal_by_id_not_found(mock_db_connection):
    """Test retrieving a meal by ID that doesn't exist."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)


def test_get_meal_by_name(mock_db_connection, meal):
    """Test retrieving a meal by name."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (1, 'Spaghetti', 'Italian', 12.99, 'MED', False)
    
    retrieved_meal = get_meal_by_name('Spaghetti')
    assert retrieved_meal.meal == meal.meal
    assert retrieved_meal.cuisine == meal.cuisine
    assert retrieved_meal.price == meal.price
    assert retrieved_meal.difficulty == meal.difficulty


def test_get_meal_by_name_not_found(mock_db_connection):
    """Test retrieving a meal by name that doesn't exist."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name 'Nonexistent' not found"):
        get_meal_by_name('Nonexistent')


##################################################
# Meal Stats Update Test Cases
##################################################

def test_update_meal_stats_win(mock_db_connection, meal):
    """Test updating meal stats with a win."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = [False]
    update_meal_stats(meal.id, 'win')

    # Ensure the DB is updated correctly
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_any_call(
        "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal.id,)
    )


def test_update_meal_stats_loss(mock_db_connection, meal):
    """Test updating meal stats with a loss."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = [False]
    update_meal_stats(meal.id, 'loss')

    # Ensure the DB is updated correctly
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_any_call(
        "UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal.id,)
    )


def test_update_meal_stats_invalid_result(mock_db_connection, meal):
    """Test updating meal stats with an invalid result."""
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
        update_meal_stats(meal.id, 'invalid')


##################################################
# Leaderboard Test Cases
##################################################

def test_get_leaderboard(mock_db_connection):
    """Test getting the leaderboard."""
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchall.return_value = [
        (1, 'Spaghetti', 'Italian', 12.99, 'MED', 5, 3, 0.6),
        (2, 'Tacos', 'Mexican', 10.99, 'LOW', 4, 2, 0.5)
    ]
    
    leaderboard = get_leaderboard(sort_by="wins")
    assert len(leaderboard) == 2
    assert leaderboard[0]['meal'] == 'Spaghetti'
    assert leaderboard[1]['meal'] == 'Tacos'


def test_get_leaderboard_invalid_sort(mock_db_connection):
    """Test getting the leaderboard with an invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")


##################################################
# Clear Meals Test Cases
##################################################

def test_clear_meals(mock_db_connection):
    """Test clearing all meals."""
    clear_meals()
    
    # Ensure the function interacts with the DB correctly
    mock_db_connection.return_value.__enter__.return_value.cursor.return_value.executescript.assert_called_once()

