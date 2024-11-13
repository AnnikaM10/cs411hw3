from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any

from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Meal:
    id: int
    meal: str
    cuisine: str
    price: float
    difficulty: str

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.difficulty not in ['LOW', 'MED', 'HIGH']:
            raise ValueError("Difficulty must be 'LOW', 'MED', or 'HIGH'.")


def create_meal(meal: str, cuisine: str, price: float, difficulty: str) -> None:
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Invalid price: {price}. Price must be a positive number.")
    if difficulty not in ['LOW', 'MED', 'HIGH']:
        raise ValueError(f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
            """, (meal, cuisine, price, difficulty))
            conn.commit()

            logger.info("Meal successfully added to the database: %s", meal)

    except sqlite3.IntegrityError:
        logger.error("Duplicate meal name: %s", meal)
        raise ValueError(f"Meal with name '{meal}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

<<<<<<< Updated upstream

def delete_meal(meal_id: int) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has already been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            cursor.execute("UPDATE meals SET deleted = TRUE WHERE id = ?", (meal_id,))
            conn.commit()

            logger.info("Meal with ID %s marked as deleted.", meal_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_leaderboard(sort_by: str="wins") -> dict[str, Any]:
    query = """
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error("Invalid sort_by parameter: %s", sort_by)
        raise ValueError("Invalid sort_by parameter: %s" % sort_by)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            meal = {
                'id': row[0],
                'meal': row[1],
                'cuisine': row[2],
                'price': row[3],
                'difficulty': row[4],
                'battles': row[5],
                'wins': row[6],
                'win_pct': round(row[7] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(meal)

        logger.info("Leaderboard retrieved successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_meal_by_id(meal_id: int) -> Meal:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?", (meal_id,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def get_meal_by_name(meal_name: str) -> Meal:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?", (meal_name,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with name %s has been deleted", meal_name)
                    raise ValueError(f"Meal with name {meal_name} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with name %s not found", meal_name)
                raise ValueError(f"Meal with name {meal_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_meal_stats(meal_id: int, result: str) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            if result == 'win':
                cursor.execute("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal_id,))
            elif result == 'loss':
                cursor.execute("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal_id,))
            else:
                raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
        
from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Meal:
    """Represents a meal item with details including name, cuisine, price, and difficulty level.

    Attributes:
        id (int): Unique identifier for the meal.
        meal (str): Name of the meal.
        cuisine (str): Type of cuisine for the meal.
        price (float): Price of the meal.
        difficulty (str): Difficulty level of meal preparation.
    """
    id: int
    meal: str
    cuisine: str
    price: float
    difficulty: str

    def __post_init__(self):
        """Initializes a Meal instance and validates the price.

        Raises:
            ValueError: If price is negative.
        """
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.difficulty not in ['Easy', 'Medium', 'Hard']:
            raise ValueError("Difficulty must be 'Easy', 'Medium', or 'Hard'.")


def fetch_meal_from_db(meal_id: int) -> Meal:
    """Retrieves a meal from the database by its ID.

    Args:
        meal_id (int): The ID of the meal to retrieve.

    Returns:
        Meal: The Meal object retrieved from the database.

    Raises:
        sqlite3.DatabaseError: If a database error occurs during retrieval.
    """
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, meal, cuisine, price, difficulty FROM meals WHERE id = ?", (meal_id,))
        result = cursor.fetchone()
        if result:
            return Meal(*result)
        else:
            raise ValueError("Meal with specified ID does not exist.")
    except sqlite3.DatabaseError as e:
        logger.error("Database error occurred: %s", e)
        raise
    finally:
        connection.close()


def add_meal_to_db(meal: Meal) -> None:
    """Adds a new meal to the database.

    Args:
        meal (Meal): The Meal object to add to the database.

    Raises:
        sqlite3.DatabaseError: If a database error occurs during insertion.
    """
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO meals (id, meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?, ?)",
                       (meal.id, meal.meal, meal.cuisine, meal.price, meal.difficulty))
        connection.commit()
        logger.info("Meal added to database: %s", meal.meal)
    except sqlite3.DatabaseError as e:
        logger.error("Failed to add meal to database: %s", e)
        raise
    finally:
        connection.close()


def update_meal_in_db(meal: Meal) -> None:
    """Updates an existing meal in the database.

    Args:
        meal (Meal): The Meal object containing updated information.

    Raises:
        sqlite3.DatabaseError: If a database error occurs during update.
    """
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE meals
            SET meal = ?, cuisine = ?, price = ?, difficulty = ?
            WHERE id = ?
            """, (meal.meal, meal.cuisine, meal.price, meal.difficulty, meal.id)
        )
        connection.commit()
        logger.info("Meal updated in database: %s", meal.meal)
    except sqlite3.DatabaseError as e:
        logger.error("Failed to update meal in database: %s", e)
        raise
    finally:
        connection.close()


def delete_meal_from_db(meal_id: int) -> None:
    """Deletes a meal from the database by its ID.

    Args:
        meal_id (int): The ID of the meal to delete.

    Raises:
        sqlite3.DatabaseError: If a database error occurs during deletion.
    """
    connection = get_db_connection()
    try:
<<<<<<< HEAD
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            if result == 'win':
                cursor.execute("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal_id,))
            elif result == 'loss':
                cursor.execute("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal_id,))
            else:
                raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
        
=======
>>>>>>> Stashed changes
def clear_meals() -> None:
    """
    Recreates the meals table, effectively deleting all meals.

    Raises:
<<<<<<< Updated upstream
    sqlite3.Error: If any database error occurs.
=======
        sqlite3.Error: If any database error occurs.
>>>>>>> Stashed changes
    """
    try:
        with open(os.getenv("SQL_CREATE_TABLE_PATH", "/app/sql/create_meal_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            logger.info("Meals cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing meals: %s", str(e))
        raise e

<<<<<<< Updated upstream
=======
def delete_meal(meal_id: int) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has already been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            cursor.execute("UPDATE meals SET deleted = TRUE WHERE id = ?", (meal_id,))
            conn.commit()

            logger.info("Meal with ID %s marked as deleted.", meal_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_leaderboard(sort_by: str="wins") -> dict[str, Any]:
    query = """
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error("Invalid sort_by parameter: %s", sort_by)
        raise ValueError("Invalid sort_by parameter: %s" % sort_by)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            meal = {
                'id': row[0],
                'meal': row[1],
                'cuisine': row[2],
                'price': row[3],
                'difficulty': row[4],
                'battles': row[5],
                'wins': row[6],
                'win_pct': round(row[7] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(meal)

        logger.info("Leaderboard retrieved successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_meal_by_id(meal_id: int) -> Meal:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?", (meal_id,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def get_meal_by_name(meal_name: str) -> Meal:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?", (meal_name,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with name %s has been deleted", meal_name)
                    raise ValueError(f"Meal with name {meal_name} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with name %s not found", meal_name)
                raise ValueError(f"Meal with name {meal_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_meal_stats(meal_id: int, result: str) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            if result == 'win':
                cursor.execute("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal_id,))
            elif result == 'loss':
                cursor.execute("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal_id,))
            else:
                raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
>>>>>>> Stashed changes
=======
        cursor = connection.cursor()
        cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
        connection.commit()
        logger.info("Meal deleted from database with ID: %d", meal_id)
    except sqlite3.DatabaseError as e:
        logger.error("Failed to delete meal from database: %s", e)
        raise
    finally:
        connection.close()
>>>>>>> origin/main
