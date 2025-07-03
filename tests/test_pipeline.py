"""
Testing pipeline module
"""

import os
from pathlib import Path
import pytest

from src.medication_extraction import pipeline
from src.medication_extraction import utils


@pytest.fixture
def cli_arguments():
    """Fixture - cli arguments on example data"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(test_dir, "data_example")
    input_pdf = os.path.join(data_dir, "Example_MedicalReport.pdf")
    return input_pdf, data_dir


@pytest.fixture
def output_files(cli_arguments):
    """Fixture - output files from example data"""
    input_pdf, output_dir = cli_arguments
    base_name = Path(input_pdf).stem
    output_path = Path(output_dir).absolute()
    output_json_file = os.path.join(output_path, f"{base_name}_medication.json")
    output_md_file = os.path.join(output_path, f"{base_name}_medication.md")
    return output_json_file, output_md_file


def test_run_workflow(cli_arguments, output_files):
    """Test run_workflow function"""
    input_pdf, output_dir = cli_arguments
    output_json_file, output_md_file = output_files

    data_extractor = pipeline.MedicalDataExtractor(
        input_pdf=input_pdf,
        output_dir=output_dir,
        ocr_model="mistral-ocr-latest",
        text_model="ministral-3b-latest",
    )
    data_extractor.run_workflow()

    assert os.path.exists(output_json_file)
    assert os.path.exists(output_md_file)

    output_json = utils.read_json_file(output_json_file)
    assert output_json["patient_info"]["name"] == "Jane Doe"
    assert output_json["medications"][0]["medication"] == "Aspirin"
    assert output_json["medications"][0]["dosage"] == "10 mg Daily"
