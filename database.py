import pymongo
import json
import os  

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["CardDetails"]  
collection = db["card"]  


json_directory = r"C:\Users\DEEPIKA\Documents\OpenCVCode\Card\ExtractedData"  # Replace with the path to your directory containing JSON files


for filename in os.listdir(json_directory):
    if filename.endswith('.json'):  
        file_path = os.path.join(json_directory, filename)
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            if isinstance(data, list):  
                collection.insert_many(data)
            else:  # If it's a single JSON object
                collection.insert_one(data)

print("All data inserted successfully!")
