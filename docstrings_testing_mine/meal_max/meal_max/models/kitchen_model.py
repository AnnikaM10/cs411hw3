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
        cursor = connection.cursor()
        cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
        connection.commit()
        logger.info("Meal deleted from database with ID: %d", meal_id)
    except sqlite3.DatabaseError as e:
        logger.error("Failed to delete meal from database: %s", e)
        raise
    finally:
        connection.close()
