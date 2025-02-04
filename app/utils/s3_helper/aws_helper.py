import boto3
from fastapi import UploadFile
from botocore.exceptions import NoCredentialsError ,ClientError
from typing import *
import app.models.model_types as model
import uuid
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_BUCKET_REGION")


async def upload_file_to_s3(payload,file: UploadFile):
    """
    Upload a file to S3 with a specific path structure based on payload inputs.
    :param file: The file to upload.
    :param payload: A dictionary containing `grade`, `subject`, and `chapter_number`.
    :return: The S3 file URL or an error message.
    """
    print("A")
    # Validate the board input (currently only CBSE supported)
    # if payload.board.lower() != "cbse":
    #     return {"error": "Only CBSE board is supported at this time."}
    print("B")
    # Construct the file path based on the payload
    file_path = f"books/{payload.board}/class {payload.grade}/{payload.subject.lower()}/{payload.chapter_number}.pdf"
    print("C")
    # Initialize the S3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )
    print("D")
    try:
        # Reset file pointer and read the file content
        await file.seek(0)
        file_content = await file.read()

        # Upload file to S3
        s3.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=file_path,
            Body=file_content,
            ContentType="application/pdf",  # Assuming the file is a PDF
        )

        # Construct the S3 file URL
        file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_path}"
        print(f"File uploaded successfully to: {file_url}")

        return file_url
        # return {
        #     "message": "File uploaded successfully.",
        #     "file_path": file_path,
        #     "file_url": file_url,
        # }
    except NoCredentialsError:
        print("Error: No AWS credentials available.")
        return {"error": "AWS credentials are not available."}
    except Exception as e:
        print(f"Error uploading file: {e}")
        return {"error": str(e), "message": "Failed to upload the file."}



def download_files_from_s3(file_key: str, expiration: int = 3600):
    """
    Generates a signed URL to download a file from S3.

    :param file_key: The key (path) of the file in the S3 bucket.
    :param expiration: Time in seconds for the signed URL to be valid. Default is 3600 seconds (1 hour).
    :return: A signed URL as a string or an error dictionary.
    """
    print(f"Attempting to generate signed URL for file: {file_key}")
    print(f"AWS Bucket: {AWS_BUCKET_NAME}, Region: {AWS_REGION}")

    try:
        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

        # Generate the presigned URL
        signed_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=expiration
        )

        print(f"Signed URL successfully generated for file: {file_key}")
        return {"signed_url": signed_url}

    except NoCredentialsError:
        error_msg = "AWS credentials are not available."
        print(f"Error: {error_msg}")
        return {"error": error_msg}

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_msg = e.response.get("Error", {}).get("Message", "Unknown error occurred.")
        print(f"ClientError [{error_code}]: {error_msg}")
        return {"error": error_msg}

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}

# async def add_files_to_existing_s3_folder(files: List[UploadFile], vector: model.VectorFilesAdd):
#     folder_name = vector.vector_storeId

#     print(f"Adding files to existing folder: {folder_name} in S3")
    
#     s3 = boto3.client(
#         "s3",
#         aws_access_key_id=AWS_ACCESS_KEY,
#         aws_secret_access_key=AWS_SECRET_KEY,
#         region_name=AWS_REGION
#     )

#     uploaded_files = []

#     for file in files:
#         uuid_string = uuid.uuid4().hex
#         file_name = f"_{uuid_string}_{file.filename}"
#         print(f"Uploading file: {file_name} to folder: {folder_name}")

#         try:
#             await file.seek(0)

#             # Read file content
#             file_content = await file.read()

#             # Define the object key with folder name (ensure the folder exists)
#             object_name = f"{folder_name}/{file_name}"

#             if file_name.endswith('.txt'):
#                 content_type = "text/plain"  
#             else :
#                 content_type = file.content_type

#             # Upload file to the existing folder in S3
#             s3.put_object(
#                 Bucket=AWS_BUCKET_NAME,
#                 Key=object_name,
#                 Body=file_content,
#                 ContentType=content_type
#             )
#             print(f"File uploaded successfully: {file_name}")

#             # Construct the S3 file URL
#             file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
#             uploaded_files.append({
#                 "file_name": file.filename,
#                 "S3file_name" : file_name,
#                 "file_url": file_url,
#                 "object_key": object_name  # Include object key
#             })

#         except NoCredentialsError:
#             print(f"Error: No AWS credentials available for file: {file_name}")
#             return {"error": "Credentials not available"}

#     print(f"File upload to existing folder completed. Uploaded files: {uploaded_files}")
#     return uploaded_files

# def delete_file_from_s3(object_name: str):
#     """
#     Delete a file from an S3 bucket

#     :param object_name: string
#     :return: Dictionary containing success status and message
#     """
#     # Initialize a session using AWS credentials
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=AWS_ACCESS_KEY,
#         aws_secret_access_key=AWS_SECRET_KEY,
#         region_name=AWS_REGION
#     )
    
#     try:
#         # Delete the object from S3
#         s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=object_name)
#         print(f"File deleted successfully from S3: {object_name}")
#         return {"status": "success", "message": f"File '{object_name}' deleted successfully."}
#     except ClientError as e:
#         print(f"Error deleting file from S3: {e}")
#         return {"status": "error", "message": str(e)}
#     except NoCredentialsError:
#         print("Error: No AWS credentials available.")
#         return {"status": "error", "message": "Credentials not available"}
    
