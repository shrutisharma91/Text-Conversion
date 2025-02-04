from typing import Optional, List, Dict
from pydantic import BaseModel

# Define the model for the request body that the API expects
class TextToPDFRequest(BaseModel):
    lesson_plan_data: str  # JSON string containing lesson plan data
    output_file_name: str  # The name of the output file for the PDF


class TextToDocxRequest(BaseModel):
    lesson_plan_data: str  # JSON string containing lesson plan data
    output_file_name: str
    


class TextTopptRequest(BaseModel):
    text: str
    output_file_name: str
    
