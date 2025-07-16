"""
Schema module - data schema
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from typing import Optional


class MedicationItem(BaseModel):
    """Medication item class"""

    medication: str = Field(
        description="Medication administered, medication at discharge",
        # description="Medication name",
        examples=["Medication", "Lisinopril"],
    )
    dosage: str = "None"
    dosage_info: str = Field(
        description="Dosage (no frequency, no route)",
        # description="Dosage",
        examples=["1mg", "10 mg"],
    )
    frequency_info: str = Field(
        description="Frequency",
        example="Daily",
    )
    # Warning: define validated as string (to avoid LLM issues)
    validated: str = "None"
    additional_information: dict = Field(
        description="Supplementary data about the medication, only when available (e.g. route)",
        examples=[{"route": "route"}, {}],
    )


# New experiments
# class MedicationItem(BaseModel):
#     """Medication item class"""
#
#     medication: str = Field(
#         description="Name of medication, name of medication administered, name of medication at discharge",
#     )
#     dosage: str = "None"
#     dosage_info: str = Field(
#         description="Dosage (no frequency, no route)",
#         examples=["1mg"],
#     )
#     frequency_info: str = Field(
#         description="Frequency",
#         examples=["Daily"],
#     )
#     # Warning: define validated as string (to avoid LLM issues)
#     validated: str = "None"
#     additional_information: dict[str, str] = Field(
#         description="Supplementary data about the medication, only when available (e.g. route, indication)",
#         examples=[{"route": "route"}, {"indication": "indication"}, {}],
#         default={},
#     )


class PatientInfo(BaseModel):
    """Patient Info class"""

    name: str = Field(description="Patient Name")
    dob: str = Field(description="Patient Date of Birth")
    age: int = Field(description="Patient age in years")
    gender: str = Field(description="Patient gender")
    mrn: str = Field(description="Patient MRN (Medical Record Number)")
    admission_date: str = Field(description="Date of Admission")
    discharge_date: str = Field(description="Date of Discharge")


class MedicalReport(BaseModel):
    """Medical report class"""

    patient_info: PatientInfo
    medications: List[MedicationItem]


def clean_json(json_object: Dict[str, Any]) -> str:
    """Post-process JSON object (based on output requirements)"""
    medication_list = json_object["medications"]
    for _, item in enumerate(medication_list):
        item["dosage"] = item["dosage_info"] + ' ' + item["frequency_info"]
        item.pop("dosage_info", None)
        item.pop("frequency_info", None)
    return json_object

def convert_json_to_md(json_object: Dict[str, Any]) -> str:
    """Convert json object to Markdown format"""
    patient_info = json_object["patient_info"]
    markdown_output = "## Patient Information\n"
    markdown_output += f"- **Name**: {patient_info['name']}\n\n"
    markdown_output += f"- **DOB**: {patient_info['dob']}\n\n"
    markdown_output += f"- **Age**: {patient_info['age']}\n\n"
    markdown_output += f"- **Gender**: {patient_info['gender']}\n\n"
    markdown_output += f"- **MRN**: {patient_info['mrn']}\n\n"
    markdown_output += (
        f"- **Date of Administration**: {patient_info['admission_date']}\n\n"
    )
    markdown_output += f"- **Date of Discharge**: {patient_info['discharge_date']}\n\n"

    medication_list = json_object["medications"]
    markdown_output += "### Extracted Medications and Dosages\n\n"
    for _, item in enumerate(medication_list):
        markdown_output += f"- **Medication**: {item['medication']}\n\n"
        markdown_output += f"  **Dosage**: {item['dosage']}\n\n"
        markdown_output += f"  **Validated**: {item['validated']}\n\n"
        dict_info = item["additional_information"]
        if len(dict_info) == 0:
            markdown_output += "  **Additional Information**: None\n\n"
        else:
            markdown_output += "  **Additional Information**:\n\n"
            for key, value in dict_info.items():
                markdown_output += f"  - **{key.capitalize()}**: {value}\n\n"
    return markdown_output
