import logging
import requests

from meal_max.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


def get_random() -> float:
    """
    Fetches a random number from random.org.

    This function makes an HTTP request to random.org to retrieve a random decimal
    fraction. It ensures that the response is valid and converts it to a float.

    Returns:
        float: A random number between 0 and 1 with two decimal places.

    Raises:
        RuntimeError: If the request to random.org fails or times out.
        ValueError: If the response from random.org cannot be converted to a float.

    """

    url = f"https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain&rnd=new"


    try:
        # Log the request to random.org
        logger.info("Fetching random number from %s", url)

        response = requests.get(url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = float(random_number_str)
        except ValueError:
            raise ValueError("Invalid response from random.org: %s" % random_number_str)

        logger.info("Received random number: %.3f", random_number)
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to random.org failed: %s", e)
        raise RuntimeError("Request to random.org failed: %s" % e)
