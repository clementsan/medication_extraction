"""
External medication validation - openfda API
"""

import logging
from typing import Any, Dict
import requests


logger = logging.getLogger(__name__)


def openfda_query(medication_name: str) -> bool:
    """
    OpenFDA API Query - Structure Product Labeling
    Notes: Validates medication name existence via OpenFDA database
    Args:
      - Name of medication
    Returns:
      - Boolean based on medication name existence (successful query)
    """

    # OpenFDA API query
    api_query = f'https://api.fda.gov/drug/label.json?search=openfda.brand_name.exact="{medication_name}"&limit=1'
    logger.debug("\t API query: %s", api_query)

    response = requests.get(api_query, timeout=5)
    data = response.json()
    results = data.get("results", [])

    if response.status_code == 200 and len(results) != 0:
        medication_name_valid = True
    elif response.status_code == 404 and data["error"]["code"] == "NOT_FOUND":
        logger.warning("\t Medication name: %s", medication_name)
        logger.warning("\t API error code: %s", data["error"]["code"])
        medication_name_valid = False
    else:
        logger.warning(
            "\t API request failed with status code: %d", response.status_code
        )
        medication_name_valid = False

    return medication_name_valid


def validate_medication(json_object: Dict[str, Any]) -> Dict[str, Any]:
    """Medication name validation - via openFDA database"""
    medication_list = json_object["medications"]
    for _, item in enumerate(medication_list):
        medication_name = item["medication"]
        logger.debug("\t Medication name: %s", medication_name)
        medication_name_valid = openfda_query(medication_name)
        logger.debug("\t Medication name - validation: %d", medication_name_valid)

        # Add / replace json value
        item["validated"] = medication_name_valid

    return json_object
