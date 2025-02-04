from docx import Document
import json

# Helper function to convert the input request data into a DOCX
async def convert_text2docx(request):
    try:
        # Convert the JSON string to a Python dictionary
        lesson_plan_data = json.loads(request.lesson_plan_data)  # Parse the input JSON string

        # Create a new Document object for DOCX
        doc = Document()

        # Add the lesson plan content to the document
        for lesson in lesson_plan_data:
            # Add lesson topic as a heading
            lesson_topic = lesson.get("Lesson_Topic", "")
            doc.add_heading(f"Lesson Topic: {lesson_topic}", level=1)

            # Add the remaining details of the lesson
            for key, value in lesson.items():
                if key != "Lesson_Topic":  # Skip the Lesson_Topic as it is already added
                    doc.add_heading(key.replace("_", " "), level=2)  # Add the key as a heading
                    if isinstance(value, list):
                        # If the value is a list, create a bullet point list
                        for item in value:
                            doc.add_paragraph(f"- {item}")
                    else:
                        # Otherwise, add it as a paragraph
                        doc.add_paragraph(str(value))

        # Define the output file path
        file_path = f"generated_files/{request.output_file_name}.docx"
        doc.save(file_path)  # Save the DOCX to the specified file path

        return file_path
    
    except Exception as e:
        raise Exception(f"An error occurred while generating the DOCX: {e}")
