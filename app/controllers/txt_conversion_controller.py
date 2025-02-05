import app.utils.conversion.pdf as pdf  # Import your PDF utility
import app.models.model_types as model_type
import app.utils.conversion.word as word
import app.utils.conversion.ppt as ppt
import os

async def convert_text2pdf(lesson_plan_json,output_file_name):
    """
    Converts the given text into a PDF and saves it to the specified file name.
    """
    try:
        # Pass the 'request' directly to the utility function
        file_path = await pdf.convert_text_to_pdf(lesson_plan_json,output_file_name)  # Pass the entire request object

        # Return the path to the generated PDF
        return file_path
    
    except Exception as e:
        raise Exception(f"Failed to generate the PDF: {e}")



async def convert_text2docx(lesson_plan_json,output_file_name):
    """
    Converts the given text into a DOCX and saves it to the specified file name.
    """
    try:
        # Pass the 'request' directly to the utility function
        file_path = await word.convert_text2docx(lesson_plan_json,output_file_name)  # Pass the entire request object

        # Return the path to the generated DOCX
        return file_path
    
    except Exception as e:
        raise Exception(f"Failed to generate the DOCX: {e}")
    

async def convert_text2ppt(request: model_type.TextTopptRequest):
    """
    Converts the given text into a PowerPoint (.pptx) file.
    """
    # Define the output file path
    output_ppt_path = f"generated_files/{request.output_file_name}.pptx"

    try:
        # Step 1: Use the lesson plan data from the request
        lesson_plan_data = request.lesson_plan_data  # Access the input data directly from the request

        # Call the generate_presentation function from ppt.py to create the PowerPoint
        await ppt.generate_presentation(lesson_plan_data, output_ppt_path)

        # Step 2: Refine the PowerPoint file to adjust content and font size
        await ppt.refine_ppt_content(output_ppt_path)

        # Return the path to the generated PowerPoint
        return output_ppt_path

    except Exception as e:
        # Log the error for debugging
        raise Exception(f"Failed to generate the PowerPoint: {e}")
