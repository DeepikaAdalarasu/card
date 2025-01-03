import google.generativeai as genai
import json
from PIL import Image
import os
from pymongo import MongoClient

genai.configure(api_key="AIzaSyAfMpQ0ZRlTcZYibA75A8lbQSMLUigFKd0")

model = genai.GenerativeModel("gemini-1.5-flash")

folder_path = r"C:\Users\DEEPIKA\Documents\OpenCVCode\Card\Images"

output_folder = r"C:\Users\DEEPIKA\Documents\OpenCVCode\Card\ExtractedData"

os.makedirs(output_folder, exist_ok=True)

mongo_client = MongoClient("mongodb://localhost:27017/")  
db_name = "Details"  
db = mongo_client[db_name]

collection_name = "CardAll"
collection = db[collection_name]

for image_name in os.listdir(folder_path):
    image_path = os.path.join(folder_path, image_name)
    
    if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        try:
            organ = Image.open(image_path)
            
            base_name = os.path.splitext(image_name)[0]
            
            response = model.generate_content(["Extract company name,name,profession,address,phone number,email id,website,filename,in json format", organ]) 

            print(f"Raw Response for {image_name}:")
            print(response.text)

            cleaned_response = response.text.replace("json", "").replace("```", "").strip()

            print(f"\nCleaned Response for {image_name}:")
            print(cleaned_response)

            try:
                cleaned_json = json.loads(cleaned_response)  
                
                cleaned_json['filename'] = base_name
                
                print("\nCleaned JSON with filename:")
                print(json.dumps(cleaned_json, indent=4))  

                output_file_path = os.path.join(output_folder, f"{base_name}.json")

                with open(output_file_path, "w") as json_file:
                    json.dump(cleaned_json, json_file, indent=4)  

                print(f"\nJSON data for {image_name} has been saved to '{output_file_path}'.")

                insert_result = collection.insert_one(cleaned_json)
                print(f"\nData successfully inserted into MongoDB collection '{collection_name}' with ID: {insert_result.inserted_id}")

            except json.JSONDecodeError:
                print(f"The cleaned response for {image_name} is not a valid JSON format.")
            except Exception as e:
                print(f"An error occurred while processing {image_name}: {e}")

        except Exception as e:
            print(f"An error occurred while opening image {image_name}: {e}")
