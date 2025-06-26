"""
Optical Character Recognition
"""

import os
import base64


def encode_pdf(pdf_file: str) -> bytes:
    """Encode the pdf file to base64"""

    if not os.path.exists(pdf_file):
        raise Exception(f"File {pdf_file} not found!")

    with open(pdf_file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def ocr_processor(pdf_file: str, mistral_client: object, ocr_model: str) -> str:
    """OCR on PDF file"""

    # Getting the base64 string
    base64_pdf = encode_pdf(pdf_file)

    ocr_response = mistral_client.ocr.process(
        model=ocr_model,
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_pdf}",
        },
        include_image_base64=True,
    )

    # Manage OCR output - combine text blocks and add page numbers
    pdf_content = []
    for idx, page in enumerate(ocr_response.pages):
        pdf_content.append(page.markdown)
        pdf_content.append(f"\n### Page {idx+1}\n")
        pdf_content.append("\n\n")

    return "\n".join(pdf_content)
