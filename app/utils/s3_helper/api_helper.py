import app.models.model_types as model_type
import app.utils.s3_helper.global_helper as ghelper
import app.utils.s3_helper.aws_helper as aws
import app.utils.pdf.pdf_processing as pdf
import app.utils.word.word_processing as word
import os

async def return_file(request: model_type.CBSE_S3):
    """
    Function to download a file from S3 and return the file after processing.
    """
    try:
        print("A")
        file_key = ghelper.generate_lesson_plan_path(request)
        print("B")
        
        # Download the file from S3 and get the signed URL
        url = await aws.download_files_from_s3(file_key)
        print("C", url['signed_url'])
        
        # Download the file using the signed URL
        file = await ghelper.download_file(url['signed_url'])
        print("D", url)
        print("1.1", file)
        
        # Return the file after processing
        return file
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def extract_text_from_file(file_path: str):
    """
    Extracts text from a given file (PDF or Word).
    """
    try:
        # Determine the file extension to decide the processing method
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == ".pdf":
            # If it's a PDF, use the pdf_processing module to extract text
            combined_text = await pdf.convert_pdf_to_text(file_path)
        elif file_extension in [".docx", ".doc"]:
            # If it's a Word document, use the word_processing module to extract text
            combined_text = await word.convert_word_to_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Clean up the temporary file after text extraction
        os.remove(file_path)
        
        return combined_text
    except Exception as e:
        return {"status": "error", "message": str(e)}



