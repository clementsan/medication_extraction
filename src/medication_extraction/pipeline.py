"""
Pipeline module - main analysis
"""

import os
from pathlib import Path
import logging
from typing import Tuple, Any, Dict

from mistralai import Mistral

from . import extraction
from . import ocr
from . import schema
from . import utils
from . import validation


logger = logging.getLogger(__name__)


class MedicalDataExtractor:
    """Medical data extractor class"""

    def __init__(
        self,
        input_pdf: str,
        output_dir: str,
        ocr_model: str,
        text_model: str,
        qc_ocr: bool = False,
        direct_qna: bool = False,
        rag: bool = False,
    ):
        self.input_pdf = input_pdf
        self.output_dir = output_dir
        self.ocr_model = ocr_model
        self.text_model = text_model
        self.qc_ocr = qc_ocr
        self.direct_qna = direct_qna
        self.rag = rag
        self.client = self.define_mistral_client()
        self.output_ocr_file, self.output_json_file, self.output_md_file = (
            self.define_output_files()
        )

    @staticmethod
    def define_mistral_client() -> object:
        """Initialize mistral client api"""
        # Retrieve API key
        mistral_api_key = utils.retrieve_api("MISTRAL_API_KEY")
        # Define Mistral client
        client = Mistral(api_key=mistral_api_key)
        return client

    def define_output_files(self) -> Tuple[str, str, str]:
        """Define output files (*ocr.md, *medication.json, *medication.md)"""
        base_name = Path(self.input_pdf).stem
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = Path(self.output_dir).absolute()
        output_ocr_file = os.path.join(output_path, f"{base_name}_ocr.md")
        output_json_file = os.path.join(output_path, f"{base_name}_medication.json")
        output_md_file = os.path.join(output_path, f"{base_name}_medication.md")
        return output_ocr_file, output_json_file, output_md_file

    def perform_ocr(self) -> str:
        """Perform OCR on the PDF file"""
        logger.info("Stage 1 - Performing OCR on PDF file")
        pdf_content = ocr.ocr_processor(self.input_pdf, self.client, self.ocr_model)
        return pdf_content

    def save_ocr_output(self, pdf_content: str):
        """Save OCR output to a markdown file if QC is enabled"""
        logger.info("\t Saving OCR output to markdown file")
        utils.save_markdown_file(pdf_content, self.output_ocr_file)

    def extract_data(self, pdf_content: str) -> Dict[str, Any]:
        """Extract data using LLM model"""
        logger.info("Stage 2 - Data extraction via LLM")
        medication_json = extraction.llm_extraction(
            self.text_model, self.client, pdf_content, self.rag
        )
        logger.info("\t Cleaning LLM JSON output")
        medication_json = schema.clean_json(medication_json)
        return medication_json

    def doc_qna(self) -> Dict[str, Any]:
        """Direct document Question & Answer - OCR + LLM combined"""
        logger.info("Stage 1 & 2 - OCR + LLM data extraction")
        medication_json = extraction.llm_qna(
            self.text_model, self.client, self.input_pdf
        )
        logger.info("\t Cleaning LLM JSON output")
        medication_json = schema.clean_json(medication_json)
        return medication_json

    @staticmethod
    def validate_data(medication_json: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data using OpenFDA API"""
        logger.info("Stage 3 - Data validation via OpenFDA API")
        medication_json_valid = validation.validate_medication(medication_json)
        return medication_json_valid

    def save_output_files(self, medication_json_valid: Dict[str, Any]):
        """Save validated data to JSON and Markdown files"""
        logger.info("Stage 4 - Saving output files")
        utils.save_json_file(medication_json_valid, self.output_json_file)
        medication_md_valid = schema.convert_json_to_md(medication_json_valid)
        utils.save_markdown_file(medication_md_valid, self.output_md_file)

    def run_workflow(self):
        """
        Main workflow:
          - Stage 1 - OCR on PDF
          - Stage 2 - Data extraction
          - Stage 3 - Data validation
          - Stage 4 - Saving output files
        """
        print("----------")
        print("MEDICAL DATA EXTRACTION")
        print("----------")

        if self.direct_qna:
            medication_json = self.doc_qna()
        else:
            # Stage 1 - Perform OCR on PDF file
            pdf_content = self.perform_ocr()

            # Optional - Save OCR output file
            if self.qc_ocr:
                self.save_ocr_output(pdf_content)

            # Stage 2 - Data extraction
            medication_json = self.extract_data(pdf_content)

        # Stage 3 - Data validation
        medication_json_valid = self.validate_data(medication_json)

        # Stage 4 - Save output files
        self.save_output_files(medication_json_valid)
