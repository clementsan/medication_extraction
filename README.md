# Project: Medication extraction from PDF reports

**Aims:**
This project aims to extract accurate medical information (e.g. medication with dosage) from PDF medical records. I opted for a workflow leveraging both OCR and LLM models.


**Components:** 
 - Use of Command Line Interface (CLI) via Typer library
 - Use of Mistral OCR and LLM models for data extraction
 - Use of OpenFDA database for external data validation


---
### Data science pipeline

**Data science pipeline:**
- Stage 1 - Optical Character Recognition (OCR) on PDF file
- Stage 2 - Specific data extraction via LLM (e.g. medications)
- Stage 3 - Medication validation via external OpenFDA API
- Stage 4 - Saving output files (markdown and json files)


---
### Source code structure

**Source code structure:**
- `main.py`: main module for command line interface
- `pipeline.py`: general data science pipeline
- `ocr.py`: Optical Character Recognition (OCR) stage
- `extraction.py`: specific data extraction stage via LLM
- `schema.py`: data schema used for data extraction
- `validation.py`: data validation stage (via external API)
- `utils.py`: utility functions


---
## Installation

Create your local python environment (via conda, poetry...) and install local package (via `pip install` or `poetry install`)

Example via pip:
 > pip install .

Example via poetry:
 > poetry install 


---
## Usage

**WARNING:** `MISTRAL_API_KEY` needs to be set in your environment, in order to run Mistal OCR and LLM models.

Application arguments:
 - `input_pdf`: PDF file with medical information
 - `output-dir`: Output folder (where JSON and Markdown files are saved)

Application options:
 - `qc-ocr`: Save OCR output in Markdown file 
 - `direct-qna`: Use direct Question&Answer step (OCR + LLM)
 - `ocr-model`: Select OCR model (Mistral OCR)
 - `text-model`: Select LLM text model (Mistral LLM models)


Example command line via python file:
> python src/medication_extraction/main.py --input_pdf <pdf_file> --output-dir <output_dir>

Example command line after local installation:
> medication-extraction --input_pdf <pdf_file> --output-dir <output_dir>

Example command line with quality control on OCR (saving OCR output file):
> medication-extraction --input_pdf <pdf_file> --output-dir <output_dir> --qc-ocr

Example command line with direct Question&Answer (OCR + LLM combined):
> medication-extraction --input_pdf <pdf_file> --output-dir <output_dir> --direct-qna

Example command line with new LLM model:
> medication-extraction --input_pdf <pdf_file> --output-dir <output_dir> --llm-model mistral-small-latest

---
## Advanced Notes

### Notes on OCR

This project leverages [Mistral OCR](https://mistral.ai/news/mistral-ocr) for Optical Character Recognition. It helps pre-process the PDF documents, reading tables accurately, and structuring them appropriately for subsequent LLM usage.  


### Notes on LLM

This project leverages Mistral LLMs. I compared several LLM models:
 - `ministral-3b-latest`: fast but not fully precise
 - `ministral-8b-latest`: fast and precise (good compromise)
 - `mistral-small-latest`: slow but more accurate (without a cleaning step)

I used an LLM temperature of 0, to enforce a more deterministic output.


### Notes on LLM prompting

I created prompt templates available in the following json file (`prompt_template.json`), to extract specific medication information (medication name, and medication administration).

The prompts provide clear and concise instructions: defining a specific task, adding context as a variable (i.e. data from PDF document), and asking for a JSON object as output format.

Prompt examples:
 - `prompt_context`: prompt allowing additional context information (as variable)
 - `prompt_doc`: prompt used when directly uploading a document (use of `direct-qna` option)

In addition, I used specific pydantic models to define a clear JSON schema. It helps ensure the LLM model provides consistent structured responses (following this custom JSON structure). In that regard, I used the `client.chat.parse` function from Mistral AI (instead of the more general `client.chat.complete` function).



### Notes on external data validation

To validate medication names retrieved from documents, I used the external [OpenFDA database](https://open.fda.gov/apis/). I performed API queries on Product Labeling, to assess if medication names are valid.

From the openFDA website: "Drug manufacturers and distributors submit documentation about their products to FDA in the Structured Product Labeling (SPL) format. The openFDA drug product labeling API returns data from this dataset."


### Notes on data extraction (and related challenges)

As a general note, we aim to extract medication from medical PDF reports. However, medication information can be found multiple times in these documents (e.g. general medication, medication from patient history, medication administered during hospital stay, and medication at discharge). I focused on the latter two components (medication administered, and medication at discharge) to be more specific in my data extraction task.

As a more specific note, `medication administration instructions`, combines both `medication dosage` and `medication frequency`. They are defined as two independent items in medical reports.
It is not easy for an LLM to extract these items and combine them directly into one single variable. I noticed variations in such outputs, either based on various document reports, or based on LLM models being used.
An easier workflow uses a two-step process (extracting both 'dosage' and 'frequency', and then combining them in a post-processing step, if the output needs to be a single JSON variable).
