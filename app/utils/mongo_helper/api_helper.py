from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(mongo_connection_string)

# Connect to the database and collection
db = client["Education-Data"] 
collection = db["Book_content"] 


async def store_data_to_mongo(payload,content,s3_path):
    """Function to store data in MongoDB."""
    data = {
        "board": payload.board,
        "grade": payload.grade,
        "subject": payload.subject,
        "chapter_number": payload.chapter_number,
        "chapter_name": payload.chapter_name,
        "s3_path": s3_path,
        "chapter_text": content,
        "is_active": True
    }
    try:
        insert_result = collection.insert_one(data)
        print(f"Data inserted successfully with ID: {insert_result.inserted_id}")
        return "Data Saved to Mongo Succesfully"
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")
        return "An error occured while sabing to Mongo"

async def deactivate_existing_entry(payload):
    """
    Function to update the is_active field to False for an existing entry in MongoDB.
    """
    query = {
        "board": payload.board,
        "grade": payload.grade,
        "subject": payload.subject,
        "chapter_number": payload.chapter_number,
        "is_active": True  # Only target active entries
    }
    update_data = {
        "$set": {
            "is_active": False  # Set is_active to False
        }
    }

    try:
        # Update only one matching document
        update_result = collection.update_one(query, update_data)

        if update_result.matched_count > 0:
            print(f"Document updated successfully. Matched Count: {update_result.matched_count}")
            return "Existing entry deactivated successfully."
        else:
            print("No matching active document found.")
            return "No active entry found to deactivate."

    except Exception as e:
        print(f"An error occurred while updating the is_active field: {e}")
        return "An error occurred while deactivating the existing entry."


async def get_data_from_mongo(payload):
    """
    Function to fetch active entries from MongoDB based on provided filters.
    """
    # Build the query dynamically based on provided filters
    query = {"is_active": True}  # Filter to include only active entries
    if payload.board:
        query["board"] = payload.board
    if payload.grade:
        query["grade"] = payload.grade
    if payload.subject:
        query["subject"] = payload.subject
    if payload.chapter_number:
        query["chapter_number"] = payload.chapter_number
    if payload.chapter_name:
        query["chapter_name"] = payload.chapter_name

    try:
        # Fetch data from MongoDB
        content = list(collection.find(query, {"_id": 0}))  # Exclude the `_id` field from the result
        return content
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return []

async def get_ordered_dropdown_values(payload):
    """
    Function to fetch unique dropdown values based on a specific order:
    board -> grade -> subject -> chapter_number and chapter_name.
    """
    try:
        # Initialize query with is_active filter
        query = {"is_active": True}

        # Determine which field to query based on provided filters
        if not payload.board:
            # No input, return unique boards
            field_to_fetch = "board"
        elif payload.board and not payload.grade:
            # Board provided, return unique grades
            query["board"] = payload.board
            field_to_fetch = "grade"
        elif payload.board and payload.grade and not payload.subject:
            # Board + Grade provided, return unique subjects
            query["board"] = payload.board
            query["grade"] = payload.grade
            field_to_fetch = "subject"
        elif payload.board and payload.grade and payload.subject:
            # Board + Grade + Subject provided, return unique chapter numbers and names
            query["board"] = payload.board
            query["grade"] = payload.grade
            query["subject"] = payload.subject
            field_to_fetch = ["chapter_number", "chapter_name"]

        # Fetch unique values from MongoDB
        if isinstance(field_to_fetch, str):
            # Single field to fetch
            cursor = collection.find(query, {field_to_fetch: 1, "_id": 0})
            unique_values = list({entry.get(field_to_fetch) for entry in cursor if field_to_fetch in entry})
        else:
            # Multiple fields (chapter_number and chapter_name)
            cursor = collection.find(query, {field: 1 for field in field_to_fetch} | {"_id": 0})
            unique_values = [
                [entry.get("chapter_number"), entry.get("chapter_name")]
                for entry in cursor
            ]

        return {
            "status": True,
            "message": "Data retrieved successfully",
            "data": unique_values
        }
    except Exception as e:
        print(f"An error occurred while fetching ordered dropdown values: {e}")
        return {
            "status": False,
            "message": "An error occurred while fetching data",
            "data": []
        }




## NOT BEING USED FOR NOW
async def update_data_in_mongo(payload, content, s3_path):
    """
    Function to update an existing entry in MongoDB or insert if not found.
    """
    query = {
        "board": payload.board,
        "grade": payload.grade,
        "subject": payload.subject,
        "chapter_number": payload.chapter_number,
        "chapter_name": payload.chapter_name
    }
    update_data = {
        "$set": {
            "s3_path": s3_path,
            "chapter_text": content
        }
    }

    try:
        # Update the document if it exists, or insert a new one
        update_result = collection.update_one(query, update_data, upsert=True)

        if update_result.matched_count > 0:
            print(f"Document updated successfully for query: {query}")
            return "Document updated successfully in MongoDB."
        elif update_result.upserted_id:
            print(f"New document inserted with ID: {update_result.upserted_id}")
            return "New document inserted successfully into MongoDB."
        else:
            print("No changes made to the document.")
            return "No changes made to MongoDB document."

    except Exception as e:
        print(f"An error occurred while updating data: {e}")
        return "An error occurred while updating data in MongoDB."

