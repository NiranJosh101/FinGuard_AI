import json
import logging
from typing import Dict, Any
from src.config import settings

logger = logging.getLogger(__name__)

def load_profile(profile_path: str = settings.MOCK_PROFILE_PATH) -> Dict[str, Any]:
    """
    Loads the mock user profile from a JSON file.
    In a live microservice, this would pull or cache data from an analytical DB.
    """
    try:
        with open(profile_path, "r") as file:
            profile_data = json.load(file)
            logger.info(f"Successfully loaded mock profile for user: {profile_data.get('user_id')}")
            return profile_data
    except FileNotFoundError:
        logger.error(f"Profile file not found at path: {profile_path}. Falling back to empty profile.")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON structure inside profile file at: {profile_path}.")
        return {}