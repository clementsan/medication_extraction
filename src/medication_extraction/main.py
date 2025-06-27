"""
Main module - Command Line Interface
"""

import logging
from dataclasses import dataclass
import typer
from typing_extensions import Annotated


from medication_extraction import pipeline


@dataclass
class ModelConfig:
    """Configuration for OCR and LLM models."""
    ocr_model: str = "mistral-ocr-latest"
    text_model: str = "mistral-8b-latest"


app = typer.Typer()


@app.command()
def main(
    input_pdf: str = typer.Option(..., "--input-pdf", help="Input PDF file"),
    output_dir: str = typer.Option(..., "--output-dir", help="Output folder"),
    qc_ocr: Annotated[
        bool, typer.Option(help="Quality Control - save OCR output file")
    ] = False,
    direct_qna: Annotated[
        bool, typer.Option(help="Direct Question & Answer - OCR + LLM combined")
    ] = False,
    model_config: ModelConfig = typer.Option(
        ModelConfig(), "--model-config", help="Model configuration"
    ),
):
    """Main command"""
    logging.basicConfig(level=logging.INFO)
    config = pipeline.ExtractorConfig(
        input_pdf=input_pdf,
        output_dir=output_dir,
        qc_ocr=qc_ocr,
        direct_qna=direct_qna,
        ocr_model=model_config.ocr_model,
        text_model=model_config.text_model,
    )
    data_extractor = pipeline.MedicalDataExtractor(config)
    data_extractor.run_workflow()


if __name__ == "__main__":
    app()
