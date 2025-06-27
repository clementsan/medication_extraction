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


def generate_llm_prompt(prompt_type: str, context: str = "") -> str:
    """
    Generate LLM prompt, leveraging prompt template file
    Args:
        - prompt_type: select specific prompt from JSON file
        - context: optional context
    Returns:
        - LLM prompt
    """

    # Read prompt template file
    prompt_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "prompt_template.json"
    )
    prompt_dict = utils.read_json_file(prompt_file)

    # Select specific prompt
    prompt_template = prompt_dict[prompt_type]
    logger.debug("Prompt template: \n%s", prompt_template)

    # Optional - Add context to prompt
    if context:
        prompt_template = prompt_template.format(context=context)

    return prompt_template


def llm_extraction(
    text_model: str, mistral_client: object, pdf_content: str
) -> Dict[str, Any]:
    """Data extraction via LLM"""

    prompt = generate_llm_prompt(prompt_type="prompt_context", context=pdf_content)

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


def llm_qna(
    text_model: str, mistral_client: object, pdf_file: str
) -> Dict[str, Any]:
    """Direct document Question & Answer - OCR + LLM combined"""

    prompt = generate_llm_prompt(prompt_type="prompt_doc", context="")

    # Getting the base64 string encoding
    base64_pdf = utils.encode_pdf(pdf_file)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}",
                    "include_image_base64": True
                }
            ]
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
