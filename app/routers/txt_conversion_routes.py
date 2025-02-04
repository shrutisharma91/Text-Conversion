from fastapi import APIRouter, Depends, Form
from fastapi.responses import FileResponse
import app.models.model_types as model_type
import app.controllers.txt_conversion_controller as controller
from app.utils.conversion.ppt import generate_presentation, refine_ppt_content
import json

router = APIRouter()

@router.post("/convert-text-to-pdf")
async def convert_text2pdf(
    request: model_type.TextToPDFRequest = Depends()
):
    try:
        # Pass the request to the controller
        retrieved_data = await controller.convert_text2pdf(request)
        message = "Text converted to PDF successfully"
        return FileResponse(path=retrieved_data, media_type='application/pdf', filename=f"{request.output_file_name}.pdf")
        
    except Exception as e:
        return {
            "status": False,
            "message": f"An error occurred: {e}",
            "data": None
        }

@router.post("/convert-text-to-docx")
async def convert_text2docx(
    request: model_type.TextToDocxRequest = Depends()
):
    try:
        # Pass the request to the controller
        retrieved_data = await controller.convert_text2docx(request)
        message = "Text converted to DOCX successfully"
        return FileResponse(path=retrieved_data, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=f"{request.output_file_name}.docx")
        
    except Exception as e:
        return {
            "status": False,
            "message": f"An error occurred: {e}",
            "data": None
        }
        
@router.post("/convert-text-to-ppt")
async def convert_text2ppt(
    lesson_plan: str = Form(..., description="Lesson plan as a JSON-formatted string.")
):
    try:
        # Define the output file path
        output_ppt_path = f"generated_files/lesson_plan.pptx"

        # Step 1: Use the lesson plan data from the request
        text_data = lesson_plan  # Access the input text directly from the request
        text_data_json = json.loads(text_data)  # Convert JSON string to dict

        # Call the generate_presentation function from ppt.py to create the PowerPoint
        await generate_presentation(text_data_json, output_ppt_path)

        # Step 2: Refine the PowerPoint file to adjust content and font size
        await refine_ppt_content(output_ppt_path)

        # Return the generated PowerPoint file as a response
        return FileResponse(
            path=output_ppt_path,
            media_type='application/pptx',
            filename="lesson_plan.pptx"
        )

    except Exception as e:
        return {
            "status": False,
            "message": f"An error occurred: {e}",
            "data": None
        }
