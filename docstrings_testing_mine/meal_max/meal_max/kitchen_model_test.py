from contextlib import contextmanager
import sqlite3
import pytest
from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor

######################################################
#
#    Tests for Meal Creation
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal."""
    create_meal(meal="Spaghetti", cuisine="Italian", price=15.5, difficulty="MED")

    expected_query = """
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """
    actual_query = mock_cursor.execute.call_args[0][0]

    assert expected_query.strip() == actual_query.strip(), "The SQL query did not match the expected structure."
    assert mock_cursor.execute.call_args[0][1] == ("Spaghetti", "Italian", 15.5, "MED")

def test_create_meal_invalid_price():
    """Test creating a meal with an invalid price."""
    with pytest.raises(ValueError, match="Invalid price: -10. Price must be a positive number."):
        create_meal(meal="Pizza", cuisine="Italian", price=-10, difficulty="LOW")

def test_create_meal_invalid_difficulty():
    """Test creating a meal with an invalid difficulty level."""
    with pytest.raises(ValueError, match="Invalid difficulty level: EXPERT. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Pizza", cuisine="Italian", price=20, difficulty="EXPERT")

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name."""
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("Duplicate entry")

    with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
        create_meal(meal="Pizza", cuisine="Italian", price=20, difficulty="LOW")

######################################################
#
#    Tests for Clearing Meals
#
######################################################

def test_clear_meals(mock_cursor, mocker):
    """Test clearing all meals from the catalog."""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': '/app/sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="CREATE TABLE meals..."))

    clear_meals()

    mock_open.assert_called_once_with('/app/sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()

######################################################
#
#    Tests for Deleting Meals
#
######################################################

def test_delete_meal(mock_cursor):
    """Test deleting a meal by its ID."""
    mock_cursor.fetchone.return_value = [False]  # Meal exists and is not deleted

    delete_meal(1)

    expected_select_query = "SELECT deleted FROM meals WHERE id = ?"
    expected_update_query = "UPDATE meals SET deleted = TRUE WHERE id = ?"
    
    actual_select_query = mock_cursor.execute.call_args_list[0][0][0]
    actual_update_query = mock_cursor.execute.call_args_list[1][0][0]

    assert actual_select_query.strip() == expected_select_query.strip()
    assert actual_update_query.strip() == expected_update_query.strip()
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_delete_meal_not_found(mock_cursor):
    """Test deleting a meal that does not exist."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test deleting a meal that has already been marked as deleted."""
    mock_cursor.fetchone.return_value = [True]  # Meal is already deleted

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

######################################################
#
#    Tests for Retrieving Meals
#
######################################################

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by its ID."""
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 20.0, "LOW", False)

    meal = get_meal_by_id(1)

    assert meal == Meal(1, "Pizza", "Italian", 20.0, "LOW")
    assert mock_cursor.execute.call_args[0][1] == (1,)

def test_get_meal_by_id_not_found(mock_cursor):
    """Test retrieving a meal by an ID that does not exist."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by its name."""
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 20.0, "LOW", False)

    meal = get_meal_by_name("Pizza")

    assert meal == Meal(1, "Pizza", "Italian", 20.0, "LOW")
    assert mock_cursor.execute.call_args[0][1] == ("Pizza",)

def test_get_meal_by_name_not_found(mock_cursor):
    """Test retrieving a meal by a name that does not exist."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name 'Sushi' not found"):
        get_meal_by_name("Sushi")

######################################################
#
#    Tests for Updating Meal Stats
#
######################################################

def test_update_meal_stats_win(mock_cursor):
    """Test updating a meal's statistics with a 'win' result."""
    mock_cursor.fetchone.return_value = [False]  # Meal is not deleted

    update_meal_stats(1, 'win')

    expected_query = "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?"
    assert mock_cursor.execute.call_args_list[1][0][0].strip() == expected_query.strip()
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_update_meal_stats_loss(mock_cursor):
    """Test updating a meal's statistics with a 'loss' result."""
    mock_cursor.fetchone.return_value = [False]  # Meal is not deleted

    update_meal_stats(1, 'loss')

    expected_query = "UPDATE meals SET battles = battles + 1 WHERE id = ?"
    assert mock_cursor.execute.call_args_list[1][0][0].strip() == expected_query.strip()
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test updating stats for a meal that has been deleted."""
    mock_cursor.fetchone.return_value = [True]  # Meal is marked as deleted

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, 'win')

def test_update_meal_stats_invalid_result():
    """Test updating a meal's statistics with an invalid result."""
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, 'draw')

######################################################
#
#    Tests for Getting the Leaderboard
#
######################################################

def test_get_leaderboard(mock_cursor):
    """Test retrieving the leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [
        (1, "Pizza", "Italian", 20.0, "LOW", 10, 7, 0.7),
        (2, "Sushi", "Japanese", 25.0, "MED", 5, 4, 0.8)
    ]

    leaderboard = get_leaderboard(sort_by="wins")

    expected_leaderboard = [
        {'id': 1, 'meal': "Pizza", 'cuisine': "Italian", 'price': 20.0, 'difficulty': "LOW", 'battles': 10, 'wins': 7, 'win_pct': 70.0},
        {'id': 2, 'meal': "Sushi", 'cuisine': "Japanese", 'price': 25.0, 'difficulty': "MED", 'battles': 5, 'wins': 4, 'win_pct': 80.0}
    ]

    assert leaderboard == expected_leaderboard

def test_get_leaderboard_invalid_sort_by():
    """Test retrieving the leaderboard with an invalid sort_by parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")
