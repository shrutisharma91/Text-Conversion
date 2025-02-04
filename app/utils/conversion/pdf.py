from fpdf import FPDF
import json

# Create a PDF class
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_left_margin(10)
        self.set_right_margin(10)

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Lesson Plan', ln=True, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

# Helper function to format nested content
def format_content(data, indent=0):
    if isinstance(data, dict):
        formatted = ""
        for key, value in data.items():
            formatted += " " * indent + f"{key.replace('_', ' ')}:\n"
            formatted += format_content(value, indent + 4)  # Indent nested dictionaries
        return formatted
    elif isinstance(data, list):
        formatted = ""
        for item in data:
            formatted += " " * indent + f"- {item}\n"  # Format list items with a leading dash
        return formatted
    else:
        return " " * indent + str(data)  # Return string if it's not a dict or list

import json
import ast

def convert_to_json(q_string):
    """
    Converts a Swagger string input into a valid JSON dictionary.
    Handles cases where single quotes are used instead of double quotes.
    """
    try:
        # Try parsing directly with json.loads()
        return json.loads(q_string)
    except json.JSONDecodeError:
        print("⚠️ JSONDecodeError: Trying to clean the input...")
        
        # Clean up the string: Replace single quotes with double quotes
        cleaned_str = q_string.strip().replace("'", '"')
        
        try:
            # Try again using json.loads()
            return json.loads(cleaned_str)
        except json.JSONDecodeError:
            print("⚠️ Still failing. Trying ast.literal_eval...")
            try:
                # Use ast.literal_eval() as a last resort
                return ast.literal_eval(q_string.strip())
            except (SyntaxError, ValueError) as e:
                print("❌ Failed to parse JSON string:", e)
                return None  # Return None if all methods fail

# Helper function to convert the input request data into a PDF
async def convert_text_to_pdf(request):
    try:
        # Convert the JSON string to a Python dictionary
        #lesson_plan_data = json.loads(request.lesson_plan_data)
        lesson_plan_data =convert_to_json(request.lesson_plan_data) 
        print(type(lesson_plan_data))
        print(lesson_plan_data)

        # Initialize the PDF object
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Generate the PDF content
        for lesson in lesson_plan_data:
            # Add lesson topic as a chapter
            lesson_topic = lesson.get("Lesson_Topic", "")
            pdf.chapter_title(f"Lesson Topic: {lesson_topic}")

            # Add the remaining details of the lesson
            for key, value in lesson.items():
                if key != "Lesson_Topic":  # Skip the Lesson_Topic as it is already added
                    pdf.chapter_title(key.replace("_", " "))  # Add the key as a title
                    formatted_content = format_content(value)  # Add the value as the body
                    pdf.chapter_body(formatted_content)  # Add formatted body text

        # Save the PDF
        file_path = f"generated_files/{request.output_file_name}.pdf"
        pdf.output(file_path)

        return file_path
    
    except Exception as e:
        raise Exception(f"An error occurred while generating the PDF: {e}")
