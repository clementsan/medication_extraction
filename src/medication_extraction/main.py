"""
Main module - Command Line Interface
"""

import logging
import typer
from typing_extensions import Annotated


from . import pipeline


app = typer.Typer()


@app.command()
def main(
    input_pdf: Annotated[str, typer.Option(help="Input PDF file")],
    output_dir: Annotated[str, typer.Option(help="Output folder")],
    ocr_model: Annotated[str, typer.Option(help="OCR model")] = "mistral-ocr-latest",
    text_model: Annotated[str, typer.Option(help="LLM model")] = "ministral-8b-latest",
    qc_ocr: Annotated[
        bool, typer.Option(help="Quality Control - save OCR output file")
    ] = False,
    direct_qna: Annotated[
        bool, typer.Option(help="Direct Question & Answer - OCR + LLM combined")
    ] = False,
    rag: Annotated[
        bool, typer.Option(help="Perform Retrieval Augmented Generation (RAG)")
    ] = False,
):
    """Main command"""
    logging.basicConfig(level=logging.INFO)
    data_extractor = pipeline.MedicalDataExtractor(
        input_pdf=input_pdf,
        output_dir=output_dir,
        ocr_model=ocr_model,
        text_model=text_model,
        qc_ocr=qc_ocr,
        direct_qna=direct_qna,
        rag=rag,
    )
    data_extractor.run_workflow()


if __name__ == "__main__":
    app()
