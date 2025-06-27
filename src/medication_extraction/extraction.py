"""
Data extraction
"""

import os
import json
import logging
from typing import Any, Dict

from medication_extraction import schema
from medication_extraction import utils

logger = logging.getLogger(__name__)


def generate_llm_prompt(context: str) -> str:
    """Define user prompt with context, leveraging prompt template file"""

    # Read prompt template file
    prompt_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "prompt_template.json"
    )
    prompt_dict = utils.read_json_file(prompt_file)
    # Add context to prompt
    prompt_template = prompt_dict["prompt"]
    logger.debug("Prompt template (without context): \n%s", prompt_template)
    prompt = prompt_template.format(context=context)

    return prompt


def llm_extraction(
    text_model: str, mistral_client: object, pdf_content: str
) -> Dict[str, Any]:
    """Data extraction via LLM"""

    prompt = generate_llm_prompt(pdf_content)

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    # Use of function "parse" to require specific structure output
    chat_response = mistral_client.chat.parse(
        model=text_model,
        messages=messages,
        response_format=schema.MedicalReport,
        temperature=0,
    )

    json_response = json.loads(chat_response.choices[0].message.content)

    return json_response
