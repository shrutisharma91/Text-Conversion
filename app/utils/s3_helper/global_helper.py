import os
import requests
import shutil
import app.models.model_types as model_type
from urllib.parse import urlparse, unquote

folder_path = "./files"

def rem_file():
    # Remove all files inside the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def generate_lesson_plan_path(payload: model_type.CBSE_S3) -> str:

    # Generate the file path
    file_path = f"class {payload.grade}/{payload.subject.lower()}/{payload.chapter_number}.pdf"

    return file_path

def download_file(url: str, save_folder: str = "files"):
    # Ensure the save folder exists, defaulting to "files"
    print('1')
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    print('2')  
    # Parse the URL to extract the path and filename
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    print('3')
    # Decode any URL-encoded characters (e.g., spaces, special characters)
    filename = unquote(filename)
 
    # Full path to save the file
    save_path = os.path.join(save_folder, filename)

    # Download the file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise error for bad status codes

        # Save the file to the destination folder
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"File downloaded successfully and saved as {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the file: {e}")

    return save_path

