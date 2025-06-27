"""
Utility functions
"""

import os
import json
import base64
import logging
from typing import Any, Dict
from dotenv import load_dotenv, find_dotenv


logger = logging.getLogger(__name__)


def retrieve_api(key_type: str) -> str:
    """Retrieve API Key"""
    logger.debug("\t Retrieving API Key...")

    _ = load_dotenv(find_dotenv())
    api_key = os.environ.get(key_type)
    if not api_key:
        raise Exception(f"API key {key_type} not found!")
    return api_key


def encode_pdf(pdf_file: str) -> str:
    """Encode the pdf file to base64"""

    if not os.path.exists(pdf_file):
        raise Exception(f"File {pdf_file} not found!")

    with open(pdf_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def read_markdown_file(input_path: str) -> str:
    """Read Markdown file"""
    logger.debug("\t Reading markdown file...")

    if not os.path.exists(input_path):
        raise Exception(f"File {input_path} not found!")

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    return content


def save_markdown_file(text: str, output_path: str):
    """Save text to a file"""
    logger.debug("\t Saving extracted text to a file...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def read_json_file(input_path: str):
    """Read json file"""
    logger.debug("\t Reading json file...")

    if not os.path.exists(input_path):
        raise Exception(f"File {input_path} not found!")

    with open(input_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    return content


def save_json_file(json_object: Dict[str, Any], output_path: str):
    """Save json object to a file"""
    logger.debug("\t Saving json object to a file...")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_object, f, indent=4)
