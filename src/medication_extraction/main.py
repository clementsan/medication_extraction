"""
Main module - Command Line Interface
"""

import logging
import typer
from typing_extensions import Annotated


from medication_extraction import pipeline


app = typer.Typer()


@app.command()
def main(
    input_pdf: str = typer.Option(..., "--input_pdf"),
    output_dir: str = typer.Option(..., "--output-dir"),
    qc_ocr: Annotated[
        bool, typer.Option(help="Quality Control - save OCR output")
    ] = False,
    direct_qna: Annotated[
        bool, typer.Option(help="Direct Question & Answer - OCR + LLM")
    ] = False,
    ocr_model: str = typer.Option("mistral-ocr-latest", "--ocr-model"),
    text_model: str = typer.Option("ministral-8b-latest", "--text-model"),
):
    """Main command"""
    logging.basicConfig(level=logging.INFO)
    data_extractor = pipeline.MedicalDataExtractor(
        input_pdf=input_pdf,
        output_dir=output_dir,
        qc_ocr=qc_ocr,
        direct_qna=direct_qna,
        ocr_model=ocr_model,
        text_model=text_model,
    )
    data_extractor.run_workflow()


if __name__ == "__main__":
    app()
