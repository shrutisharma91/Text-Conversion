from fpdf import FPDF
import json

def skip_unsupported_characters(text: str) -> str:
    """
    Removes (skips) all characters outside Windows-1252 (0–255).
    """
    return "".join(ch for ch in text if ord(ch) <= 255)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_left_margin(10)
        self.set_right_margin(10)

    def header(self):
        # Use built-in font that only supports 0–255 range
        self.set_font('Arial', 'B', 16)
        header_text = "Lesson Plan"
        # Skip unsupported chars if any (unlikely here)
        header_text = skip_unsupported_characters(header_text)
        self.cell(0, 10, header_text, ln=True, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        # Skip unsupported characters
        title = skip_unsupported_characters(title)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        # Skip unsupported characters
        body = skip_unsupported_characters(body)
        self.multi_cell(0, 10, body)
        self.ln()

def format_content(data, indent=0):
    """
    Recursively formats dict/list/string into a readable text block,
    skipping characters outside 0–255.
    """
    if isinstance(data, dict):
        formatted = ""
        for key, value in data.items():
            # Replace underscores, skip unsupported chars
            key_text = key.replace("_", " ")
            key_text = skip_unsupported_characters(key_text)
            
            formatted += " " * indent + f"{key_text}:\n"
            formatted += format_content(value, indent + 4)
        return formatted

    elif isinstance(data, list):
        formatted = ""
        for item in data:
            # Convert item to string and skip unsupported chars
            item_str = skip_unsupported_characters(str(item))
            formatted += " " * indent + f"- {item_str}\n"
        return formatted

    else:
        data_str = skip_unsupported_characters(str(data))
        return " " * indent + data_str + "\n"

async def convert_text_to_pdf(lesson_plan_json, output_file_name):
    try:
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        lessons = lesson_plan_json.get("lesson_plan", [])

        for lesson in lessons:
            # Lesson Topic
            lesson_topic = lesson.get("Lesson_Topic", "")
            if lesson_topic:
                pdf.chapter_title(f"Lesson Topic: {lesson_topic}")

            # Other Keys
            for key, value in lesson.items():
                if key == "Lesson_Topic":
                    continue
                sanitized_key = skip_unsupported_characters(key.replace("_", " "))
                pdf.chapter_title(sanitized_key)

                # Format and skip unsupported chars in the value
                formatted_content = format_content(value)
                pdf.chapter_body(formatted_content)

        file_path = f"generated_files/{output_file_name}.pdf"
        pdf.output(file_path)

        return file_path
    
    except Exception as e:
        raise Exception(f"An error occurred while generating the PDF: {e}")
