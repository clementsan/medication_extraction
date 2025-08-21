"""
Data extraction
"""

import os
import json
import logging
from typing import Any, Dict

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_mistralai import MistralAIEmbeddings

from . import schema
from . import utils
from .phoenix_tracer import tracer


logger = logging.getLogger(__name__)


def retrieve_llm_prompt(prompt_type: str) -> str:
    """
    Retrieve LLM prompt, leveraging prompt template file
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

    return prompt_template


@tracer.chain
def doc_retrieval(pdf_content: str, query) -> str:
    """
    Perform doc retrieval using mistral embedding and chromadb vector database
    Args:
        - pdf_content: input document
        - query: user query for document retrieval
    Returns:
        - retrieved content
    """

    # Step 1 - Split PDF content based on markdown content
    headers_to_split_on = [
        ("#", "Header 1"),
        # ("##", "Header 2"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on, strip_headers=False
    )
    md_header_splits = markdown_splitter.split_text(pdf_content)
    logger.debug("\nNumber document splits: %d", len(md_header_splits))

    # Step 2 - Generate embeddings for each text chunk (via Mistral Embeddings API)
    text_embeddings = MistralAIEmbeddings(model="mistral-embed")

    # Step 3- Add embeddings to in-memory vector store
    vector_store = InMemoryVectorStore(text_embeddings)
    # Index chunks
    _ = vector_store.add_documents(documents=md_header_splits)

    # Step 4 - Perform document retrieval via similarity search on query
    retrieved_docs = vector_store.similarity_search(query, k=4)
    retrieved_results = "\n\n".join(doc.page_content for doc in retrieved_docs)

    return retrieved_results


@tracer.chain
def llm_extraction(
    text_model: str, mistral_client: object, pdf_content: str, rag: bool = False
) -> Dict[str, Any]:
    """
    Data extraction via LLM
    Args:
        - text_model: LLM text model
        - mistral_client: mistral client
        - pdf_content: input document
        - rag: optional retrieval strategy
    Returns:
        - LLM response
    """

    # Retrieve prompt from template
    prompt = retrieve_llm_prompt(prompt_type="prompt_context")

    # Option to perform Retrieval Augmented Generation
    if rag:
        logger.info("\t Performing document retrieval")
        context = doc_retrieval(pdf_content, prompt)
        logger.debug("\nRetrieved context: \n %s", context)
    else:
        context = pdf_content

    # Optional - Add context to prompt (full pdf_content or retrieved context)
    if context:
        prompt = prompt.format(context=context)

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


@tracer.chain
def llm_qna(text_model: str, mistral_client: object, pdf_file: str) -> Dict[str, Any]:
    """
    Direct document Question & Answer - OCR + LLM combined
    Args:
        - text_model: LLM text model
        - mistral_client: mistral client
        - pdf_file: input PDF document
    Returns:
        - LLM response
    """

    prompt = retrieve_llm_prompt(prompt_type="prompt_doc")

    # Getting the base64 string encoding
    base64_pdf = utils.encode_pdf(pdf_file)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}",
                    "include_image_base64": True,
                },
            ],
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
